from typing import Dict

import pandas as pd
from pandera.typing import DataFrame

from chat_analyzer import MY_CHAT_NAMES
from chat_analyzer.data_definitions import CombinedChat, ChatFeatures, SingleChat
from chat_analyzer.data_definitions import CombinedChat, ChatFeatures, SingleChat, cat_weekdays


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
    df['week'] = df.datetime.dt.strftime('%Y-%U')
    df['n_symbols'] = df.message.str.len()
    d: Dict[int, str] = dict(enumerate(cat_weekdays.categories))
    df['weekday'] = df.datetime.dt.dayofweek.map(d).astype(cat_weekdays)
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


if __name__ == '__main__':
    pass
