def cache_led_updates(func):
    """
    Decorator for functions that want to cache all
    led updates and consolidate them into one update
    at the end of the function call.

    Note: Instance of decorated function must have an `led_cache` attribute
          that implements the `start_caching_led_updates` and
          `stop_caching_led_updates` functions.
    """

    def wrapper_cache_led_updates(self, *args, **kwargs):
        self.led_cache.start_caching_led_updates()
        func(self, *args, **kwargs)
        self.led_cache.stop_caching_led_updates()

    return wrapper_cache_led_updates
