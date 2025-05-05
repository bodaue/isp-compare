from typing import Any

from httpx import Response


def check_response(
    response: Response, expected_status: int = 200, expected_detail: str | None = None
) -> dict[str, Any] | None:
    status = response.status_code

    assert status == expected_status, (
        f"Expected status code {expected_status}, got {response.status_code}, "
        f"response: {response.text}"
    )

    if expected_detail is not None:
        response_json = response.json()
        assert "detail" in response_json, (
            f"Expected 'detail' in response, got {response_json}"
        )
        assert expected_detail.lower() in response_json["detail"].lower(), (
            f"Expected detail to contain '{expected_detail}', got"
            f" '{response_json['detail']}'"
        )

    if response.status_code == 204:
        return None
    return response.json()
