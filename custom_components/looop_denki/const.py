"""Constants for the Looop Denki integration."""

DOMAIN = "looop_denki"

# Configuration
CONF_AREA_CODE = "area_code"

# Update intervals
UPDATE_INTERVAL_SECONDS = 300  # 5 minutes

# Sensor attributes – current price
ATTR_CURRENT_LEVEL = "current_level"
ATTR_CURRENT_TEXT = "current_text"
ATTR_STATUS = "status"
ATTR_TIME_SLOT = "time_slot"
ATTR_HOUR = "hour"
ATTR_MINUTE_RANGE = "minute_range"

# Sensor attributes – today stats
ATTR_TODAY_ALL_PRICES = "all_prices"
ATTR_TODAY_MIN_SLOT = "min_slot"
ATTR_TODAY_MIN_TIME = "min_time"
ATTR_TODAY_MAX_SLOT = "max_slot"
ATTR_TODAY_MAX_TIME = "max_time"

# Sensor attributes – cheapest hours today
ATTR_CHEAPEST_SLOTS = "cheapest_slots"
ATTR_CHEAPEST_TIMES = "cheapest_times"
ATTR_CHEAPEST_COUNT = "cheapest_count"
ATTR_CHEAPEST_THRESHOLD = "threshold_used"
ATTR_AVG_PRICE = "avg_price"
ATTR_MINUTES_UNTIL_NEXT_CHEAP = "minutes_until_next_cheap"
ATTR_STD_DEV = "std_dev"
ATTR_PRICE_RANGE = "price_range"
