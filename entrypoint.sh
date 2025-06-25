#!/bin/sh

echo "Attivazione debugpy..."

# Aspetta che il DB sia pronto
echo "Aspetto il DB..."
python -c "
import socket, time
while True:
    try:
        s = socket.create_connection(('db', 5432))
        s.close()
        break
    except:
        time.sleep(1)
"

# Avvia Django con debugpy
exec python -Xfrozen_modules=off -m debugpy --wait-for-client --listen 0.0.0.0:5678 manage.py runserver 0.0.0.0:8000
