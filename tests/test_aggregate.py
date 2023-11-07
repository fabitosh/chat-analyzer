import pandas as pd
from pandas import Timestamp, Timedelta
from pandas._testing import assert_frame_equal
from pandera.typing import DataFrame

from chat_analyzer.aggregate import merge_consecutive_msg
from chat_analyzer.data_definitions import RawChat


def test_merge_consecutive_msg():
    raw = {
        'index': [0, 1, 2, 3, 4], 'columns': ['sender', 'message', 'datetime'],
        'data': [
            ['A', 'Hi', pd.Timestamp('2020-01-06 23:39:00')],
            ['B', 'Who?', pd.Timestamp('2020-01-07 07:00:00')],
            ['B', 'Leave', pd.Timestamp('2020-01-07 11:43:00')],
            ['B', 'Now', pd.Timestamp('2020-01-07 11:44:00')],
            ['A', 'Sorry.', pd.Timestamp('2020-01-07 13:01:00')]],
        'index_names': [None], 'column_names': [None]}
    df_raw = pd.DataFrame.from_dict(raw, orient='tight')
    df = DataFrame[RawChat](df_raw)
    result = merge_consecutive_msg(df, merge_window_s=60)

    expected = \
        {'index': [0, 1, 2, 3],
         'columns': ['datetime', 'sender', 'message', 'n_block', 'datetime_last', 'block_duration'],
         'data': [
             [Timestamp('2020-01-06 23:39:00'), 'A', 'Hi', 1, Timestamp('2020-01-06 23:39'),
              Timedelta('0 days 00:00:00')],
             [Timestamp('2020-01-07 07:00:00'), 'B', 'Who?', 1, Timestamp('2020-01-07 07:00'),
              Timedelta('0 days 00:00:00')],
             [Timestamp('2020-01-07 11:43'), 'B', 'Leave\nNow', 2, Timestamp('2020-01-07 11:44'),
              Timedelta('0 days 00:01:00')],
             [Timestamp('2020-01-07 13:01'), 'A', 'Sorry.', 1, Timestamp('2020-01-07 13:01'),
              Timedelta('0 days 00:00:00')]],
         'index_names': [None], 'column_names': [None]}
    df_expected = pd.DataFrame.from_dict(expected, orient='tight')

    assert_frame_equal(result, df_expected)
