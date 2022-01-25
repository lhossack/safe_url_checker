FROM python:3.8-slim

RUN apt-get update && \ 
    apt-get -qq install -y

WORKDIR /app

RUN python3 -m venv .venv
RUN .venv/bin/pip install gunicorn

COPY requirements.txt setup.py README.md ./
COPY urlchecker/*.py urlchecker/
RUN .venv/bin/pip install -r requirements.txt

COPY sample_resources/* sample_resources/

ENV FLASK_ENV=production URLINFO_LOGLEVEL=INFO URLINFO_CONFIG=/app/sample_resources/default_config.json

EXPOSE 8000

CMD ["/bin/bash", "-c", \
    ".venv/bin/gunicorn -b 0.0.0.0:8000 --workers=2 'urlchecker.flask_frontend:create_app()'"]