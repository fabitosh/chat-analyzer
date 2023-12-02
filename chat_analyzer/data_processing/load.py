import os
import re
import datetime
from typing import Optional

import pandas as pd
from pandera.typing import DataFrame

from chat_analyzer import PATH_WHATSAPP_MSG, PATH_SIGNAL_MSG
from chat_analyzer.data_processing.aggregate import merge_consecutive_msg
from chat_analyzer.analysis.analyze import add_features, extract_single_chat_features
from chat_analyzer.utils.data_definitions import RawChat, SingleChat


def load_whatsapp_chat(chat_txt: str) -> DataFrame[SingleChat]:
    df = parse_whatsapp(chat_txt)
    df = merge_consecutive_msg(df, merge_window_s=60)
    df = extract_single_chat_features(df)
    return DataFrame[SingleChat](df)


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
            df_chat = add_features(df_single)
            dfs.append(df_chat)
    df = pd.concat(dfs)
    df = add_features(df)
    return df


def agg_to_pkl(path_whatsapp, path_signal, path_processed_pkl) -> str:
    df = aggregate_whatsapp_conversations(path_whatsapp)
    dtnow = datetime.datetime.now().strftime("%d%m%Y-%H%M")
    file_name = f"df_whatsapp_{dtnow}.pkl"
    path_pkl = os.path.join(path_processed_pkl, file_name)
    df.to_pickle(path_pkl)
    return path_pkl
