import base64
import datetime
import io

import pandas as pd
from dash import html, register_page, dcc, dash_table, Output, Input, callback, State
import dash_bootstrap_components as dbc

from chat_analyzer.data_processing.load import load_whatsapp_chat

register_page(
    __name__,
    name='Upload',
    top_nav=True,
    order=1
)


def layout():
    layout = html.Div([
        dbc.Row(dbc.Col(html.Div("Upload your WhatsApp chat"))),
        dbc.Row(
            dbc.Col([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=False),
            ])),
        dbc.Row(dbc.Col(html.Div(id='output-data'))),
    ])
    return layout


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    chat_export: str = decoded.decode('utf-8')
    df = load_whatsapp_chat(chat_export)
    return df


@callback(Output('df-store', 'data'),
          Input('upload-data', 'contents'),
          State('upload-data', 'filename'),
          State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        df = parse_contents(list_of_contents, list_of_names, list_of_dates)
        print("Parsed Contents")
        return df.to_json(date_format='iso', orient='records')
