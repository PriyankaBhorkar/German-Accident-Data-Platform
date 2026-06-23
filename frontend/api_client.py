from __future__ import annotations

from typing import Any

import requests


BASE_URL = "http://127.0.0.1:8000"


def get_json(
    endpoint: str,
    params: dict[str, Any] | None = None
) -> tuple[Any | None, str | None]:
    """
    Send a GET request to the FastAPI backend.

    Returns:
        tuple:
            response data or None,
            error message or None
    """

    url = f"{BASE_URL}{endpoint}"

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 404:
            try:
                message = response.json().get(
                    "detail",
                    "No matching data was found."
                )
            except ValueError:
                message = "No matching data was found."

            return None, message

        if response.status_code == 422:
            try:
                detail = response.json().get(
                    "detail",
                    "The request parameters are invalid."
                )
            except ValueError:
                detail = "The request parameters are invalid."

            return None, str(detail)

        response.raise_for_status()

        return response.json(), None

    except requests.exceptions.ConnectionError:
        return (
            None,
            "The FastAPI backend is not available. "
            "Start it on http://127.0.0.1:8000."
        )

    except requests.exceptions.Timeout:
        return None, "The API request timed out."

    except requests.exceptions.HTTPError as exc:
        return None, f"API request failed: {exc}"

    except requests.exceptions.RequestException as exc:
        return None, f"Unable to contact the API: {exc}"

    except ValueError:
        return None, "The API returned an invalid JSON response."