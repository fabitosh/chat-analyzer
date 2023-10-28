import pandas as pd
from pandas import Timestamp, Timedelta, NaT
from pandas._testing import assert_frame_equal, assert_series_equal
from pandera.typing import DataFrame

from chat_analyzer.aggregate import merge_consecutive_msg, determine_duration_since_their_last_message, \
    determine_duration_to_reply
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


def test_determine_duration_since_their_last_message():
    df = pd.DataFrame({
        'sender': list('YXXXY'),
        'datetime': [pd.Timestamp('2023-01-01 12:00'),
                     pd.Timestamp('2023-01-01 12:20'),
                     pd.Timestamp('2023-01-01 12:30:00'),
                     pd.Timestamp('2023-01-01 15:00'),
                     pd.Timestamp('2023-01-01 15:30:30'),
                     ],
        'datetime_last': [pd.Timestamp('2023-01-01 12:00'),
                          pd.Timestamp('2023-01-01 12:20'),
                          pd.Timestamp('2023-01-01 12:31:20'),
                          pd.Timestamp('2023-01-01 15:00'),
                          pd.Timestamp('2023-01-01 15:30:55'), ]})

    out = determine_duration_since_their_last_message(df)

    expected = pd.Series({0: Timedelta('0 days 00:00:00'),
                          1: Timedelta('0 days 00:20:00'),
                          2: Timedelta('0 days 00:30:00'),
                          3: Timedelta('0 days 03:00:00'),
                          4: Timedelta('0 days 00:30:30')})

    assert_series_equal(expected, out)


def test_determine_duration_to_reply():
    df = pd.DataFrame({
        'sender': list('YXXXY'),
        'datetime': [pd.Timestamp('2023-01-01 12:00'),
                     pd.Timestamp('2023-01-01 12:20'),
                     pd.Timestamp('2023-01-01 12:30:00'),
                     pd.Timestamp('2023-01-01 15:00'),
                     pd.Timestamp('2023-01-01 15:30:30'),
                     ],
        'datetime_last': [pd.Timestamp('2023-01-01 12:00'),
                          pd.Timestamp('2023-01-01 12:20'),
                          pd.Timestamp('2023-01-01 12:31:20'),
                          pd.Timestamp('2023-01-01 15:00'),
                          pd.Timestamp('2023-01-01 15:30:55'), ]})

    out = determine_duration_to_reply(df)

    expected = pd.Series({0: NaT,
                          1: Timedelta('0 days 00:20:00'),
                          2: NaT,
                          3: NaT,
                          4: Timedelta('0 days 00:30:30')})

    assert_series_equal(expected, out)
