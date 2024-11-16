import sys

import pandas as pd
from chat_analyzer.dash_app.serializer import serialize, deserialize

def test_serialize_deserialize_does_not_change_df():

    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })

    serialized = serialize(df)
    deserialized = deserialize(serialized)

    assert df.equals(deserialized)


def test_serialize_deserialize_retains_dtypes():
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4.2, 5.1, 6.0],
        'C': ['cat', 'dog', 'mouse'],
        'D': ['red', 'blue', 'red']
    }).astype({'D': 'category'})

    serialized = serialize(df)
    deserialized = deserialize(serialized)

    assert df.equals(deserialized)


def test_serialization_compresses_better_than_to_json():
    n_rows = 500
    df = pd.DataFrame({
        'A': range(n_rows),
        'B': [1.1 * i for i in range(n_rows)],
        'C': ['red', 'blue'] + ['red'] * (n_rows - 2)
    }).astype({'C': 'category'})
    json_baseline_bytes = sys.getsizeof(df.to_json())

    serialized = serialize(df)
    size_serialized_bytes = sys.getsizeof(serialized)
    assert size_serialized_bytes < json_baseline_bytes
