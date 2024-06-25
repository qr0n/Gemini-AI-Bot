import time
import google.generativeai as genai
import json

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

genai.configure(api_key=config["GEMINI"]["API_KEY"])

video_file = genai.upload_file("3195394-uhd_3840_2160_25fps.mp4")

while video_file.state.name == "PROCESSING":
    print('.', end='')
    time.sleep(1)
    video_file = genai.get_file(video_file.name)

if video_file.state.name == "FAILED":
  raise ValueError(video_file.state.name)

# Create the prompt.
prompt = "Describe this video."

# The Gemini 1.5 models are versatile and work with multimodal prompts
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# Make the LLM request.
print("Making LLM inference request...")
response = model.generate_content([video_file, prompt], request_options={"timeout": 600})
print(response.text)