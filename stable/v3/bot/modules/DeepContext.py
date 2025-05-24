"""
Deep Context module for handling context-aware interactions and classifications
"""

from modules.CommonCalls import CommonCalls
from google import genai

from google.genai.types import (
    SafetySetting,
    GenerateContentConfig,
    GenerateContentResponse,
)

client = genai.Client(api_key=CommonCalls.config()["gemini_api_key"])


class DeepContext:
    """Parent class hosting both DeepContext Logic and DeepContext Hook"""

    class Logic:
        VALID_CATEGORIES = {
            "voice-call-initialize",
            "voice-call-end",
            "normal-chat-normal",
            "interesting-chat-good",
            "interesting-chat-bad",
            "none-none",
        }

        @staticmethod
        def is_in_vc(server_id) -> bool:
            """Check if bot is in voice channel"""
            pass

        @staticmethod
        async def classify(
            text: str, author_name: str, server_id: int = None, channel_id: int = None
        ):
            """
            Classify text input from discord using Google Gemini API.

            Args:
                text (str): The message text to classify
                author_name (str): Name of the message author
                server_id (int, optional): Discord server ID
                channel_id (int, optional): Discord channel ID

            Returns:
                dict: Classification results including category and hidden meaning
            """
            character_details = CommonCalls.load_character_details()

            system_instruction = f"""
            You are an AI Agent named "{character_details['name']}"
            However you will avoid referring to yourself as an AI or LLM.
            The person who's data you're classifying is named {author_name}
            ONLY initialize events when the user is mentioning YOUR name.

            Classify the text into one of these categories:
            - normal-chat-normal: Regular conversation with nothing notable
            - interesting-chat-good: Discussion aligns with likes: {character_details["likes"]}
            - interesting-chat-bad: Discussion aligns with dislikes: {character_details["dislikes"]}
            - voice-call-initialize: User wants to start voice call
            - voice-call-end: User wants to end voice call

            Also identify any hidden meanings or implied actions in the text.

            Return as JSON: {"category": "category-name", "hidden-meaning": "identified meanings"}
            """

            response: GenerateContentResponse = (
                await client.aio.models.generate_content(
                    contents=text,
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

            return CommonCalls.clean_json(response.text)

        @staticmethod
        def modifier(input_json: dict) -> dict:
            """
            Modify classification results by adding flags for certain categories.

            Args:
                input_json (dict): The classification results to modify

            Returns:
                dict: Modified classification results
            """
            if input_json["category"] == "voice-call-initialize":
                input_json["kill"] = True
            return input_json
