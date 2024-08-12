# ⚠️ THIS IS A WARNING ⚠️ 
## THIS PROJECT WILL BE AGAINST THE DISCORD'S DEVELOPERS TERMS OF CONDITIONS UPDATE ON JULY 8TH FOR ALL INDIVIDUALS USING GEMINI WITHOUT BILLING
## SEE THIS https://ai.google.dev/gemini-api/terms#data-use-unpaid AND THIS https://discord.com/developers/docs/policies-and-agreements/developer-policy CLAUSE 21.
> 21. Do not use message content obtained through the APIs to train machine learning or AI models (including large language models) unless express permission is granted by Discord.

## This is a project I made for **FUN**

### This **IS** a rip off of [this service](https://discord.gg/shapes)

#### Gemini-AI-Bot
##### This is a discord bot that uses [google's gemini api](https://ai.google.dev/) to generate messages for a conversation, so far this project is not complete.

##### How to setup
```bash
pip install -r requirements.txt
```
##### Make sure to edit the `config.json` (v0.9)
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
        "MAX_CONTEXT_WINDOW" : 20,
        "FILTERS" : {
            "sexually_explicit" : "BLOCK_NONE",
            "harassment" : "BLOCK_NONE",
            "dangerous_content" : "BLOCK_NONE",
            "hate_speech" : "BLOCK_NONE",
            "unspecified" : "BLOCK_MEDIUM_AND_ABOVE"
        },
    "FREEWILL": {
        "enabled" : false,
        "text_frequency" : 0.02,
        "reaction_frequency" : 0,
        "keywords_added_chance" : 1,
        "keywords" : [""]
    },
    "MESSAGES" : {
        "wack" : "Ow! Uhh, what were we talking about?",
        "wack_error" : "Sorry, can't remove what's not there. :joy:",
        "error" : "Nuh uh, not gonna happen.",
        "activated_message" : "Hey! I'm new here :wave:",
        "deactivated_message" : "Awh, sorry to see you go! You can still talk to me by pinging me :pleading_face:"
    },
    "VOICE" : {
        "elevenlabs_api_key" : "",
        "record_time" : 10
    },
    "FILES" : {
        "allow" : true,
        "keep_in_context" : false
    },
    "BOT_TOKEN" : ""
}
``` 
#### Also, if there is need of a database helper, run `sqlhelper.py`, just remember to put your SQL credentials in.
