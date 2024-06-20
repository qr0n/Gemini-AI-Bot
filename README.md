# This is a project I made for **FUN**

## This **IS** a rip off of [this service](https://discord.gg/shapes)

### Gemini-AI-Bot
#### This is a discord bot that uses [google's gemini api](https://ai.google.dev/) to generate messages for a conversation, so far this project is not complete.

##### How to setup
```bash
pip install -r requirements.txt
```
##### Make sure to edit the `config.json`
```json
{
    "SQL_CREDENTIALS" : {
        "username" : "",
        "password" : "",
        "host" : "",
        "database" : ""
    },
    "GEMINI" : {
        "API_KEY" : "",
        "AI_MODEL" : "models/gemini-1.5-flash-latest",
        "MAX_CONTEXT_WINDOW" : 20
    },
    "FREEWILL": {
        "enabled" : true,
        "text_frequency" : 1,
        "reaction_frequency" : 1
    },
    "API_KEY" : "",
    "AI_MODEL" : "models/gemini-1.5-flash-latest",
    "MAX_CONTEXT_WINDOW" : 20,
    "BOT_TOKEN" : ""}
``` 
###### Also, if there is need of a database helper, run `sqlhelper.py`, just remember to put your SQL credentials in.