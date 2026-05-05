"""
Utility functions module.
"""

import json
import zlib
import base64


def b64zipstr2json(encoded_data):
    """
    Takes a Base64-encoded compressed JSON string and returns the original JSON data
    as a Python object.
    """
    # Step 1: Base64 decode
    compressed_data = base64.b64decode(encoded_data)

    # Step 2: Decompress the zlib data
    json_string = zlib.decompress(compressed_data).decode('utf-8')

    # Step 3: Parse the JSON string back to a Python object
    return json.loads(json_string)
