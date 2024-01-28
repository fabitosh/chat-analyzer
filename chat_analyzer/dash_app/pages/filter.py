from dash import html, register_page

register_page(
    __name__,
    name='Filter',
    top_nav=True,
    order=2
)


def layout():
    layout = html.Div([
        html.H1(
            [
                "Filter"
            ]
        )
    ])
    return layout