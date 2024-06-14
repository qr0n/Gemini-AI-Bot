from modules.BotModel import BotModel

class ContextWindow:
    def __init__(self) -> None:
        self.context_window: dict = {}

    def count_tokens(self, user_id):
        ctx_as_string = "\n".join(self.context_window[user_id]) # TODO : switch to localized ctx window.
        prompt = BotModel.read_prompt() + "\n" + ctx_as_string
        return 
    
    def add_to_window(self, author, message, user_id):
        if self.context_window[user_id]:
            ctx_as_string = "\n".join(self.context_window[user_id])
            self.context_window[user_id].append(f"{author} : {message}")
        else:
            self.context_window[user_id] = []
            self.context_window[user_id].append(f"{author} : {message}")

ContextWindow().context_window