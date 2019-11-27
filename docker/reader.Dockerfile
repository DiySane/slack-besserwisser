FROM python:3.7.5-buster
COPY requirements.txt /workspace/requirements.txt
WORKDIR /workspace
RUN pip install -r requirements.txt
COPY read_slack_channels.py /workspace/read_slack_channels.py
ENTRYPOINT [ "python", "read_slack_channels.py" ]
