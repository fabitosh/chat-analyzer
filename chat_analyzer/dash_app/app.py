import glob
import os

from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd

from chat_analyzer import MY_CHAT_NAMES, PATH_DIR_PROCESSED_PICKLES
from chat_analyzer.analysis.analysis import hourly_statistics
from chat_analyzer.visualization.visualize import create_fig_hourly_barpolar

pkl_files = glob.glob('../../' + PATH_DIR_PROCESSED_PICKLES + '*.pkl')
latest_pkl_file = max(pkl_files, key=os.path.getctime)
df = pd.read_pickle(latest_pkl_file)

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children=f'chat-analyzer for {MY_CHAT_NAMES[0]}', style={'textAlign': 'center'}),
    html.H3(children=f'using {latest_pkl_file}', style={'textAlign': 'center'}),

    dcc.Dropdown(df.chat.unique(), id='chat-selection', multi=True, maxHeight=500, optionHeight=25),
    dcc.DatePickerRange(id='datetime-range-picker', initial_visible_month=df.datetime.max()),
    dcc.Dropdown(df.sender.unique(), id='sender-selection', multi=True),
    dcc.Dropdown(df.receiver.unique(), id='receiver-selection', multi=True),

    dcc.Graph(id='graph-hourly-barpolar'),
    html.Div(id='output-container-date-picker-range')
])


@callback(
    Output('graph-hourly-barpolar', 'figure'),
    Input('chat-selection', 'value'),
    Input('datetime-range-picker', 'start_date'),
    Input('datetime-range-picker', 'end_date'),
    Input('sender-selection', 'value'),
    Input('receiver-selection', 'value'),
)
def update_graph(list_chats, dt_start, dt_end, list_sender, list_receiver):
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
    Output('output-container-date-picker-range', 'children'),
    Input('datetime-range-picker', 'start_date'),
    Input('datetime-range-picker', 'end_date'))
def update_output(start_date, end_date):
    if not start_date and not end_date:
        return 'Select a date to see it displayed here'

    return f"{start_date=}, {end_date=}"


if __name__ == '__main__':
    app.run(debug=True)
