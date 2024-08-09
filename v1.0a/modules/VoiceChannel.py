import json
import asyncio
import google.generativeai as genai
import speech_recognition as sr
from modules.ManagedMessages import ManagedMessages
from discord import Message
from google.generativeai.types import HarmCategory, HarmBlockThreshold

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class VoiceChannel:

    async def stt(speech) -> str:
        """Accepts arg speech, returns type string"""

    async def voice_content():
        """"""