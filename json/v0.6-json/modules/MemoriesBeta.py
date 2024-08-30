import json
import google.generativeai as genai
from discord import Message
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from modules.ContextWindow import ContextWindow

with open("./config.json", "r") as config_file:
    config = json.load(config_file)

context_window = ContextWindow.context_window

genai.configure(api_key=config["GEMINI"]["API_KEY"])
model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"])

max_context_window = config["GEMINI"]["MAX_CONTEXT_WINDOW"]  # Read the max context window size

class Memories:
    def __init__(self):
        self.details = self.load_character_details()
        self.character_name = self.details["name"]
        self.role = self.details["role"]
        self.age = self.details["age"]
        self.description = self.details["description"]
        self.memory_file = "memories.json"

    @staticmethod
    def load_character_details():
        try:
            with open("prompt.json", "r") as unloaded_prompt_json:
                prompt_json = json.load(unloaded_prompt_json)
        except FileNotFoundError:
            raise FileNotFoundError("The prompt.json file was not found.")
        except json.JSONDecodeError:
            raise ValueError("The prompt.json file is not a valid JSON.")

        return {
            "name": prompt_json.get('name', 'unknown_bot'),
            "role": prompt_json.get('role', 'unknown_role'),
            "age": prompt_json.get('age', 'unknown_age'),
            "description": prompt_json.get('description', 'no description provided')
        }
    
    @staticmethod
    def clean_json(nasty_json : str):
        """
        Description:
        This function cleans the potentially dirty json by removing the markdown
        
        Arguments:
        nasty_json : str
        
        Returns:
        nasty_json : dict
        """
        if nasty_json.startswith(("```json", )) and nasty_json.endswith("```"):
            return json.loads(nasty_json[7:-3])
        else:
            return json.loads(nasty_json) # Assumed to be clean.. lol

    def save_to_memory(self, message: Message, force=False):
        print("Called function Memories.save_to_memory() [Line 61 from modules/MemoriesBeta.py]")
        user_id = f"{message.guild.id}-{message.author.id}"

        if force or len(context_window[user_id]) == max_context_window:
            summary_of_context_window = self.summarize_context_window(user_id)
            special_phrase = self.is_worth_remembering(context='\n'.join(context_window[user_id]))["special_phrase"]
            
            self._write_memory(user_id, special_phrase, summary_of_context_window)
            print(f"Saved message: {message.content}\nTo memory: {summary_of_context_window}\nFor: {user_id}")

    def summarize_context_window(self, user_id, retry=3):
        print("Called function Memories.summarize_context_window() [Line 69 (nice) from modules/MemoriesBeta.py]")
        prompt = f"You're a data analyst whose only purpose is to summarize large but concise summaries of text provided to you. Try to retain most of the information! Your first task is to summarize this conversation from the perspective of {self.character_name} --- Conversation Start ---\n{'\n'.join(context_window[user_id])} --- Conversation End ---"
        
        try:
            response = model.generate_content(prompt).text
            return response
        
        except Exception as E:
            print(f"Error generating response: {E}")
            retry_count = 0
            
            while retry_count < retry:
            
                try:
                    response = model.generate_content(prompt).text
                    return response
            
                except Exception as E:
                    print(f"Error generating response (retry {retry_count}): {E}")
                    retry_count += 1
            
            else:
                return ""

    def _write_memory(self, user_id, special_phrase, summary):
        try:
            with open(self.memory_file, "r") as memory_file:
                memories = json.load(memory_file)
        except FileNotFoundError:
            memories = {}
        except json.JSONDecodeError:
            memories = {}

        if user_id not in memories:
            memories[user_id] = []

        memories[user_id].append({
            "special_phrase": special_phrase,
            "memory": summary
        })

        with open(self.memory_file, "w") as memory_file:
            json.dump(memories, memory_file, indent=4)

    def fetch_and_sort_entries(self, user_id):
        try:
            with open(self.memory_file, "r") as memory_file:
                memories = json.load(memory_file)
        except FileNotFoundError:
            memories = {}
        except json.JSONDecodeError:
            memories = {}

        return {entry["special_phrase"]: entry["memory"] for entry in memories.get(user_id, [])}

    def is_worth_remembering(self, context):
        print("Called function Memories.is_worth_remembering() [Line 124 from modules/MemoriesBeta.py]")
        prompt = """
Objective:
Determine whether a conversation is worth remembering based on predefined criteria and if it is, provide ONE word from the entire conversation that you'd remember.

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
        full_prompt = prompt + "\n" + context
        try:
            unloaded_json = model.generate_content(full_prompt).text
            print(unloaded_json)
            json_parsed = json.loads(unloaded_json)
            return json_parsed
        except Exception as E:
            print(E)
            return {"is_worth": False, "special_phrase": None}

    def compare_memories(self, user_id, message):
        print("Called function Memories.compare_memories() [Line 157 from modules/MemoriesBeta.py]")
        json_format = """{"is_similar" : true/false, "similar_phrase" : the phrase in [Message 2]}"""
        entries = self.fetch_and_sort_entries(user_id).keys()
        system_instruction = f"""
Objective:
    Determine if the provided phrase or message is similar to another given phrase or message based on predefined criteria.

    Guidelines:
    1. **Content Overlap**: Examine if the majority of content in both messages overlap.
    2. **Contextual Similarity**: Check if the context or the main idea presented in both messages is alike.
    3. **Linguistic Patterns**: Identify if similar linguistic patterns, phrases, or keywords are used.
    4. **Semantic Similarity**: Evaluate if both messages convey the same meaning even if different words are used.

    Instructions:
    1. Read the provided message and phrases.
    2. Assess each message based on the provided guidelines.
    3. Determine if the messages meet one or more of the criteria:
       a. The content of both messages overlaps significantly.
       b. The contexts or main ideas of both messages align.
       c. Similar linguistic patterns or keywords are used in both messages.
       d. The overall meaning conveyed by both messages is the same.
       e. be lenient in your comparison, if a phrase has 2/3 keywords return complete the rest.
    4. If the phrase is similar, provide it in the JSON-type response ONLY provide the MOST similar phrase.
    
    5. Provide your response in this JSON schema {json_format} without ANY formatting ie.. no backticks '`' no syntax highlighting, no numbered lists.

        """
        comparing_model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"], system_instruction=system_instruction)
        message_list = f"""
Message: {message}
List of phrases: {", ".join(entries)}
"""
        try:
            unloaded_json = comparing_model.generate_content(message_list).text
            json_parsed = self.clean_json(unloaded_json)
            return json_parsed
        except Exception as E:
            print(E)
            return {"is_similar": False, "similar_phrase": None}
