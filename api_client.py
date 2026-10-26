import json
import urllib.error
import urllib.request

from config import API_INFER_URL, API_TIMEOUT_SECONDS
from logger import log


def send_infer_request(payload: dict) -> dict:
    log(f"Sending request to API: {API_INFER_URL}")

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_INFER_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request, timeout=API_TIMEOUT_SECONDS
        ) as response:
            response_text = response.read().decode("utf-8")
        result = json.loads(response_text)
        log("API response received successfully")
        return result
    except urllib.error.HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            log(f"HTTPError from API: {error.code} {error.reason} - {error_body}")
        except Exception:
            log(f"HTTPError from API: {error.code} {error.reason}")
        raise
    except Exception as error:
        log(f"Error sending API request: {error}")
        raise
