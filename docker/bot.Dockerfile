FROM python:3.7.5-buster
# FROM python:3.8-slim-buster
# FROM 3.10.0a3-alpine3.12
COPY requirements.txt /workspace/requirements.txt
# COPY requirements.txt /workspace
WORKDIR /workspace
# RUN pip install slackeventsapi
# RUN apk add --update build-base libffi-dev
# RUN apk add --update py3-pip
# RUN pip install -r requirements.txt
RUN pip install requirements.txt
RUN python -m pip install slackeventsapi
COPY listen_and_reply.py /workspace/listen_and_reply.py
ENTRYPOINT [ "python", "listen_and_reply.py" ]
