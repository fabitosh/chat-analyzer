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
        dbc.Row(dbc.Col(html.Div(id='output-data-upload'))),
    ])
    return layout


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        chat_export: str = decoded.decode('utf-8')
        df = load_whatsapp_chat(chat_export)
    except Exception as e:
        print(e)
        return html.Div([f'There was an error processing this file of type {content_type}.'])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.iloc[:20].to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),
    ])


@callback(Output('output-data-upload', 'children'),
          Input('upload-data', 'contents'),
          State('upload-data', 'filename'),
          State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [parse_contents(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        return children
