from alpine:3.11
run apk add --no-cache python3 && \
    apk add --no-cache py3-pip && \
    pip3 install --no-cache --upgrade pip && \
    pip3 install --no-cache gunicorn && \
    pip3 install --no-cache flask && \
    pip3 install -r requirements.txt
copy . /app
entrypoint ["python3", "run-server.py"]
