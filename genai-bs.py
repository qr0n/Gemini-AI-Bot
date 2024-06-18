import google.generativeai as genai



for i in genai.list_models():
    print(i.name)
