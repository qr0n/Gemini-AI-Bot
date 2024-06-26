import json
import datetime
import os
import asyncio
import google.generativeai as genai
from discord.ext import commands
from discord import Message, Reaction, AllowedMentions
from modules.Memories import Memories
from modules.ContextWindow import ContextWindow
from modules.BotModel import read_prompt, BotModel

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class Gemini:

    def __init__(self):
        # UNIFY ALL COG ABSTRACT AS MUCH AS POSSIBLE
        pass