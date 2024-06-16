import google.generativeai as genai
import json

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

genai.configure(api_key=config["API_KEY"])

my_id = "my-tuned-model-id"
operation = genai.create_tuned_model(
    id = my_id,
    source_model="models/text-bison-001",
    training_data=[{'text_input': 'example input', 'output': 'example output'}]
)
tuned_model=operation.result()      # Wait for tuning to finish

genai.generate_text(f"tunedModels/{my_id}", prompt="...")