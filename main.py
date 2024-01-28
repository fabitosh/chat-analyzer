import pandas as pd

from chat_analyzer import PATH_WHATSAPP_MSG, PATH_SIGNAL_MSG, PATH_DIR_PROCESSED_PICKLES, \
    PATH_DIR_CHAT_HTML_VISUALIZATIONS
from chat_analyzer.data_processing.load import agg_to_pkl
from chat_analyzer.visualization.visualize import create_chat_html

if __name__ == '__main__':
    pkl_path = agg_to_pkl(PATH_WHATSAPP_MSG, PATH_SIGNAL_MSG, PATH_DIR_PROCESSED_PICKLES)
    print(f"Chats aggregated in pickle file at {pkl_path}")

    df = pd.read_pickle(pkl_path)
    for chat, df_chat in df.groupby("chat"):
        print(f"Creating chat visualization for {chat}")
        create_chat_html(df_chat=df_chat, chat=chat, path_html_output=PATH_DIR_CHAT_HTML_VISUALIZATIONS)
