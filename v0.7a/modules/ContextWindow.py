import google.generativeai as genai
import json

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

genai.configure(api_key=config["API_KEY"])
model = genai.GenerativeModel(config["AI_MODEL"])

max_context_window = config["MAX_CONTEXT_WINDOW"]

class ContextWindow:
    context_window: dict = {}

    # def check_context_length_with_prompt(prompt, context_window, user_id) -> bool:
    #     """
    #     This function is used by `add_to_window`, it checks token
    #     """
    #     full_prompt = prompt + "\n" + "\n".join(context_window[user_id])
    #     tokens = genai.count_text_tokens(model=config["AI_MODEL"], prompt=full_prompt)
            
    #     return type(tokens)

    # def add_to_window(author, message, user_id):
    #     """
    #     This function auto-handles all token limits.
    #     """
    #     context_as_string = "\n".join(self.context_window[user_id])
    #     if self.check_context_length_with_prompt():
    #         return


# TODO : Reimplement this lol.