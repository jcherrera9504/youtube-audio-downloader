#!/bin/bash
# Actualizar paquetes
apt-get update

# Instalar ffmpeg
apt-get install -y ffmpeg

# Instalar yt-dlp
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
chmod a+rx /usr/local/bin/yt-dlp

# Instalar dependencias de Python
pip install -r requirements.txt
