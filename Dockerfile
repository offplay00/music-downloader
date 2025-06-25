# Dockerfile
FROM python:3.11-slim

# Imposta variabili di ambiente per migliorare le prestazioni
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Imposta la directory di lavoro
WORKDIR /code

# Installa dipendenze di sistema necessarie (ffmpeg) e pulisci i file temporanei
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia solo il file requirements.txt per installare le dipendenze Python
COPY requirements.txt /code/

# Installa le dipendenze Python senza cache
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice nel container
COPY . /code/

# Comando di default per avviare l'applicazione
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]