# Python Instant Messenger Analyser
Analyze your instant messaging behaviour. Exported WhatsApp Chat .txt files are parsed into a pandas dataframe, which is also enriched by feature columns.


# Getting started
## Installation
1. Install [poetry](https://python-poetry.org/), if not already installed.
2. `git clone https://github.com/fabitosh/chat-analyzer.git`
3. `cd chat-analyzer`
4. Install project dependencies `poetry install`
5. [Export your WhatsApp Chats](#WhatsApp).
6. Configure `chat_analyzer/__init__.py` to your needs. I work with a gitignored `data/` folder within the project.
7. Run `main.py`
8. View basic chat analysis in `data/visualiyed/` for each chat as html files. A dash application is wip.

## Structure
```
main.py
chat_analyzer
├── __init__.py                     # Configuration
├── analysis
│   ├── __init__.py
│   └── analysis.py                 # Module for conducting analysis on chat data
│
├── data_processing
│   ├── __init__.py
│   └── load.py
│       ├── extract.py              # Module for parsing raw chats and merging consecutive messages
│       └── feature_engineering.py  # Define feature columns
│
├── utils
│   ├── __init__.py
│   └── data_definitions.py
│
├── visualization
│   ├── __init__.py
│   └── visualize.py
│
├── data
│   ├── raw                         # Raw chat exports
│   ├── processed                   # Parsed and enriched entire dataframes as pickle.
│   └── visualized                  # Basic chat visualization html files
│
├── notebooks                       # Explaratory notebooks can go here.
└── tests
```

# Thoughts and Notes
## Load
Every chat should be parsed into a `RawChat` DataFrame. If you are chatting to the same person through multiple messengers, the possibility to concat/combine two `RawChat` should be an option if desired.

### WhatsApp
Manually export every chat into a .txt file. As of this writing, this was only possible from the phone. Dump all chats of interest into a folder and set said path as `PATH_WHATSAPP_MSG` .

### Signal Messages
Parsing is still to be implemented.
https://github.com/tbvdm/sigtop


## Analysis 
Analysis can happen on multiple layers:
- Analysis which every message/row has.
  - Statistics derived in the context of the chat should be included in `analysis.extract_single_chat_features()`. Example: Time it took to reply
  - Metrics that only need the row for context are put to `analysis.add_features()`. Example: Number of message symbols
- Analysis of one chat behaviour:
- Analysis of the sender's instant messengers as whole
