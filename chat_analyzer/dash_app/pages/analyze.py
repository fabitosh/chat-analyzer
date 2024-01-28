import glob
import os

import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, dash_table, register_page
import dash_bootstrap_components as dbc

from chat_analyzer import PATH_DIR_PROCESSED_PICKLES, MY_CHAT_NAMES
from chat_analyzer.analysis.analysis import agg_chat_metrics, hourly_statistics
from chat_analyzer.visualization.visualize import timedelta_to_str, create_fig_hourly_barpolar

register_page(
    __name__,
    name='Analyze',
    top_nav=True,
    order=3,
)


pkl_files = glob.glob('../../' + PATH_DIR_PROCESSED_PICKLES + '*.pkl')
latest_pkl_file = max(pkl_files, key=os.path.getctime)
df = pd.read_pickle(latest_pkl_file)


def layout():
    layout = html.Div([
        dbc.Row(html.H1(children=f'chat-analyzer for {MY_CHAT_NAMES[0]}', style={'textAlign': 'center'})),
        dbc.Row(html.H3(children=f'using {latest_pkl_file}', style={'textAlign': 'center'})),
        dbc.Row(html.Hr()),
        dbc.Row([
            controls,
            dbc.Col([
                dbc.Row(dash_table.DataTable(id='table-total-stats')),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='graph-hourly-barpolar'), width=3),
                    dbc.Col(dcc.Graph(id='graph-time-to-reply-per-day')),
                ])
            ])
        ]),
        dbc.Row(html.Hr()),
    ])
    return layout

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    # "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    # "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

controls = dbc.Col(
    [
        html.H3("Filters", className="display-4"),
        html.Hr(),
        html.P("Select the data of interest", className="lead"),
        html.P("Chat"),
        dcc.Dropdown(df.chat.unique(), id='chat-selection', multi=True, maxHeight=500, optionHeight=25),
        html.P("Time Range"),
        dcc.DatePickerRange(id='datetime-range-picker', initial_visible_month=df.datetime.max()),
        html.P("Sender"),
        dcc.Dropdown(df.sender.unique(), id='sender-selection', multi=True),
        html.P("Receiver"),
        dcc.Dropdown(df.receiver.unique(), id='receiver-selection', multi=True),
    ],
    style=SIDEBAR_STYLE,
    width=3,
)


@callback(
    Output('table-total-stats', 'data'),
    Input('chat-selection', 'value'),
    Input('datetime-range-picker', 'start_date'),
    Input('datetime-range-picker', 'end_date'),
    Input('sender-selection', 'value'),
    Input('receiver-selection', 'value'),
)
def update_chat_metrics(list_chats, dt_start, dt_end, list_sender, list_receiver):
    dff = df
    if list_chats:
        dff = dff[dff.chat.isin(list_chats)]
    if dt_start:
        dff = dff[dff.datetime > dt_start]
    if dt_end:
        dff = dff[dff.datetime < dt_end]
    if list_sender:
        dff = dff[dff.sender.isin(list_sender)]
    if list_receiver:
        dff = dff[dff.receiver.isin(list_receiver)]
    chat_metrics = agg_chat_metrics(dff.groupby(['sender', 'receiver'])).reset_index()

    timedelta_cols = list(chat_metrics.select_dtypes(include=['timedelta64']).columns)
    for col in timedelta_cols:
        chat_metrics[col] = chat_metrics[col].apply(timedelta_to_str)

    return chat_metrics.to_dict('records')


@callback(
    Output('graph-hourly-barpolar', 'figure'),
    Input('chat-selection', 'value'),
    Input('datetime-range-picker', 'start_date'),
    Input('datetime-range-picker', 'end_date'),
    Input('sender-selection', 'value'),
    Input('receiver-selection', 'value'),
)
def update_barpolar_graph(list_chats, dt_start, dt_end, list_sender, list_receiver):
    dff = df
    if list_chats:
        dff = dff[dff.chat.isin(list_chats)]
    if dt_start:
        dff = dff[dff.datetime > dt_start]
    if dt_end:
        dff = dff[dff.datetime < dt_end]
    if list_sender:
        dff = dff[dff.sender.isin(list_sender)]
    if list_receiver:
        dff = dff[dff.receiver.isin(list_receiver)]
    hour_stats = hourly_statistics(dff)
    return create_fig_hourly_barpolar(hour_stats)


@callback(
    Output('graph-time-to-reply-per-day', 'figure'),
    Input('chat-selection', 'value'),
    Input('datetime-range-picker', 'start_date'),
    Input('datetime-range-picker', 'end_date'),
    Input('sender-selection', 'value'),
    Input('receiver-selection', 'value'),
)
def update_time_to_reply_per_day_graph(list_chats, dt_start, dt_end, list_sender, list_receiver):
    dff = df
    if list_chats:
        dff = dff[dff.chat.isin(list_chats)]
    if dt_start:
        dff = dff[dff.datetime > dt_start]
    if dt_end:
        dff = dff[dff.datetime < dt_end]
    if list_sender:
        dff = dff[dff.sender.isin(list_sender)]
    if list_receiver:
        dff = dff[dff.receiver.isin(list_receiver)]
    return fig_time_to_reply_per_weekday(dff)