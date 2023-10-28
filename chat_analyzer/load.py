import os
import re
import datetime
from typing import Optional

import pandas as pd
from pandera.typing import DataFrame

from chat_analyzer import PATH_WHATSAPP_MSG, PATH_SIGNAL_MSG
from chat_analyzer.aggregate import merge_consecutive_msg
from chat_analyzer.types import RawChat


def parse_whatsapp(chat_export: str) -> DataFrame[RawChat]:
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4},? \d{1,2}:\d{2}(?: [APap][Mm])?) - ([^:]+): (.+)$'
    matches = re.findall(pattern, chat_export, re.MULTILINE)

    data = []
    for match in matches:
        timestamp, sender, message = match
        data.append({'timestamp': timestamp, 'sender': sender, 'message': message})

    df = pd.DataFrame(data)
    df['datetime'] = pd.to_datetime(df['timestamp'], format="%d/%m/%Y, %H:%M", errors='raise')
    df = df.drop(columns='timestamp')
    # df['sender'] = df['sender'].astype("category")
    chat_participants = df.sender.unique().tolist()
    if len(chat_participants) == 2:
        sender_to_receiver: dict = {chat_participants[0]: chat_participants[1],
                                    chat_participants[1]: chat_participants[0]}
        df['receiver'] = df['sender'].map(sender_to_receiver)
    # df['week'] = df.datetime.dt.strftime('%Y-%U')
    # df['n_symbols'] = df.message.str.len()
    return DataFrame[RawChat](df)


def aggregate_whatsapp_conversations(path_whatsapp_chats: str) -> Optional[pd.DataFrame]:
    df = None
    for file in os.listdir(path_whatsapp_chats):
        filename = os.fsdecode(file)
        print(filename)
        if filename.endswith(".txt"):
            filepath = os.path.join(path_whatsapp_chats, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                chat_export = file.read()

            df_raw = parse_whatsapp(chat_export)
            df_combined = merge_consecutive_msg(df_raw)
            df_chat = make_features(df_combined)

            if df is None:
                df = df_chat
            else:
                df = pd.concat([df, df_chat])
            continue
        else:
            continue
    return df


def agg_to_pkl(path_whatsapp, path_signal) -> str:
    df = aggregate_whatsapp_conversations(path_whatsapp)
    dtnow = datetime.datetime.now().strftime("%d%m%Y-%H%M")
    path_pkl = f"../data/df_whatsapp_{dtnow}.pkl"
    df.to_pickle(path_pkl)
    return path_pkl


if __name__ == "__main__":
    agg_to_pkl(PATH_WHATSAPP_MSG, PATH_SIGNAL_MSG)


