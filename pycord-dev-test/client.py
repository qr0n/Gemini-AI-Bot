from elevenlabs import play, save
from elevenlabs.client import ElevenLabs

client = ElevenLabs(
  api_key="sk_3696dde3641726a857f6fabbdf8b4b9a1311d90adeca320b" # Defaults to ELEVEN_API_KEY
)

audio = client.generate(
  text="Hello! 你好! Hola! नमस्ते! Bonjour! こんにちは! مرحبا! 안녕하세요! Ciao! Cześć! Привіт! வணக்கம்!",
  voice="Rachel",
  model="eleven_multilingual_v2"
)

save(audio, "my-file.mp3")