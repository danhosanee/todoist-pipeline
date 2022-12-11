import pytest
from datetime import datetime, timezone
from urllib.parse import urlparse
from todoist.get_completed import (
    create_headers,
    get_sync_url,
    request_string,
    get_request,
    date_offset,
    format_str,
    json_to_df,
    tz_to_utc
)


@pytest.fixture
def token():
    return "test123"


@pytest.fixture
def date_today():
    return datetime(2022, 12, 5)


@pytest.fixture
def tz():
    return "Australia/Mebourne"


def test_create_headers(token):
    headers = create_headers(token)
    assert headers == {
        "Authorization": "Bearer test123"
    }


def test_request_string(token):
    url = request_string("completed/get_all", token=token)
    assert urlparse(url).netloc == "api.todoist.com"
    assert urlparse(url).path == "/sync/v9/completed/get_all"
    assert urlparse(url).query == "&token=test123"


def test_date_offset(date_today):
    date = date_offset(date_today, week_num=-1, week_day=0)
    assert date == datetime(2022, 11, 28)


def test_format_str(date_today):
    date_str = format_str(date_today, "%Y-%m-%d")
    assert date_str == "2022-12-05"


