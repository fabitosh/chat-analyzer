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


class Chat(CombinedChat):
    week: str  # Year-Week
    n_symbols: int
