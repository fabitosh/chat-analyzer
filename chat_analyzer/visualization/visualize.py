import base64
import datetime
import os
from io import BytesIO
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from calplot import calplot

from chat_analyzer.analysis.analysis import agg_chat_metrics, n_messages_per_day, hourly_statistics
from chat_analyzer.utils.data_definitions import ChatFeatures

PRIMARY_COLOR = "#aaaaaa"
SECONDARY_COLOR = "#dddddd"


def create_chat_html(df_chat: ChatFeatures, chat: str, path_html_output: str):
    # Chat Overview Metrics
    chat_metrics = agg_chat_metrics(df_chat.groupby('sender'))
    html_chat_metrics = pretty_html(chat_metrics, caption=f"Chat Metrics for {chat}")

    # Calplot of messages
    mplfig, _ = calplot(n_messages_per_day(df_chat), cmap='YlGn')
    html_calplot = matplotlib_fig_to_html(mplfig)

    # Spider Charts Activity per Day
    hour_stats = hourly_statistics(df_chat)
    fig_hourly_barpolar = create_fig_hourly_barpolar(hour_stats)
    html_hourly_barpolar = fig_hourly_barpolar.to_html(full_html=False, include_plotlyjs='cdn')

    # Barplot time to reply by weekday
    fig_time_to_reply = fig_time_to_reply_per_weekday(df_chat)
    html_time_to_reply = fig_time_to_reply.to_html(full_html=False, include_plotlyjs='cdn')

    filename = f'Chat_Analysis_{chat.replace(" ", "_")}.html'
    filepath = os.path.join(path_html_output, filename)
    with open(filepath, 'w+') as f:
        f.write("<center>")
        f.write(html_chat_metrics)
        f.write(html_calplot)
        f.write(html_hourly_barpolar)
        f.write(html_time_to_reply)
        f.write("</center>")


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
    if pd.isna(td):
        return '-'
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


def matplotlib_fig_to_html(fig):
    tmpfile = BytesIO()
    fig.subplots_adjust(left=0.05)
    fig.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    html = '<img src=\'data:image/png;base64,{}\'>'.format(encoded)
    return html


def create_fig_hourly_barpolar(df) -> go.Figure:
    fig = go.Figure()
    for sender, dfp in df.groupby('sender'):
        customdata = pd.concat([
            dfp.hour,
            dfp.hour + 1 % 24,
            round(dfp.avg_symbols_per_message, 1),
            dfp.avg_time_to_reply.apply(timedelta_to_str)], axis=1)

        hourly_polar_bars = go.Barpolar(
            r=dfp.total_messages,
            theta=dfp.hour * 360 / 24 + 7.5,
            opacity=0.7,
            name=sender,
            customdata=customdata)

        fig.add_traces([hourly_polar_bars])

    n_hour_labels = 6
    fig.update_layout(
        polar={
            "angularaxis": {
                "tickmode": "array",
                "rotation": 90,
                "direction": 'clockwise',
                "tickvals": list(range(0, 360, 360 // n_hour_labels)),
                "ticktext": [f"{h:02}:00" for h in range(0, 24, 24 // n_hour_labels)],
                'showgrid': True,
            },
            'radialaxis': {
                'range': [0, df.total_messages.max()],
                'showgrid': True,
                'nticks': 6,
                'tickangle': 90,
                'showline': False,
            },
            'barmode': "overlay",
        },
        height=1000,
    )
    fig.update_traces(hovertemplate="<br>".join([
        "<b>%{customdata[0]}:00 - %{customdata[1]}:00</b>",
        "Messages: %{r}",
        "Avg. Symbols per Message: %{customdata[2]}",
        "Avg. Time to Reply: %{customdata[3]}",
    ]))
    return fig


def fig_time_to_reply_per_weekday(df) -> go.Figure:
    return px.box(df,
                  x='weekday',
                  y=df['duration_to_reply'].dt.total_seconds() / 60,
                  color='sender',
                  labels={'y': "Time to Reply [min]"},
                  log_y=True,
                  height=700,
                  category_orders={'weekday': df.weekday.cat.categories})
