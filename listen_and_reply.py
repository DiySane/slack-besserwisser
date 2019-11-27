import os
import slack
import sidekick

DEPLOYMENT_URL = os.environ["PELTARION_DEPLOYMENT_URL"]
DEPLOYMENT_TOKEN = os.environ["PELTARION_DEPLOYMENT_TOKEN"]
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]

THRESHOLD = 0.7

sidekick_client = sidekick.Deployment(url=DEPLOYMENT_URL,
                                      token=DEPLOYMENT_TOKEN)


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


def main():
    rtm_client = slack.RTMClient(token=SLACK_TOKEN)
    rtm_client.start()


if __name__ == '__main__':
    main()
