import dash_ag_grid as dag
import pandas as pd
from dash import html, register_page, callback, Output, Input

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
        html.Div(id='ag-grid-container'),
    ])
    return layout


@callback(
    Output('ag-grid-container', 'children'),
    Input('df-store', 'data')
)
def display_grid(data: SerializedData):
    print("Displaying grid")
    if data is not None:
        df: pd.DataFrame = deserialize(data)
        grid = dag.AgGrid(
            id='my-grid',
            columnDefs=[{"field": i} for i in df.columns],
            rowData=df.to_dict('records'),
            defaultColDef={
                "filter": True,
                "sortable": True,
                "resizable": True
            },
        )
        return grid
