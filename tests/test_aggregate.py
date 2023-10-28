import pandas as pd
from pandas import Timestamp, Timedelta
from pandas._testing import assert_frame_equal
from pandera.typing import DataFrame

from chat_analyzer.aggregate import merge_consecutive_msg
from chat_analyzer.types import RawChat


def test_merge_consecutive_msg():
    raw = {
        'index': [0, 1, 2, 3, 4], 'columns': ['sender', 'message', 'datetime', 'receiver'],
        'data': [
            ['Max Von Muster', 'Hello there 😁', pd.Timestamp('2020-01-06 23:39:00'), 'Veronika'],
            ['Veronika', 'Who are you? 😡', pd.Timestamp('2020-01-07 07:00:00'), 'Max Von Muster'],
            ['Veronika', 'Leave me alone.', pd.Timestamp('2020-01-07 11:43:00'), 'Max Von Muster'],
            ['Veronika', 'Changed my mind', pd.Timestamp('2020-01-07 11:44:00'), 'Max Von Muster'],
            ['Max Von Muster', 'Sorry.', pd.Timestamp('2020-01-07 13:01:00'), 'Veronika']],
        'index_names': [None], 'column_names': [None]}
    df_raw = pd.DataFrame.from_dict(raw, orient='tight')
    df = DataFrame[RawChat](df_raw)
    result = merge_consecutive_msg(df, merge_window_s=60)

    expected = \
        {'index': [0, 1, 2, 3],
         'columns': ['datetime', 'sender', 'message', 'n_block', 'datetime_last', 'receiver', 'block_duration'],
         'data': [
             [Timestamp('2020-01-06 23:39:00'), 'Max Von Muster', 'Hello there 😁', 1, Timestamp('2020-01-06 23:39'),
              'Veronika', Timedelta('0 days 00:00:00')],
             [Timestamp('2020-01-07 07:00:00'), 'Veronika', 'Who are you? 😡', 1, Timestamp('2020-01-07 07:00'),
              'Max Von Muster', Timedelta('0 days 00:00:00')],
             [Timestamp('2020-01-07 11:43'), 'Veronika', 'Leave me alone.\nChanged my mind', 2,
              Timestamp('2020-01-07 11:44'), 'Max Von Muster', Timedelta('0 days 00:01:00')],
             [Timestamp('2020-01-07 13:01'), 'Max Von Muster', 'Sorry.', 1, Timestamp('2020-01-07 13:01'),
              'Veronika', Timedelta('0 days 00:00:00')]],
         'index_names': [None], 'column_names': [None]}
    df_expected = pd.DataFrame.from_dict(expected, orient='tight')

    assert_frame_equal(result, df_expected)
