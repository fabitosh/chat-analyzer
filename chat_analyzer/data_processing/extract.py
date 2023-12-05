import re

import pandas as pd
from pandera.typing import DataFrame

from chat_analyzer.utils.data_definitions import RawChat, CombinedChat


def parse_whatsapp(chat_txt) -> DataFrame[RawChat]:
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4},? \d{1,2}:\d{2}(?: [APap][Mm])?) - ([^:]+): (.+)$'
    matches = re.findall(pattern, chat_txt, re.MULTILINE)
    data = []
    for timestamp, sender, message in matches:
        data.append({'timestamp': timestamp, 'sender': sender, 'message': message})
    df = pd.DataFrame(data)
    df['datetime'] = pd.to_datetime(df['timestamp'], format="%d/%m/%Y, %H:%M", errors='raise')
    df = df.drop(columns='timestamp')
    # df['sender'] = df['sender'].astype("category")
    return DataFrame[RawChat](df)


def merge_consecutive_msg(df: DataFrame[RawChat], merge_window_s: float = 60) -> DataFrame[CombinedChat]:
    mask_time_delta = df['datetime'].diff() > pd.Timedelta(seconds=merge_window_s)
    mask_same_sender = df["sender"].shift() != df["sender"]
    mask_consecutive_messages = mask_time_delta | mask_same_sender
    df_combined = df.groupby(mask_consecutive_messages.cumsum()).agg(
        datetime=('datetime', 'first'),
        sender=('sender', 'first'),
        message=('message', '\n'.join),
        n_block=('message', 'count'),
        datetime_last=('datetime', 'last'),
    ).reset_index(drop=True)
    df_combined['block_duration'] = df_combined['datetime_last'] - df_combined['datetime']
    return DataFrame[CombinedChat](df_combined)
