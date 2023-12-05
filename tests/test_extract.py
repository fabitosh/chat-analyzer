from pandas import Timestamp, Timedelta
from pandas.testing import assert_frame_equal

import pandas as pd
import pytest
from pandera.typing import DataFrame

from chat_analyzer.data_processing.extract import parse_whatsapp, merge_consecutive_msg
from chat_analyzer.utils.data_definitions import RawChat


def test_parse_whatsapp_ignores_whatsapp_disclaimer():
    raw_text_input = '''
06/01/2020, 23:39 - Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp...
06/01/2020, 23:39 - Max: Hello there
07/01/2020, 07:00 - Veronika: Who are you?
        '''
    result = parse_whatsapp(raw_text_input)

    expected = {
        'index': [0, 1, ], 'columns': ['sender', 'message', 'datetime'],
        'data': [
            ['Max', 'Hello there', pd.Timestamp('2020-01-06 23:39:00')],
            ['Veronika', 'Who are you?', pd.Timestamp('2020-01-07 07:00:00')]],
        'index_names': [None], 'column_names': [None]}
    df_expected = pd.DataFrame.from_dict(expected, orient='tight')

    assert_frame_equal(result, df_expected)


def test_parse_whatsapp_can_handle_emojis():
    raw_text_input = '''
06/01/2020, 23:39 - Max: Hello there 😁
07/01/2020, 07:00 - Veronika: Who are you? 😡
07/01/2020, 11:43 - Veronika: Leave me alone.
07/01/2020, 13:01 - Max: Sorry.
        '''
    result = parse_whatsapp(raw_text_input)

    expected = {
        'index': [0, 1, 2, 3], 'columns': ['sender', 'message', 'datetime'],
        'data': [
            ['Max', 'Hello there 😁', pd.Timestamp('2020-01-06 23:39:00')],
            ['Veronika', 'Who are you? 😡', pd.Timestamp('2020-01-07 07:00:00')],
            ['Veronika', 'Leave me alone.', pd.Timestamp('2020-01-07 11:43:00')],
            ['Max', 'Sorry.', pd.Timestamp('2020-01-07 13:01:00')]],
        'index_names': [None], 'column_names': [None]}
    df_expected = pd.DataFrame.from_dict(expected, orient='tight')

    assert_frame_equal(result, df_expected)


def test_parse_whatsapp_can_handle_spaces_in_name():
    raw_text_input = '''
06/01/2020, 23:39 - Max Von Muster: Hello there 😁
07/01/2020, 07:00 - Veronika: Who are you? 😡
07/01/2020, 11:43 - Veronika: Leave me alone.
07/01/2020, 13:01 - Max Von Muster: Sorry.
        '''
    result = parse_whatsapp(raw_text_input)

    expected = {
        'index': [0, 1, 2, 3], 'columns': ['sender', 'message', 'datetime'],
        'data': [
            ['Max Von Muster', 'Hello there 😁', pd.Timestamp('2020-01-06 23:39:00')],
            ['Veronika', 'Who are you? 😡', pd.Timestamp('2020-01-07 07:00:00')],
            ['Veronika', 'Leave me alone.', pd.Timestamp('2020-01-07 11:43:00')],
            ['Max Von Muster', 'Sorry.', pd.Timestamp('2020-01-07 13:01:00')]],
        'index_names': [None], 'column_names': [None]}
    df_expected = pd.DataFrame.from_dict(expected, orient='tight')

    assert_frame_equal(result, df_expected)


def test_parse_whatsapp_raises_change_in_datetime_format():
    raw_text_input = '''
06/21/2020, 23:39 - Max: Hello there
07/21/2020, 07:00 - Veronika: Who are you?
        '''
    with pytest.raises(ValueError):
        _ = parse_whatsapp(raw_text_input)


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
