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


def test_app_startup(traveltime):
    with patch("travel_time.traveltime.TravelTime") as mock:
        mock.return_value = traveltime
        main()


@patch("travel_time.traveltime.time.localtime")
def test_is_work_hours(time_mock, traveltime):
    time_mock.return_value = datetime(year=2020, month=12, day=1, hour=3).timetuple()
    assert not traveltime.is_work_hours()
    time_mock.return_value = datetime(year=2020, month=12, day=1, hour=6).timetuple()
    assert not traveltime.is_work_hours()
    time_mock.return_value = datetime(year=2020, month=12, day=1, hour=12).timetuple()
    assert traveltime.is_work_hours()


def test_google_request(traveltime):
    expected, actual = traveltime.travel_time_google()
    assert expected == 60
    assert actual == 120


@patch("travel_time.traveltime.time.localtime")
def test_label_out_of_work_hours(time_mock, traveltime):
    time_mock.return_value = datetime(year=2020, month=12, day=1, hour=1).timetuple()
    traveltime.update_label()
    traveltime.time = ""


@patch("travel_time.traveltime.time.localtime")
def test_label_inside_work_hours(time_mock, traveltime):
    time_mock.return_value = datetime(year=2020, month=12, day=1, hour=10).timetuple()
    traveltime.update_label()
    traveltime.time = "2 mins"
