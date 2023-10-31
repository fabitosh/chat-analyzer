import pandas as pd
from pandera.typing import DataFrame

from chat_analyzer.data_definitions import RawChat, CombinedChat, ChatFeatures


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
        receiver=('receiver', 'first'),
        chat=('chat', 'first')
    )
    df_combined['block_duration'] = df_combined['datetime_last'] - df_combined['datetime']
    return DataFrame[CombinedChat](df_combined)


def add_features(df: DataFrame[CombinedChat]) -> DataFrame[ChatFeatures]:
    df['week'] = df.datetime.dt.strftime('%Y-%U')
    df['n_symbols'] = df.message.str.len()
    df['duration_since_their_last'] = determine_duration_since_their_last_message(df)
    df['duration_to_reply'] = determine_duration_to_reply(df)
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
