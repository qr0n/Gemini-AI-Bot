import json
import os

from google import genai
from google.genai.types import (
    GenerateContentConfig,
    SafetySetting,
    GenerateContentResponse,
)
from discord import Message
from modules.ManagedMessages import ManagedMessages
from modules.CommonCalls import CommonCalls

context_window = ManagedMessages.context_window

client = genai.Client(api_key=CommonCalls.config()["gemini_api_key"])


# JSON storage paths
MEMORIES_FILE = f"data/{CommonCalls.config()['alias']}-memories.json"


class Memories:
    def __init__(self):
        self.details = CommonCalls.load_character_details()
        self.character_name = self.details["name"]
        self.role = self.details["role"]
        self.age = self.details["age"]
        self.description = self.details["description"]

    async def summarize_context_window(self, channel_id, retry=3):
        prompt = f"You're a data analyst who's only purpose is to summarize large but concise summaries on text provided to you, try to retain most of the information! Your first task is to summarize this conversation from the perspective of {self.character_name} --- Conversation Start ---\n{'\n'.join(context_window[channel_id])} --- Conversation End ---"

        response: GenerateContentResponse = await client.aio.models.generate_content(
            prompt,
            model=CommonCalls.config()["aiModel"],
            config=GenerateContentConfig(
                safety_settings=[
                    SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold=CommonCalls.config()["filterHateSpeech"],
                    ),
                    SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold=CommonCalls.config()["filterHarassment"],
                    ),
                    SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold=CommonCalls.config()["filterSexuallyExplicit"],
                    ),
                    SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold=CommonCalls.config()["filterDangerous"],
                    ),
                ],
            ),
        )

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
        print(
            "Save to memory function call `Memories.save_to_memory` (Message from line 98 @ modules/Memories.py)"
        )
        channel_id = message.channel.id
        key = str(channel_id)  # Ensure key consistency

        # Load the current memories from the JSON file
        memories = self.load_memories()

        if force or len(context_window[channel_id]) == int(
            CommonCalls.config()["maxContext"]
        ):
            summary_of_context_window = await self.summarize_context_window(channel_id)
            special_phrase = (
                await self.is_worth_remembering(
                    context="\n".join(context_window[channel_id])
                )
            )["special_phrase"]
            memory_entry = {
                "special_phrase": special_phrase,
                "memory": summary_of_context_window,
                "timestamp": message.created_at.isoformat(),
            }

            # Append to the existing memories
            memories[key] = memories.get(key, []) + [memory_entry]

            # Save the updated memories back to the JSON file
            self.save_memories(memories)

            print(
                f"Saved message: {message.content}\nTo memory: {summary_of_context_window}\nFor: {channel_id}"
            )

    def fetch_and_sort_entries(self, channel_id):
        # Load the current memories from the JSON file
        memories = self.load_memories()
        key = str(channel_id)  # Ensure key consistency

        # Get the memories for the specific channel, sorted by timestamp
        sorted_memories = sorted(memories.get(key, []), key=lambda x: x["timestamp"])

        # Create a dictionary with special_phrase as the key and memory as the value
        result = {entry["special_phrase"]: entry["memory"] for entry in sorted_memories}
        return result

    async def is_worth_remembering(self, context):
        print(
            "Worth Remembering function call `Memories.is_worth_remembering` (Message from line 131 @ modules/Memories.py)"
        )
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

        try:
            unloaded_json: GenerateContentResponse = (
                await client.aio.models.generate_content(
                    context,
                    model=CommonCalls.config()["aiModel"],
                    config=GenerateContentConfig(
                        safety_settings=[
                            SafetySetting(
                                category="HARM_CATEGORY_HATE_SPEECH",
                                threshold=CommonCalls.config()["filterHateSpeech"],
                            ),
                            SafetySetting(
                                category="HARM_CATEGORY_HARASSMENT",
                                threshold=CommonCalls.config()["filterHarassment"],
                            ),
                            SafetySetting(
                                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                threshold=CommonCalls.config()[
                                    "filterSexuallyExplicit"
                                ],
                            ),
                            SafetySetting(
                                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                                threshold=CommonCalls.config()["filterDangerous"],
                            ),
                        ],
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                    ),
                )
            )
            clean_json = json.loads(self.clean_json(unloaded_json.text))
            return clean_json
        except Exception as E:
            print(E)

    async def compare_memories(self, channel_id, message):
        print(
            "Compare Memories function call `Memories.compare_memories` (Message from line 202 @ modules/Memories.py)"
        )
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
        message_list = f"""
Context: {"\n".join(context_window[channel_id])}
List of phrases: {", ".join(entries)}
"""
        try:
            unloaded_json = await client.aio.models.generate_content(
                contents=message_list,
                model=CommonCalls.config()["aiModel"],
                config=GenerateContentConfig(
                    safety_settings=[
                        SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold=CommonCalls.config()["filterHateSpeech"],
                        ),
                        SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold=CommonCalls.config()["filterHarassment"],
                        ),
                        SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold=CommonCalls.config()["filterSexuallyExplicit"],
                        ),
                        SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold=CommonCalls.config()["filterDangerous"],
                        ),
                    ],
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                ),
            )
            clean_json = json.loads(self.clean_json(unloaded_json.text))

            return clean_json
        except Exception as E:
            print(E)
            return {"is_similar": False, "similar_phrase": None}

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
            return {
                key: Memories.convert_to_serializable(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [Memories.convert_to_serializable(item) for item in data]
        else:
            return data

    def save_memories(self, memories):
        serializable_memories = self.convert_to_serializable(memories)
        with open(MEMORIES_FILE, "w") as file:
            json.dump(serializable_memories, file, indent=4)
