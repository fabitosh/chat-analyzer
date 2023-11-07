import pandas as pd
from pandas.core.groupby import DataFrameGroupBy
from pandera.typing import DataFrame

from chat_analyzer.data_definitions import RawChat, CombinedChat


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


def agg_chat_metrics(dfgb: DataFrameGroupBy) -> None:
    """derive statistics of grouped data"""
    dfgb.agg(
        total_symbols=('n_symbols', 'sum'),
        total_messages=('message', 'count'),
        avg_time_to_reply=('duration_to_reply', 'mean'),
    )
