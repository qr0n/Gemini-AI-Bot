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
    "SQL-CREDENTIALS" : {
        "username" : "",
        "password" : "",
        "host" : "",
        "database" : ""
    },
    "API-KEY" : "",
    "BOT-TOKEN" : "",
    "AI-MODEL" : "gemini-1.5-flash-latest"
}
``` 
###### Also, if there is need of a database helper, run `sqlhelper.py`, just remember to put your SQL credentials in.