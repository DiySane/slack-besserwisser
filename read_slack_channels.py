import slack
import argparse
import typing
import os
import pandas as pd

SLACK_HISTORY_MESSAGE_LIMIT = 1000
SLACK_TOCKEN = os.environ["SLACK_APP_TOCKEN"]


def _read_one_channel(channel: dict,
                      client: slack.WebClient,
                      limit: int,
                      latest: int = None):
    channel_id = channel["id"]
    cnt = min([limit, SLACK_HISTORY_MESSAGE_LIMIT])
    if latest is None:
        # Let the slack server handle timestamp
        all_messages = client.channels_history(channel=channel_id,
                                               count=cnt).data["messages"]
    else:
        all_messages = client.channels_history(channel=channel_id,
                                               count=cnt,
                                               latest=latest).data["messages"]

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
    all_channels = client.channels_list().data["channels"]
    relevant_channels = filter(lambda x: x["name"] in channels, all_channels)
    messages = map(lambda x: _read_one_channel(x, client=client, limit=limit),
                   relevant_channels)
    return pd.concat(messages)


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
