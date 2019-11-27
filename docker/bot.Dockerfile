FROM python:3.7.5-buster
COPY requirements.txt /workspace/requirements.txt
WORKDIR /workspace
RUN pip install -r requirements.txt
COPY listen_and_reply.py /workspace/listen_and_reply.py
ENTRYPOINT [ "python", "listen_and_reply.py" ]
