import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, page_container

from chat_analyzer.dash_app.navigation import create_navbar

app = Dash(__name__,
           title='chat-analyzer',
           use_pages=True,
           suppress_callback_exceptions=True,  # Callbacks depend on other callbacks
           external_stylesheets=[dbc.themes.ZEPHYR])

app.layout = dcc.Loading(  # <- Wrap App with Loading Component
    id='loading-page-content',
    children=[
        dcc.Store(id='df-store', storage_type='session'),
        html.Div(
            [
                create_navbar(),
                page_container,
            ],

        )
    ],
)

server = app.server

if __name__ == '__main__':
    app.run(debug=True)
