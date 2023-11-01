# Python Instant Messenger Analyser
The vision is to have a messenger independent platform to analyze yours chatting behaviour. The project is split into:
- `load`: parse the chat input from the various sources into a defined DataFrame
- `aggregate`: clean the data, aggregate consecutive messages, add features to each message
- `analyze`: aggregate and visualize relevant metrics

## Load
Every chat should be parsed into a `RawChat` DataFrame. If you are chatting to the same person through multiple messengers, the possibility to concat/combine two `RawChat` should be an option if desired.
### WhatsApp
Manually export every chat into a .txt file. Dump all those into a folder and set said path as `PATH_WHATSAPP_MSG`.

### Signal Messages
To be implemented
https://github.com/tbvdm/sigtop
