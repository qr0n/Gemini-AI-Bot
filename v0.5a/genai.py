import google.generativeai as genai
import json

my_id = "my-tuned-model-id"
operation = genai.create_tuned_model(
    id = my_id,
    source_model="models/text-bison-001",
    training_data=[
        {
            'hi': 'what',
            'output': 'example output'
        },
        {
            ""
        }
        ]
)
tuned_model=operation.result()      # Wait for tuning to finish

genai.generate_text(f"tunedModels/{my_id}", prompt="...")