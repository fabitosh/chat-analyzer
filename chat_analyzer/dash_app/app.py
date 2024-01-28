import glob
import os

from dash import Dash, html, dcc, callback, Output, Input, dash_table, page_container
import dash_bootstrap_components as dbc
import pandas as pd

from chat_analyzer import MY_CHAT_NAMES, PATH_DIR_PROCESSED_PICKLES
from chat_analyzer.analysis.analysis import hourly_statistics, agg_chat_metrics
from chat_analyzer.dash_app.navigation import create_navbar
from chat_analyzer.visualization.visualize import create_fig_hourly_barpolar, timedelta_to_str, \
    fig_time_to_reply_per_weekday




app = Dash(__name__,
           title='chat-analyzer',
           use_pages=True,
           external_stylesheets=[dbc.themes.ZEPHYR])


app.layout = dcc.Loading(  # <- Wrap App with Loading Component
    id='loading_page_content',
    children=[
        html.Div(
            [
                create_navbar(),
                page_container
            ]
        )
    ],
)

server = app.server

if __name__ == '__main__':
    app.run(debug=True)
