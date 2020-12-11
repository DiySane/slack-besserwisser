import os
import slack
import sidekick
from slackeventsapi import SlackEventAdapter
# from slack import SlackEventAdapter
from slack import WebClient

DEPLOYMENT_URL = os.environ["PELTARION_DEPLOYMENT_URL"]
DEPLOYMENT_TOKEN = os.environ["PELTARION_DEPLOYMENT_TOKEN"]
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]

THRESHOLD = 0.7

sidekick_client = sidekick.Deployment(url=DEPLOYMENT_URL,
                                      token=DEPLOYMENT_TOKEN)

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

# Create a SlackClient for your bot to use for Web API requests
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = WebClient(slack_bot_token)

# Example responder to greetings


@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "hi" in message.get('text'):
        channel = message["channel"]
        message = "Hello <@%s>! :tada:" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=message)
    if message.strip() == "":
        return

    prediction = sidekick_client.predict(message=message)
    random_score = prediction['channel']['random']
    if random_score > THRESHOLD:
        message = f"I'm {random_score * 100 :.2f}% sure that this belongs in #random."
        slack_client.chat_postMessage(channel=channel, text=message)
        # web_client.chat_postMessage(channel=channel_id,
        #                             text=message,
        #                             thread_ts=thread_ts)


# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    slack_client.chat_postMessage(channel=channel, text=text)

# Error events


@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))


# Once we have our event listeners configured, we can start the
# Flask server with the default `/events` endpoint on port 3000
slack_events_adapter.start(port=3000)


@slack.RTMClient.run_on(event='message')
def check_for_random_messages(**payload):
    data = payload['data']
    user = data.get('user')
    # Ignore messages without user
    if user is None:
        return
    web_client: slack.WebClient = payload['web_client']
    channel_id = data['channel']
    thread_ts = data['ts']
    message = data.get("text", "")

    # Don't answer to empty messages
    if message.strip() == "":
        return

    prediction = sidekick_client.predict(message=message)
    random_score = prediction['channel']['random']
    if random_score > THRESHOLD:
        message = f"I'm {random_score * 100 :.2f}% sure that this \
belongs in #random."

        web_client.chat_postMessage(channel=channel_id,
                                    text=message,
                                    thread_ts=thread_ts)


# def main():
    # rtm_client = slack.RTMClient(token=SLACK_TOKEN)
    # rtm_client.start()


# if __name__ == '__main__':
    # main()
