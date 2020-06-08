import tkinter
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from travel_time.traveltime import TravelTime, main


@pytest.fixture(scope="function")
def traveltime():
    config = {
        "work_address": "123 Fake St",
        "home_address": "999 Test Ave",
        "google_api_key": "xxx",
        "work_start_hour": 9,
        "work_end_hour": 17,
    }

    with patch("travel_time.traveltime.requests.get") as mock, patch(
        "tkinter.Tk.mainloop"
    ):
        response_mock = MagicMock()
        response_mock.json.return_value = {
            "routes": [
                {
                    "legs": [
                        {
                            "duration": {"value": 60},
                            "duration_in_traffic": {"value": 120},
                        },
                    ]
                }
            ]
        }
        mock.return_value = response_mock
        yield TravelTime(tkinter.Tk(), 0, 0, config)


def get_time(hour, minute=0):
    return datetime(year=2020, month=12, day=1, hour=hour, minute=minute).timetuple()


#############
# Begin Tests
#############
def test_app_startup(traveltime):
    with patch("travel_time.traveltime.TravelTime") as mock:
        mock.return_value = traveltime
        main()


@patch("travel_time.traveltime.time.localtime")
def test_is_work_hours(time_mock, traveltime):
    time_mock.return_value = get_time(3)
    assert not traveltime.is_work_hours()
    time_mock.return_value = get_time(6)
    assert not traveltime.is_work_hours()
    time_mock.return_value = get_time(12)
    assert traveltime.is_work_hours()


def test_google_request(traveltime):
    expected, actual = traveltime.travel_time_google()
    assert expected == 60
    assert actual == 120


@patch("travel_time.traveltime.time.localtime")
def test_label_out_of_work_hours(time_mock, traveltime):
    time_mock.return_value = get_time(1)
    traveltime.update_label()
    traveltime.time = ""


@pytest.mark.parametrize(
    "duration,expected_text",
    [
        (7320, "2 hours 2 minutes"),
        (7260, "2 hours 1 minute"),
        (7200, "2 hours"),
        (3720, "1 hour 2 minutes"),
        (3660, "1 hour 1 minute"),
        (3600, "1 hour"),
        (120, "2 minutes"),
        (60, "1 minute"),
    ],
)
@patch("travel_time.traveltime.time.localtime")
def test_label_inside_work_hours(time_mock, traveltime, duration, expected_text):
    time_mock.return_value = get_time(10)
    with patch.object(traveltime, "travel_time_google", return_value=(1, duration)):
        traveltime.update_label()
        assert traveltime.time.get() == expected_text


@pytest.mark.parametrize(
    "duration,expected_color",
    [
        (200, "red"),
        (151, "red"),
        (150, "goldenrod"),
        (130, "goldenrod"),
        (121, "goldenrod"),
        (120, "forest green"),
        (110, "forest green"),
        (100, "forest green"),
        (80, "forest green"),
    ],
)
@patch("travel_time.traveltime.time.localtime")
def test_label_colors(time_mock, traveltime, duration, expected_color):
    time_mock.return_value = get_time(10)
    with patch.object(traveltime, "travel_time_google", return_value=(100, duration)):
        traveltime.update_label()
        assert traveltime.label_time.config()["foreground"][-1] == expected_color
