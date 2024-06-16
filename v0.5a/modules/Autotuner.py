# TODO : https://ai.google.dev/api/python/google/generativeai/create_tuned_model
"""
Use User Feedback Loop:
To set up a feedback loop, you could implement a rating system
after each interaction or provide a way for users 
to report issues with specific responses. 
Collecting this data will allow you to identify patterns
in what users find helpful or not and adjust the chatbot’s behavior.
"""

"""
Use discord.ext.tasks.loop to tune a model gradually personalizing the responses.
Make sure the content is saved, make sure the content saved is worth anything
Make sure this feature is togglable
Make sure to keep the past 3 models alive
Make sure to delete models that aren't worthy
Make sure to collect user data.
"""