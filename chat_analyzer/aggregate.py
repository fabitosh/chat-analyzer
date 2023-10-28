import pandas as pd
from pandera.typing import DataFrame

from chat_analyzer.types import RawChat, CombinedChat


def merge_consecutive_msg(df: DataFrame[RawChat], merge_window_s: float = 60) -> DataFrame[CombinedChat]:
    mask_time_delta = df['datetime'].diff() > pd.Timedelta(seconds=merge_window_s)
    mask_same_sender = df["sender"].shift() != df["sender"]
    mask_consecutive_messages = mask_time_delta | mask_same_sender
    df_combined = df.groupby(mask_consecutive_messages.cumsum(), as_index=False).agg(
        datetime=('datetime', 'first'),
        sender=('sender', 'first'),
        message=('message', '\n'.join),
        n_block=('message', 'count'),
        datetime_last=('datetime', 'last'),
        receiver=('receiver', 'first'))
    df_combined['block_duration'] = df_combined['datetime_last'] - df_combined['datetime']
    return DataFrame[CombinedChat](df_combined)


def add_features(df: DataFrame[CombinedChat]):
    df['week'] = df.datetime.dt.strftime('%Y-%U')
    df['n_symbols'] = df.message.str.len()


if __name__ == '__main__':
    pass
