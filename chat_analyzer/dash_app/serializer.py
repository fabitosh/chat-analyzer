import base64
from io import BytesIO
import pandas as pd


SerializedData = str


def serialize(df: pd.DataFrame) -> SerializedData:
    """Serializes the DataFrame to store in a dcc.Store component"""
    parquet_bytes = df.to_parquet(engine='pyarrow')  # can't natively be serialized to JSON
    return base64.b64encode(parquet_bytes).decode('utf-8')


def deserialize(serialized_data: SerializedData) -> pd.DataFrame:
    """Deserializes the dcc.Store component to a DataFrame"""
    parquet_bytes = base64.b64decode(serialized_data.encode('utf-8'))
    return pd.read_parquet(BytesIO(parquet_bytes), engine='pyarrow')