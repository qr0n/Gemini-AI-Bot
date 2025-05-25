FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y libopus-dev mpv wget
RUN apt-get remove youtube-dl
RUN wget https://github.com/yt-dlp/yt-dlp/releases/download/2025.04.30/yt-dlp_linux -O /usr/local/bin/youtube-dl
RUN chmod a+rx /usr/local/bin/youtube-dl
RUN apt-get install python-is-python3
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]