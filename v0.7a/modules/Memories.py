import json
import google.generativeai as genai
import mysql.connector
from discord import Message
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from modules.ContextWindow import ContextWindow

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

context_window = ContextWindow.context_window

genai.configure(api_key=config["GEMINI"]["API_KEY"])
model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"])

db_config = {
    'user': config["SQL_CREDENTIALS"]["username"],
    'password': config["SQL_CREDENTIALS"]["password"],
    'host': config["SQL_CREDENTIALS"]["host"],
    'database': config["SQL_CREDENTIALS"]["database"],
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()
max_context_window = config["MAX_CONTEXT_WINDOW"] # TODO: need to patch unlimited context window

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
    
    def summarize_context_window(self, channel_id, retry=3):
        prompt = f"You're an AI LLM, who's only purpose is to summarize large but concise summaries on text provided to you, try to retain most of the information! Your first task is to summarize this conversation from the perspective of {self.character_name} --- Conversation Start ---\n{'\n'.join(context_window[channel_id])} --- Conversation End ---"
        
        try:
            response = model.generate_content(prompt).text
            return response
        except Exception as E:
            print(f"Error generating response: {E}")
            retry_count = 0
            while retry_count < retry:  # Adjust the retry count as needed
                try:
                    response = model.generate_content(prompt).text
                    return response
                except Exception as E:
                    print(f"Error generating response (retry {retry_count}): {E}")
                    retry_count += 1
            else:
                return ""
            
    def save_to_memory(self, message : Message, force=False):
        channel_id = message.channel.id
        if force:
            sql = "INSERT INTO memories (channel_id, special_phrase, memory) VALUES (%s, %s, %s)" # change this on DB
            summary_of_context_window = self.summarize_context_window(channel_id)
            special_phrase = self.is_worth_remembering(context='\n'.join(context_window[channel_id]))["special_phrase"]
            values = (channel_id, special_phrase, summary_of_context_window)
            cursor.execute(sql, values)
            conn.commit()
            print(f"Saved message: {message.content}\nTo memory: {summary_of_context_window}\nFor: {channel_id}")
        if len(context_window[channel_id]) == max_context_window:
            is_worth = self.is_worth_remembering(context='\n'.join(context_window[channel_id]))
            if is_worth['is_worth']:
                sql = "INSERT INTO memories (channel_id, special_phrase, memory) VALUES (%s, %s, %s)"
                summary_of_context_window = self.summarize_context_window(channel_id)
                special_phrase = self.is_worth_remembering(context='\n'.join(context_window[channel_id]))["special_phrase"]
                values = (channel_id, special_phrase, summary_of_context_window)
                cursor.execute(sql, values)
                conn.commit()
                print(f"Saved message: {message.content}\nTo memory: {summary_of_context_window}\nFor: {channel_id}")
    
    def fetch_and_sort_entries(self, channel_id):
        sql = """
        SELECT special_phrase, memory
        FROM memories
        WHERE channel_id = %s
        ORDER BY timestamp
        """
        cursor.execute(sql, (channel_id,))
        rows = cursor.fetchall()
        
        # Initializing an empty dictionary to store the results
        result = {}
    
        # Iterating over the rows and populating the dictionary
        for row_num, row in enumerate(rows):
            print(row_num)
            special_phrase, memory = row
            result[special_phrase] = memory
    
        return result
    
    def is_worth_remembering(self, context):
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
            clean_json = json.loads(self.clean_json(unloaded_json))
            print(clean_json)
            return clean_json
        except Exception as E:
            print(E)
        
    def compare_memories(self, channel_id, message):
        
        json_format = """{"is_similar" : true/false, "similar_phrase" : the phrase in [Message 2]}"""
        entries = self.fetch_and_sort_entries(channel_id).keys()
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
       e. be lenient in your comparision, if a phrase has 2/3 keywords return complete the rest.
    4. If the phrase is simmilar, provide it in the JSON-type response ONLY provide the MOST similar phrase.
    
    5. Provide your response in this JSON schema {json_format} without ANY formatting ie.. no backticks '`' no syntax highlighting, no numbered lists.

"""     
        comparing_model = genai.GenerativeModel(config["AI_MODEL"], system_instruction=system_instruction)
        message_list = f"""
Message: {message}
List of phrases: {", ".join(entries)}
"""
        try:
            unloaded_json = comparing_model.generate_content(message_list).text
            clean_json = json.loads(self.clean_json(unloaded_json))
            return clean_json
        except Exception as E:
            print(E)
            return {"is_similar" : False, "special_phrase" : None}
        
    def clean_json(self, json : str):
        if json.startswith("```json") and json.endswith("```"):
            return json[7:-3]
        else:
            return json