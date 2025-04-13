FROM python:3.13-slim

WORKDIR /app

# Instalacja zależności dla Pygame i innych bibliotek graficznych
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie plików projektu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu
COPY . .

# Uruchomienie symulacji z wirtualnym ekranem (dla Pygame)
CMD ["xvfb-run", "-a", "python", "main.py"]