"""Test the Looop Denki binary sensor platform."""

from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_integration


@pytest.fixture
def mock_api_data() -> dict[str, Any]:
    """Mock API data for binary sensor testing."""
    return {
        "0": {
            "price_data": [9.8, 11.2, 7.9, 14.5] * 12,
            "level": [0, -0.5, 0, 0.5] * 12,
            "text": {
                str(i + 1): {
                    "price": (9.8, 11.2, 7.9, 14.5)[i % 4],
                    "level": (0, -0.5, 0, 0.5)[i % 4],
                }
                for i in range(48)
            },
        },
        "1": {
            "price_data": [10.5, 12.3, 8.7, 15.2] * 12,
            "level": [0, -0.5, 0, 0.5] * 12,
            "text": {
                str(i + 1): {
                    "price": (10.5, 12.3, 8.7, 15.2)[i % 4],
                    "level": (0, -0.5, 0, 0.5)[i % 4],
                }
                for i in range(48)
            },
        },
        "2": {
            "price_data": [11.2, 13.1, 9.4, 16.0] * 12,
            "level": [0, -0.5, 0, 0.5] * 12,
            "text": {
                str(i + 1): {
                    "price": (11.2, 13.1, 9.4, 16.0)[i % 4],
                    "level": (0, -0.5, 0, 0.5)[i % 4],
                }
                for i in range(48)
            },
        },
    }


async def test_binary_sensor_setup(
    hass: HomeAssistant, mock_api_data: dict[str, Any]
) -> None:
    """Test that binary sensor entities are created with correct unique IDs."""
    with patch(
        "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
        return_value=mock_api_data,
    ):
        await setup_integration(hass)

    entity_registry = er.async_get(hass)

    cheap_entity = entity_registry.async_get("binary_sensor.cheap_now")
    assert cheap_entity is not None
    assert cheap_entity.unique_id == "looop_denki_03_cheap_now"

    alert_entity = entity_registry.async_get("binary_sensor.price_alert")
    assert alert_entity is not None
    assert alert_entity.unique_id == "looop_denki_03_price_alert"


async def test_cheap_now_on_when_status_is_good(hass: HomeAssistant) -> None:
    """Test cheap_now is ON when current price status is でんき日和."""
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={
                "current_price": 8.7,
                "current_level": -0.5,
                "status": "でんき日和",
            },
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

    state = hass.states.get("binary_sensor.cheap_now")
    assert state is not None
    assert state.state == STATE_ON
    assert state.attributes["status"] == "でんき日和"
    assert state.attributes["current_level"] == -0.5


async def test_cheap_now_off_when_status_is_normal(hass: HomeAssistant) -> None:
    """Test cheap_now is OFF when current price status is 通常."""
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={
                "current_price": 15.0,
                "current_level": 0,
                "status": "通常",
            },
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

    state = hass.states.get("binary_sensor.cheap_now")
    assert state is not None
    assert state.state == STATE_OFF


async def test_price_alert_on_when_status_is_warning(hass: HomeAssistant) -> None:
    """Test price_alert is ON when current price status is でんき注意報."""
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={
                "current_price": 28.0,
                "current_level": 0.5,
                "status": "でんき注意報",
            },
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

    state = hass.states.get("binary_sensor.price_alert")
    assert state is not None
    assert state.state == STATE_ON
    assert state.attributes["status"] == "でんき注意報"


async def test_price_alert_on_when_status_is_critical(hass: HomeAssistant) -> None:
    """Test price_alert is ON when current price status is でんき警報."""
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={
                "current_price": 120.0,
                "current_level": 1.0,
                "status": "でんき警報",
            },
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

    state = hass.states.get("binary_sensor.price_alert")
    assert state is not None
    assert state.state == STATE_ON
    assert state.attributes["status"] == "でんき警報"


async def test_price_alert_off_when_status_is_good(hass: HomeAssistant) -> None:
    """Test price_alert is OFF when current price status is でんき日和."""
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={
                "current_price": 8.0,
                "current_level": -0.5,
                "status": "でんき日和",
            },
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

    state = hass.states.get("binary_sensor.price_alert")
    assert state is not None
    assert state.state == STATE_OFF


async def test_binary_sensors_unavailable_when_no_current_info(
    hass: HomeAssistant,
) -> None:
    """Test binary sensors are unavailable when current_info is empty."""
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

    for entity_id in ("binary_sensor.cheap_now", "binary_sensor.price_alert"):
        state = hass.states.get(entity_id)
        assert state is not None, f"{entity_id} not registered"
        assert state.state == STATE_UNAVAILABLE, f"{entity_id} should be unavailable"


async def test_cheap_now_falls_back_to_level_when_no_status(
    hass: HomeAssistant,
) -> None:
    """Test cheap_now uses current_level as fallback when status is absent."""
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={"current_price": 9.0, "current_level": -0.5},
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

    state = hass.states.get("binary_sensor.cheap_now")
    assert state is not None
    assert state.state == STATE_ON


async def test_price_alert_falls_back_to_level_when_no_status(
    hass: HomeAssistant,
) -> None:
    """Test price_alert uses current_level as fallback when status is absent."""
    with (
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.async_get_prices",
            return_value={},
        ),
        patch(
            "custom_components.looop_denki.api.LooopDenkiApiClient.get_current_price_info",
            return_value={"current_price": 28.0, "current_level": 0.5},
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

    state = hass.states.get("binary_sensor.price_alert")
    assert state is not None
    assert state.state == STATE_ON
