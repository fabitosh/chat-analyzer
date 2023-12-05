from typing import Dict, List

import emoji
import numpy as np
import pandas as pd
from pandera.typing import DataFrame

from chat_analyzer import MY_CHAT_NAMES
from chat_analyzer.utils.data_definitions import CombinedChat, ChatFeatures, SingleChat, cat_weekdays, cat_months


def extract_single_chat_features(df) -> DataFrame[SingleChat]:
    """Features which need to be determined in the context of a single chat"""
    chat_participants = df.sender.unique()
    df['chat'] = ', '.join(p for p in chat_participants if p not in MY_CHAT_NAMES)
    if len(chat_participants) != 2:
        raise NotImplementedError(f"Group Chats and Monologues are not supported. "
                                  f"Your chat participants: {chat_participants}")
    a, b = chat_participants
    sender_to_receiver: dict = {a: b, b: a}
    df['receiver'] = df['sender'].map(sender_to_receiver)
    df['duration_since_their_last'] = determine_duration_since_their_last_message(df)
    df['duration_to_reply'] = determine_duration_to_reply(df)
    return DataFrame[SingleChat](df)


def add_features(df: DataFrame[CombinedChat]) -> DataFrame[ChatFeatures]:
    """Features which can be determined without the context of the chat"""
    id_to_month: Dict[int, str] = dict(enumerate(cat_months.categories))
    df['month'] = df.datetime.dt.month.map(id_to_month).astype(cat_months)

    df['week'] = df.datetime.dt.strftime('%Y-%U')

    id_to_weekday: Dict[int, str] = dict(enumerate(cat_weekdays.categories))
    df['weekday'] = df.datetime.dt.dayofweek.map(id_to_weekday).astype(cat_weekdays)

    df['hour'] = df.datetime.dt.hour.astype(np.uint8)

    df['n_symbols'] = df.message.str.len()
    df['emojis'] = extract_emojis(df.message)
    df['n_emojis'] = df.emojis.apply(len)
    return DataFrame[ChatFeatures](df)


def determine_duration_since_their_last_message(df) -> pd.Series:
    mask_sender_change = df["sender"].shift(-1) != df["sender"]
    time_since_last = (df['datetime'] -
                       df.groupby(mask_sender_change.cumsum())['datetime_last'].transform("min").shift(1))
    time_since_last = time_since_last.fillna(pd.Timedelta(seconds=0))  # first row
    return time_since_last


def determine_duration_to_reply(df) -> pd.Series:
    mask_is_new_sender = df["sender"].shift() != df["sender"]
    time_last_message = df.groupby(mask_is_new_sender.cumsum())['datetime_last'].transform("max").shift()
    time_to_respond = df.loc[mask_is_new_sender, 'datetime'] - time_last_message
    time_to_respond[0] = pd.Timedelta('0 days 00:00:00')
    return time_to_respond


def extract_emojis(s: pd.Series):
    return s.apply(extract_string_emojis)


def extract_string_emojis(text: str) -> List[str]:
    return [e.chars for e in emoji.analyze(text)]


