"""Test the Looop Denki sensor platform."""

from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_integration


@pytest.fixture
def mock_api_data() -> dict[str, Any]:
    """Mock API data for testing."""
    return {
        "0": {  # Yesterday's data
            "price_data": [9.8, 11.2, 7.9, 14.5] * 12,  # 48 entries for 24 hours
            "level": [0, -0.5, 0, 0.5] * 12,
            "text": {
                str(i + 1): {
                    "price": (9.8, 11.2, 7.9, 14.5)[i % 4],
                    "level": (0, -0.5, 0, 0.5)[i % 4],
                }
                for i in range(48)
            },  # 1-based indexing
        },
        "1": {  # Today's data
            "price_data": [10.5, 12.3, 8.7, 15.2] * 12,  # 48 entries for 24 hours
            "level": [0, -0.5, 0, 0.5] * 12,
            "text": {
                str(i + 1): {
                    "price": (10.5, 12.3, 8.7, 15.2)[i % 4],
                    "level": (0, -0.5, 0, 0.5)[i % 4],
                }
                for i in range(48)
            },  # 1-based indexing
        },
        "2": {  # Tomorrow's data
            "price_data": [11.2, 13.1, 9.4, 16.0] * 12,
            "level": [0, -0.5, 0, 0.5] * 12,
            "text": {
                str(i + 1): {
                    "price": (11.2, 13.1, 9.4, 16.0)[i % 4],
                    "level": (0, -0.5, 0, 0.5)[i % 4],
                }
                for i in range(48)
            },  # 1-based indexing
        },
    }


async def test_sensor_setup(hass: HomeAssistant, mock_api_data: dict[str, Any]) -> None:
    """Test sensor setup."""
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value=mock_api_data,
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={"current_price": 12.3},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_next_price_info",
            return_value={"next_price": 13.1},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_tomorrow_forecast_info",
            return_value={"data_available": True, "tomorrow_average": 14.5},
        ),
    ):
        await setup_integration(hass)

    entity_registry = er.async_get(hass)

    # Test current price sensor
    current_entity = entity_registry.async_get("sensor.current_price")
    assert current_entity
    assert current_entity.unique_id == "looop_denki_03_current_price"

    # Test additional sensors exist
    next_entity = entity_registry.async_get("sensor.next_price")
    assert next_entity
    assert next_entity.unique_id == "looop_denki_03_next_price"

    tomorrow_avg_entity = entity_registry.async_get("sensor.tomorrow_average_price")
    assert tomorrow_avg_entity
    assert tomorrow_avg_entity.unique_id == "looop_denki_03_tomorrow_average"


async def test_sensor_state(hass: HomeAssistant, mock_api_data: dict[str, Any]) -> None:
    """Test sensor state."""
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value=mock_api_data,
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={
                "current_price": 12.3,
                "current_level": -0.5,
                "current_text": "Price: 12.3, Level: -0.5",
                "status": "でんき日和",
                "time_slot": 24,
                "hour": 12,
                "minute_range": "00-29",
            },
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_next_price_info",
            return_value={
                "next_price": 13.1,
                "next_status": "でんき注意報",
                "next_time_slot": 25,
            },
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_tomorrow_forecast_info",
            return_value={
                "data_available": True,
                "tomorrow_average": 14.5,
                "tomorrow_min": 8.7,
                "tomorrow_max": 20.2,
                "tomorrow_min_time": {"start": "03:00", "end": "03:29"},
                "tomorrow_max_time": {"start": "19:00", "end": "19:29"},
            },
        ),
    ):
        await setup_integration(hass)

    # Test current price sensor
    current_state = hass.states.get("sensor.current_price")
    assert current_state
    assert current_state.state == "12.3"
    assert current_state.attributes["current_level"] == -0.5
    assert current_state.attributes["current_text"] == "Price: 12.3, Level: -0.5"
    assert current_state.attributes["status"] == "でんき日和"
    assert current_state.attributes["time_slot"] == 24
    assert current_state.attributes["hour"] == 12
    assert current_state.attributes["minute_range"] == "00-29"

    # Test next price sensor
    next_state = hass.states.get("sensor.next_price")
    assert next_state
    assert next_state.state == "13.1"
    assert next_state.attributes["next_status"] == "でんき注意報"
    assert next_state.attributes["next_time_slot"] == 25

    # Test tomorrow average price sensor
    tomorrow_avg_state = hass.states.get("sensor.tomorrow_average_price")
    assert tomorrow_avg_state
    assert tomorrow_avg_state.state == "14.5"
    assert tomorrow_avg_state.attributes["data_available"] is True

    # Test tomorrow min price sensor
    tomorrow_min_state = hass.states.get("sensor.tomorrow_minimum_price")
    assert tomorrow_min_state
    assert tomorrow_min_state.state == "8.7"
    assert tomorrow_min_state.attributes["start"] == "03:00"
    assert tomorrow_min_state.attributes["end"] == "03:29"

    # Test tomorrow max price sensor
    tomorrow_max_state = hass.states.get("sensor.tomorrow_maximum_price")
    assert tomorrow_max_state
    assert tomorrow_max_state.state == "20.2"
    assert tomorrow_max_state.attributes["start"] == "19:00"
    assert tomorrow_max_state.attributes["end"] == "19:29"


