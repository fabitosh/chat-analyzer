from dash import html, register_page

register_page(
    __name__,
    name='Upload',
    top_nav=True,
    order=1
)


def layout():
    layout = html.Div([
        html.H1(
            [
                "Upload"
            ]
        )
    ])
    return layout