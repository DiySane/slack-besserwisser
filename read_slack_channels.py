import slack
import argparse
import typing
import os
import pandas as pd
import json
# from slack_sdk.errors import SlackApiError

SLACK_HISTORY_MESSAGE_LIMIT = 1000
SLACK_TOCKEN = os.environ["SLACK_APP_TOCKEN"]

all_channels = []

def fetch_conversations(client, types="public_channel,private_channel"):
    try:
        # Call the conversations.list method using the WebClient
        next_cursor = ''
        while True:
            print("next_cursor: {}\n".format(next_cursor))
            result = client.conversations_list(limit=1000, cursor = next_cursor, types=types)
            save_conversations(result["channels"])
            if result["response_metadata"]["next_cursor"] != "":
                next_cursor = result["response_metadata"]["next_cursor"]
            else:
                next_cursor = ""
                break

    except SlackApiError as e:
        logger.error("Error fetching conversations: {}".format(e))


# Put conversations into the JavaScript object
def save_conversations(conversations):
    # conversation_id = ""
    for conversation in conversations:
        # Key conversation info on its unique ID
        # conversation_id = conversation["id"]

        # Store the entire conversation object
        # (you may not need all of the info)
        all_channels.append(conversation)

# fetch_conversations()


def _read_one_channel(channel: dict,
                      client: slack.WebClient,
                      limit: int,
                      latest: int = None):
    print("channel: {}", channel)
    channel_id = channel["id"]
    cnt = min([limit, SLACK_HISTORY_MESSAGE_LIMIT])
    # print("users_convo: {}\n".format(client.conversations_history(channel=channel_id,
    #                                                             count=5)))
    if latest is None:
        # Let the slack server handle timestamp
        # all_messages = client.channels_history(channel=channel_id,
        #                                        count=cnt).data["messages"]
        # all_messages = client.users_conversations(channel=channel_id,
        #                                        count=cnt).data["messages"]
        all_messages = client.conversations_history(channel=channel_id,
                                               count=cnt).data["messages"]
    else:
        all_messages = client.conversations_history(channel=channel_id,
                                               count=cnt,
                                               latest=latest).data["messages"]
    # print("all_messages: {}\n", all_messages)

    oldest = all_messages[-1]["ts"]
    filtered_by_type = list(
        filter(lambda x: x["type"] == "message", all_messages))
    n_retrieved = len(filtered_by_type)
    message_texts = map(lambda x: x["text"], filtered_by_type)
    current_df = pd.DataFrame({
        "channel": channel["name"],
        "message": message_texts
    })
    if n_retrieved < limit and len(all_messages) == cnt:
        next_df = _read_one_channel(client=client,
                                    channel=channel,
                                    limit=limit - n_retrieved,
                                    latest=oldest)
        return pd.concat((current_df, next_df))

    return current_df


def read_channels_into_df(token: str, channels: typing.List[str],
                          limit: int) -> pd.DataFrame:
    client = slack.WebClient(token=token)
    print("channels: {}\n",channels)
    # all_channels = client.channels_list().data["channels"]
    # all_channels = client.conversations_list()
    fetch_conversations(client)
    # print("all_channels: {}\n",json.dumps(all_channels))
    print("all_channels_count: {}\n",len(all_channels))
    # relevant_channels = filter(lambda x: x["name"] in channels, all_channels)
    relevant_channels = [x for x in all_channels if x["name"] in channels]
    print("relevant_channels: {}\n".format(json.dumps(relevant_channels)))
    messages = map(lambda x: _read_one_channel(x, client=client, limit=limit),
                   relevant_channels)
    return pd.concat(messages)
    # return pd.concat(map(lambda x: _read_one_channel(x, client=client, limit=limit),
    #                relevant_channels))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channels",
                        "-c",
                        nargs="+",
                        required=False,
                        type=str,
                        default=["general", "random"],
                        help="The channels to read")
    parser.add_argument("--limit",
                        "-l",
                        help="Maximum number of messages per channel",
                        type=int,
                        default=6000)

    parser.add_argument("--output", "-o", type=str, default="channels.csv")
    return parser.parse_args()


def main():
    args = parse_args()
    df = read_channels_into_df(token=SLACK_TOCKEN,
                               channels=args.channels,
                               limit=args.limit)
    print("Counts of messages per channel:\n")
    print(df.groupby("channel").count())
    df.to_csv(args.output, index_label="index")


if __name__ == '__main__':
    main()
