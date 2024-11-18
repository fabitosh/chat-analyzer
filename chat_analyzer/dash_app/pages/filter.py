from datetime import datetime

import dash_ag_grid as dag
import pandas as pd
from dash import html, register_page, callback, Output, Input, dcc

from chat_analyzer.dash_app.serializer import deserialize, SerializedData

register_page(
    __name__,
    name='Filter',
    top_nav=True,
    order=2
)


def layout():
    layout = html.Div([
        html.H1(["Filter"]),
        dcc.DatePickerRange(id='datetime-range-picker'),
        html.Div(id='ag-grid-container'),
    ])
    return layout


@callback(
    Output('ag-grid-container', 'children'),
    Output('datetime-range-picker', 'min_date_allowed'),
    Output('datetime-range-picker', 'max_date_allowed'),
    Output('datetime-range-picker', 'initial_visible_month'),
    Input('df-raw', 'data')
)
def display_grid(data: SerializedData):
    print("Displaying grid")
    if data is not None:
        df: pd.DataFrame = deserialize(data)
        dt_min: datetime = df['datetime'].min()
        dt_max: datetime = df['datetime'].max()
        grid = dag.AgGrid(
            id='my-grid',
            columnDefs=[{"field": i} for i in df.columns if i not in ["block_duration", "chat", "receiver"]],
            rowData=df.to_dict('records'),
            defaultColDef={
                "filter": True,
                "sortable": True,
                "resizable": True
            },
            style={"height": 1200, "width": "100%"}
        )
        return grid, dt_min, dt_max, dt_max
    return html.Div("No data to display"), None, None, None

