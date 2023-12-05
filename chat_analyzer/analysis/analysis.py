import pandas as pd
from pandas.core.groupby import DataFrameGroupBy
from pandera.typing import DataFrame

from chat_analyzer.utils.data_definitions import ChatFeatures


def n_messages_per_day(df) -> pd.Series:
    n_msg_per_day = df.groupby(df.datetime.dt.date)['message'].count()
    n_msg_per_day.index = pd.to_datetime(n_msg_per_day.index)
    return n_msg_per_day


def hourly_statistics(df: DataFrame[ChatFeatures]) -> pd.DataFrame:
    grouping = df.groupby([df.hour, 'sender'])
    return agg_chat_metrics(grouping).reset_index()


def agg_chat_metrics(dfgb: DataFrameGroupBy) -> pd.DataFrame:
    """derive statistics of grouped data"""
    df = dfgb.agg(
        total_messages=('message', 'count'),
        total_symbols=('n_symbols', 'sum'),
        avg_symbols_per_message=('n_symbols', 'mean'),
        avg_time_to_reply=('duration_to_reply', 'mean'),
        avg_time_since_their_last=('duration_since_their_last', 'mean'),
        count_msg_with_answer=('duration_to_reply', 'count'),
    )
    df['n_follow_up_messages'] = df['total_messages'] - df['count_msg_with_answer']
    df = df.drop(columns='count_msg_with_answer')
    return df
