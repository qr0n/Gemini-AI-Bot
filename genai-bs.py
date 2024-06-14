import google.generativeai as genai

genai.configure(api_key="AIzaSyDCBEsCR--gdmguCaHifg9k7dxPRDUe-NQ")

for i in genai.list_models():
    print(i.name)