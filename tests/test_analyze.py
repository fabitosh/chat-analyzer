import pandas as pd
from pandas import Timedelta, NaT
from pandas._testing import assert_series_equal

from chat_analyzer.analyze import determine_duration_since_their_last_message, determine_duration_to_reply


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

    expected = pd.Series({0: Timedelta('0 days 00:00:00'),
                          1: Timedelta('0 days 00:20:00'),
                          2: NaT,
                          3: NaT,
                          4: Timedelta('0 days 00:30:30')})

    assert_series_equal(expected, out)