async def test_sensor_unavailable_when_no_data(hass: HomeAssistant) -> None:
    """Test sensor is unavailable when no data is available."""
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_next_price_info",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_tomorrow_forecast_info",
            return_value={},
        ),
    ):
        await setup_integration(hass)

    # Current price sensor should be unavailable
    current_state = hass.states.get("sensor.current_price")
    assert current_state
    assert current_state.state == STATE_UNAVAILABLE

    # Next price sensor should be unavailable
    next_state = hass.states.get("sensor.next_price")
    assert next_state
    assert next_state.state == STATE_UNAVAILABLE

    # Tomorrow sensors should be unavailable
    tomorrow_avg_state = hass.states.get("sensor.tomorrow_average_price")
    assert tomorrow_avg_state
    assert tomorrow_avg_state.state == STATE_UNAVAILABLE


async def test_sensor_update_failure(hass: HomeAssistant) -> None:
    """Test sensor handles update failures gracefully."""
    with patch(
        "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
        side_effect=Exception("API Error"),
    ):
        config_entry = await setup_integration(hass)

    # When API fails during initial setup, the integration should be in
    # setup retry state
    assert config_entry.state == ConfigEntryState.SETUP_RETRY


async def test_today_stats_sensors(
    hass: HomeAssistant, mock_api_data: dict[str, Any]
) -> None:
    """Test today's average, min, max, and cheapest hours sensors."""
    with patch(
        "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
        return_value=mock_api_data,
    ):
        await setup_integration(hass)

    # Expected values from mock data: prices [10.5, 12.3, 8.7, 15.2] * 12
    # avg = (10.5+12.3+8.7+15.2)/4 = 11.675
    # min = 8.7, max = 15.2
    # threshold = 11.675 * 0.9 ≈ 10.51  → cheapest slots where price < 10.51 → only 8.7
    # cheapest slots (0-based): 2,6,10,14,18,22,26,30,34,38,42,46 → 12 slots

    today_avg_state = hass.states.get("sensor.today_average_price")
    assert today_avg_state is not None
    assert today_avg_state.state == "11.67"
    assert "all_prices" in today_avg_state.attributes
    assert len(today_avg_state.attributes["all_prices"]) == 48

    today_min_state = hass.states.get("sensor.today_minimum_price")
    assert today_min_state is not None
    assert today_min_state.state == "8.7"
    assert today_min_state.attributes["min_slot"] == 2
    assert today_min_state.attributes["min_time"] == "1:00~1:29"

    today_max_state = hass.states.get("sensor.today_maximum_price")
    assert today_max_state is not None
    assert today_max_state.state == "15.2"
    assert today_max_state.attributes["max_slot"] == 3
    assert today_max_state.attributes["max_time"] == "1:30~1:59"

    cheapest_state = hass.states.get("sensor.cheapest_hours_today")
    assert cheapest_state is not None
    assert cheapest_state.state == "12"
    attrs = cheapest_state.attributes
    assert attrs["cheapest_count"] == 12
    assert 2 in attrs["cheapest_slots"]
    assert "1:00~1:29" in attrs["cheapest_times"]
    assert attrs["avg_price"] == 11.67
    assert "std_dev" in attrs
    assert "price_range" in attrs
    assert attrs["price_range"] == 6.5


async def test_today_stats_sensors_unavailable_when_no_today_data(
    hass: HomeAssistant,
) -> None:
    """Test today sensors are unavailable when today's data (key '1') is absent."""
    api_data_without_today = {
        "0": {
            "price_data": [10.0] * 48,
            "level": [0] * 48,
            "text": {str(i + 1): {"price": 10.0, "level": 0} for i in range(48)},
        },
        # key "1" deliberately missing
    }
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value=api_data_without_today,
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_next_price_info",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_tomorrow_forecast_info",
            return_value={},
        ),
    ):
        await setup_integration(hass)

    for entity_id in (
        "sensor.today_average_price",
        "sensor.today_minimum_price",
        "sensor.today_maximum_price",
        "sensor.cheapest_hours_today",
    ):
        state = hass.states.get(entity_id)
        assert state is not None, f"{entity_id} not registered"
        assert state.state == STATE_UNAVAILABLE, f"{entity_id} should be unavailable"
