import os
import re
import datetime
from typing import Optional

import pandas as pd
from pandera.typing import DataFrame

from chat_analyzer import PATH_WHATSAPP_MSG, PATH_SIGNAL_MSG, MY_CHAT_NAMES
from chat_analyzer.aggregate import merge_consecutive_msg, add_features
from chat_analyzer.data_definitions import RawChat, SingleChat


def parse_whatsapp(chat_txt) -> DataFrame[RawChat]:
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4},? \d{1,2}:\d{2}(?: [APap][Mm])?) - ([^:]+): (.+)$'
    matches = re.findall(pattern, chat_txt, re.MULTILINE)
    data = []
    for timestamp, sender, message in matches:
        data.append({'timestamp': timestamp, 'sender': sender, 'message': message})
    df = pd.DataFrame(data)
    df['datetime'] = pd.to_datetime(df['timestamp'], format="%d/%m/%Y, %H:%M", errors='raise')
    df = df.drop(columns='timestamp')
    return DataFrame[RawChat](df)


def load_whatsapp_chat(chat_txt: str) -> DataFrame[SingleChat]:
    df = parse_whatsapp(chat_txt)
    # df['sender'] = df['sender'].astype("category")
    chat_participants = df.sender.unique()
    df['chat'] = ', '.join(p for p in chat_participants if p not in MY_CHAT_NAMES)

    if len(chat_participants) != 2:
        raise NotImplementedError(f"Group Chats and Monologues are not supported. "
                                  f"Your chat participants: {chat_participants}")

    a, b = chat_participants
    sender_to_receiver: dict = {a: b, b: a}
    df['receiver'] = df['sender'].map(sender_to_receiver)
    return DataFrame[SingleChat](df)


def aggregate_whatsapp_conversations(path_whatsapp_chats: str) -> Optional[pd.DataFrame]:
    dfs = []
    for file in os.listdir(path_whatsapp_chats):
        filename = os.fsdecode(file)
        print(filename)
        if filename.endswith(".txt"):
            filepath = os.path.join(path_whatsapp_chats, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                chat_export = file.read()

            df_single = load_whatsapp_chat(chat_export)
            df_combined = merge_consecutive_msg(df_single)
            df_chat = add_features(df_combined)
            dfs.append(df_chat)
    return pd.concat(dfs)


def agg_to_pkl(path_whatsapp, path_signal) -> str:
    df = aggregate_whatsapp_conversations(path_whatsapp)
    dtnow = datetime.datetime.now().strftime("%d%m%Y-%H%M")
    path_pkl = f"../data/df_whatsapp_{dtnow}.pkl"
    df.to_pickle(path_pkl)
    return path_pkl


if __name__ == "__main__":
    pkl_path = agg_to_pkl(PATH_WHATSAPP_MSG, PATH_SIGNAL_MSG)
    print(f"Chats aggregated in pickle file at {pkl_path}")
