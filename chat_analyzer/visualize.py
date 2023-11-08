import datetime
from typing import Dict, Optional

import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

PRIMARY_COLOR = "#aaaaaa"
SECONDARY_COLOR = "#dddddd"


def hover(hover_color=SECONDARY_COLOR):
    return dict(selector="tbody tr:hover",
                props=[("background-color", "%s" % hover_color)])


def set_table_style_css(styler):
    """
    From https://stackoverflow.com/a/49687866/2007153
    Get a Jupyter like html of pandas dataframe
    """

    styles = [
        # table properties
        dict(selector=" ",
             props=[("margin", "20"),
                    # ("width", "100%"),
                    ("font-family", '"Helvetica", "Arial", sans-serif'),
                    ("border-collapse", "collapse"),
                    # ("border", "1px"),
                    ("border", f"2px solid {PRIMARY_COLOR}"),
                    ("text-align", "center")
                    ]),

        # header color - optional
        dict(selector="thead",
             props=[("background-color", PRIMARY_COLOR)
                    ]),

        # background shading
        dict(selector="tbody tr:nth-child(even)",
             props=[("background-color", "#fff")]),
        dict(selector="tbody tr:nth-child(odd)",
             props=[("background-color", "#eee")]),

        # cell spacing
        dict(selector="td",
             props=[("padding", ".5em")]),

        # header cell properties
        dict(selector="th",
             props=[("font-size", "100%"),
                    ("padding", '10px'),
                    ("text-align", "center")]),

        # caption placement
        dict(selector="caption",
             props=[("caption-side", "bottom"),
                    ('color', PRIMARY_COLOR),
                    ('padding', '0.5em')]),

        # render hover last to override background-color
        hover()]
    return styler.set_table_styles(styles)


def timedelta_to_str(td: datetime.timedelta):
    s = td.total_seconds()
    h = 3600
    return f'{int(s / h)}:{int(s % h / 60):02d}:{int(s % 60):02d}'


def pretty_html(df, caption: str, path=None) -> Optional[str]:
    timedelta_cols = list(df.select_dtypes(include=['timedelta64']).columns)
    for col in timedelta_cols:
        df[col] = df[col].apply(timedelta_to_str)

    df = (df.style
          .pipe(set_table_style_css)
          .format_index(lambda x: x.replace('_', ' ').title(), axis=1)
          .format(precision=1, thousands="'", decimal='.')
          .set_caption(caption))

    if path is None:
        return df.to_html()

    df.to_html(path)

