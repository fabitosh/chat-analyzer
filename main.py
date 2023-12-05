import pandas as pd
from calplot import calplot

from chat_analyzer import PATH_WHATSAPP_MSG, PATH_SIGNAL_MSG, PATH_DIR_PROCESSED_PICKLES
from chat_analyzer.analysis.analysis import n_messages_per_day, hourly_statistics, agg_chat_metrics
from chat_analyzer.data_processing.load import agg_to_pkl
from chat_analyzer.visualization.visualize import pretty_html, matplotlib_fig_to_html, create_fig_hourly_barpolar, \
    fig_time_to_reply_per_weekday

if __name__ == '__main__':
    pkl_path = agg_to_pkl(PATH_WHATSAPP_MSG, PATH_SIGNAL_MSG, PATH_DIR_PROCESSED_PICKLES)
    print(f"Chats aggregated in pickle file at {pkl_path}")

    df = pd.read_pickle(pkl_path)
    for chat, df_chat in df.groupby("chat"):
        print(chat)
        # Chat Overview Metrics®
        chat_metrics = agg_chat_metrics(df_chat.groupby('sender'))
        html_chat_metrics = pretty_html(chat_metrics, caption=f"Chat Metrics for {chat}")

        # Calplot of messages
        mplfig, _ = calplot(n_messages_per_day(df_chat), cmap='YlGn')
        html_calplot = matplotlib_fig_to_html(mplfig)

        # Spider Charts Activity per Day
        hour_stats = hourly_statistics(df_chat)
        fig_hourly_barpolar = create_fig_hourly_barpolar(hour_stats)
        html_hourly_barpolar = fig_hourly_barpolar.to_html(full_html=False, include_plotlyjs='cdn')

        # Plots
        fig_time_to_reply = fig_time_to_reply_per_weekday(df_chat)
        html_time_to_reply = fig_time_to_reply.to_html(full_html=False, include_plotlyjs='cdn')

        with open(f'data/visualized/Chat_Analysis_{chat.replace(" ", "_")}.html', 'w+') as f:
            f.write("<center>")
            f.write(html_chat_metrics)
            f.write(html_calplot)
            f.write(html_hourly_barpolar)
            f.write(html_time_to_reply)
            f.write("</center>")

