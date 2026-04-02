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
ATTR_CURRENT_START_TIME = "current_start_time"
ATTR_CURRENT_END_TIME = "current_end_time"

# Sensor attributes – next price
ATTR_NEXT_START_TIME = "next_start_time"
ATTR_NEXT_END_TIME = "next_end_time"

# Sensor attributes – today stats
ATTR_TODAY_ALL_PRICES = "all_prices"
ATTR_TODAY_MIN_SLOT = "min_slot"
ATTR_TODAY_MIN_TIME = "min_time"
ATTR_TODAY_MIN_TIME_START = "min_time_start"
ATTR_TODAY_MIN_TIME_END = "min_time_end"
ATTR_TODAY_MAX_SLOT = "max_slot"
ATTR_TODAY_MAX_TIME = "max_time"
ATTR_TODAY_MAX_TIME_START = "max_time_start"
ATTR_TODAY_MAX_TIME_END = "max_time_end"

# Sensor attributes – tomorrow stats start/end times
ATTR_TOMORROW_MIN_TIME_START = "tomorrow_min_time_start"
ATTR_TOMORROW_MIN_TIME_END = "tomorrow_min_time_end"
ATTR_TOMORROW_MAX_TIME_START = "tomorrow_max_time_start"
ATTR_TOMORROW_MAX_TIME_END = "tomorrow_max_time_end"

# Sensor attributes – cheapest hours today
ATTR_CHEAPEST_SLOTS = "cheapest_slots"
ATTR_CHEAPEST_TIMES = "cheapest_times"
ATTR_CHEAPEST_COUNT = "cheapest_count"
ATTR_CHEAPEST_THRESHOLD = "threshold_used"
ATTR_AVG_PRICE = "avg_price"
ATTR_MINUTES_UNTIL_NEXT_CHEAP = "minutes_until_next_cheap"
ATTR_STD_DEV = "std_dev"
ATTR_PRICE_RANGE = "price_range"

# Sensor attributes – expensive hours today
ATTR_EXPENSIVE_SLOTS = "expensive_slots"
ATTR_EXPENSIVE_TIMES = "expensive_times"
ATTR_EXPENSIVE_COUNT = "expensive_count"
ATTR_EXPENSIVE_THRESHOLD = "threshold_used"
ATTR_FIRST_EXPENSIVE_SLOT = "first_expensive_slot"
ATTR_FIRST_EXPENSIVE_TIME = "first_expensive_time"
