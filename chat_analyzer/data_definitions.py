from datetime import datetime

import pandera as pa
from numpy import timedelta64


class RawChat(pa.DataFrameModel):
    datetime: datetime
    sender: str
    message: str
    receiver: str = pa.Field(nullable=True)  # unresolved for group chats


class CombinedChat(RawChat):
    """Aggregate multiple messages from the same person to one block"""
    datetime: datetime = pa.Field(description='Datetime of the first or only message that got grouped.')
    datetime_last: datetime = pa.Field(
        description='Datetime of the last aggregated message that was received',
        nullable=True)
    n_block: int = pa.Field(description='Amount of consecutive messages from one person that got grouped.')
    block_duration: timedelta64 = pa.Field(
        description='Time passed between the aggregated, consecutive messages.',
        nullable=True)


class ChatFeatures(CombinedChat):
    week: str  # Year-Week
    n_symbols: int
    duration_since_their_last: timedelta64 = pa.Field(
        description='Duration since the recipient texted at the time of the message')
    duration_to_reply: timedelta64 = pa.Field(
        description='The duration it took to reply, iff the message is the first reply.',
        nullable=True)
