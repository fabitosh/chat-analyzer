import glob
import os

from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
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
    dcc.Dropdown(df.chat.unique(), id='chat-selection'),
    dcc.Graph(id='graph-hourly-barpolar')
])


@callback(
    Output('graph-hourly-barpolar', 'figure'),
    Input('chat-selection', 'value')
)
def update_graph(value):
    dff = df[df.chat == value]
    hour_stats = hourly_statistics(dff)
    return create_fig_hourly_barpolar(hour_stats)


if __name__ == '__main__':
    app.run(debug=True)
