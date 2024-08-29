import json
import google.generativeai as genai
from discord import Message
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from modules.ManagedMessages import ManagedMessages
from google.protobuf.json_format import MessageToDict
import os

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

context_window = ManagedMessages.context_window

genai.configure(api_key=config["GEMINI"]["API_KEY"])
model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"])

max_context_window = config["GEMINI"]["MAX_CONTEXT_WINDOW"] # TODO: need to patch unlimited context window

# JSON storage paths
MEMORIES_FILE = "./memories.json"

class Memories:
    def __init__(self):
        self.details = self.load_character_details()
        self.character_name = self.details["name"]
        self.role = self.details["role"]
        self.age = self.details["age"]
        self.description = self.details["description"]

    @staticmethod
    def load_character_details():
        try:
            with open("prompt.json", "r") as unloaded_prompt_json:
                prompt_json = json.load(unloaded_prompt_json)
        except FileNotFoundError:
            raise FileNotFoundError("The prompt.json file was not found.")
        except json.JSONDecodeError:
            raise ValueError("The prompt.json file is not a valid JSON.")

        personality_traits = prompt_json.get('personality_traits', {})
        name = personality_traits.get('name', 'unknown_bot')
        role = personality_traits.get('role', 'unknown_role')
        age = personality_traits.get('age', 'unknown_age')
        description = personality_traits.get('description', 'no description provided')
    
        return {
            "name": name,
            "role": role,
            "age": age,
            "description": description
        }
    
    async def summarize_context_window(self, channel_id, retry=3):
        prompt = f"You're a data analyst who's only purpose is to summarize large but concise summaries on text provided to you, try to retain most of the information! Your first task is to summarize this conversation from the perspective of {self.character_name} --- Conversation Start ---\n{'\n'.join(context_window[channel_id])} --- Conversation End ---"
        
        response = await model.generate_content_async(prompt, safety_settings={
                                                        HarmCategory.HARM_CATEGORY_HARASSMENT : config["GEMINI"]["FILTERS"]["sexually_explicit"],
                                                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : config["GEMINI"]["FILTERS"]["harassment"],
                                                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : config["GEMINI"]["FILTERS"]["dangerous_content"],
                                                        HarmCategory.HARM_CATEGORY_HATE_SPEECH : config["GEMINI"]["FILTERS"]["hate_speech"]})
        
        try:
            return response.text
        except Exception as E:
            print(f"Error generating response: {E}")
            retry_count = 0
            while retry_count < retry:  # Adjust the retry count as needed
                try:
                    fall_back_response = response.candidates[0].content.parts
                    return fall_back_response
                except Exception as E:
                    print(f"Error generating response (retry {retry_count}): {E}")
                    retry_count += 1
            else:
                return ""
    
    async def save_to_memory(self, message: Message, force=False):
        channel_id = message.channel.id

        # Load the current memories from the JSON file
        memories = self.load_memories()

        if force or len(context_window[channel_id]) == max_context_window:
            summary_of_context_window = await self.summarize_context_window(channel_id)
            special_phrase = (await self.is_worth_remembering(context='\n'.join(context_window[channel_id])))["special_phrase"]
            memory_entry = {
                "special_phrase": special_phrase,
                "memory": summary_of_context_window,
                "timestamp": message.created_at.isoformat()
            }

            # Append to the existing memories
            memories[channel_id] = memories.get(channel_id, []) + [memory_entry]

            # Save the updated memories back to the JSON file
            self.save_memories(memories)

            print(f"Saved message: {message.content}\nTo memory: {summary_of_context_window}\nFor: {channel_id}")
    
    def fetch_and_sort_entries(self, channel_id):
        # Load the current memories from the JSON file
        memories = self.load_memories()

        # Get the memories for the specific channel, sorted by timestamp
        sorted_memories = sorted(memories.get(channel_id, []), key=lambda x: x["timestamp"])
        
        # Create a dictionary with special_phrase as the key and memory as the value
        result = {entry["special_phrase"]: entry["memory"] for entry in sorted_memories}
        return result
    
    async def is_worth_remembering(self, context):
        system_instruction = """
Objective:
Determine whether a conversation is worth remembering based on predefined criteria and if it is, provide a highly detailed phrase summarizing the entire conversation that you'd remember.

Guidelines:
1. **Relevance**: The conversation should be directly relevant to ongoing or important topics.
2. **Novelty**: The conversation should provide new insights or information not previously encountered.
3. **Actionability**: The conversation should lead to actionable steps or decisions.
4. **Emotional Significance**: The conversation should have an emotional impact or involve significant personal interaction.

Instructions:
1. Read the entire conversation.
2. Assess each message based on the provided guidelines.
3. Determine if the overall conversation meets one or more of the following criteria:
    a. Provides new, useful information relevant to current tasks or goals.
    b. Leads to specific actions or decisions that can be implemented.
    c. Contains emotionally significant interactions worth preserving.
4. If the conversation is relevant, provide a phrase that when said, you'd remember the summary of this conversation.

Provide your response in a JSON format {"is_worth" : true/false, "special_phrase" : phrase_goes_here} without ANY formatting, ie.. no backticks '`' no syntax highlighting, no numbered lists.'
    """
        remember_model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"], system_instruction=system_instruction)
        try:
            unloaded_json = await remember_model.generate_content_async(context, generation_config={"response_mime_type": "application/json"}, safety_settings={
                                                        HarmCategory.HARM_CATEGORY_HARASSMENT : config["GEMINI"]["FILTERS"]["sexually_explicit"],
                                                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : config["GEMINI"]["FILTERS"]["harassment"],
                                                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : config["GEMINI"]["FILTERS"]["dangerous_content"],
                                                        HarmCategory.HARM_CATEGORY_HATE_SPEECH : config["GEMINI"]["FILTERS"]["hate_speech"]})
            clean_json = json.loads(self.clean_json(unloaded_json.text))
            print("") # TODO Add log here
            return clean_json
        except Exception as E:
            print(E)
        
    async def compare_memories(self, channel_id, message):
        entries = self.fetch_and_sort_entries(channel_id).keys()
        
        system_instruction = """
Objective:
Determine if the provided context or phrase is similar to another given phrase or message based on predefined criteria.

Guidelines:
1. **Content Overlap**: Examine if the majority of content in both messages overlaps.
2. **Contextual Similarity**: Check if the context or the main idea presented in both messages is alike.
3. **Linguistic Patterns**: Identify if similar linguistic patterns, phrases, or keywords are used.
4. **Semantic Similarity**: Evaluate if both messages convey the same meaning even if different words are used.

Instructions:
1. Read the provided message and phrases.
2. Assess each message based on the provided guidelines.
3. Determine if the messages meet one or more of the following criteria:
    a.The content of both messages overlaps significantly.
    b. The contexts or main ideas of both messages align.
    c. Similar linguistic patterns or keywords are used in both messages.
    d. The overall meaning conveyed by both messages is the same.
    e. Be lenient in your comparison; if a phrase has 2/3 keywords, complete the rest.

If the phrase is similar, provide it in the JSON-type response ONLY. Provide the MOST similar phrase.
Provide your response in this JSON schema:

{
    "is_similar" : true/false,
    "similar_phrase" : the phrase in [Message 2]
}

without ANY formatting, i.e., no backticks '`', no syntax highlighting, no numbered lists.
"""     
        comparing_model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"], system_instruction=system_instruction)
        message_list = f"""
Context: {"\n".join(context_window[channel_id])}
List of phrases: {", ".join(entries)}
"""
        print("Compare Memories function call `Memories.compare_memories` (Message from line 202 @ modules/Memories.py)")
        try:
            unloaded_json = await comparing_model.generate_content_async(message_list, generation_config={"response_mime_type": "application/json"}, safety_settings={
                                                        HarmCategory.HARM_CATEGORY_HARASSMENT : config["GEMINI"]["FILTERS"]["sexually_explicit"],
                                                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : config["GEMINI"]["FILTERS"]["harassment"],
                                                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : config["GEMINI"]["FILTERS"]["dangerous_content"],
                                                        HarmCategory.HARM_CATEGORY_HATE_SPEECH : config["GEMINI"]["FILTERS"]["hate_speech"]})
            clean_json = json.loads(self.clean_json(unloaded_json.text))
            return clean_json
        except Exception as E:
            print(E)
            return {"is_similar" : False, "special_phrase" : None}
        
    def clean_json(self, json: str):
        if json.startswith("```json") and json.endswith("```"):
            return json[7:-3]
        else:
            return json

    @staticmethod
    def load_memories():
        """Load the memories from the JSON file."""
        if not os.path.exists(MEMORIES_FILE):
            return {}
        with open(MEMORIES_FILE, "r") as file:
            return json.load(file)

    @staticmethod
    def convert_to_serializable(data):
        # Check if data is of RepeatedComposite type and convert it
        if isinstance(data, dict):
            return {key: Memories.convert_to_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [Memories.convert_to_serializable(item) for item in data]
        else:
            return data

    def save_memories(self, memories):
        serializable_memories = self.convert_to_serializable(memories)
        with open(MEMORIES_FILE, "w") as file:
            json.dump(serializable_memories, file, indent=4)