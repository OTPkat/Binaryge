import json
from typing import Any, Dict, Optional

from google.cloud import secretmanager


def get_json_dict_from_secret_resource_id(
    secret_resource_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Assumes that the secret is stored as a dictionary
    """
    client_ = secretmanager.SecretManagerServiceClient()
    response = client_.access_secret_version(name=secret_resource_id)
    try:
        credentials = json.loads(response.payload.data.decode("UTF-8"))
    except json.decoder.JSONDecodeError as e:
        repr(e)
        print("Make sure to check if the secret format is good")
        raise e
    else:
        return credentials
