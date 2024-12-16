from script.colours import Colours
from script.constants import LedLightingType, SysEx


class KeyboardControllerLedWriter:

    def __init__(self, sender, product_defs):
        self.sender = sender
        self.product_defs = product_defs
        self.sysex_led_update_header = SysEx.MessageHeader.value + [product_defs.Constants.NovationProductId.value,
                                                                    0x01]
        self.shift_pressed = False
        self._shift_button_led_states = {}
        self._button_led_states = {}
        self._cached_led_updates = {}
        self._caching = False
        self.gamma = 2.25
        self._initialise_button_led_states()

    @staticmethod
    def brightness(r, g, b):
        return max(max(r, g, ), b)

    def _initialise_button_led_states(self):
        self._caching = True
        for button in self.product_defs.ButtonToLedIndex.keys():
            self.set_button_colour(button, Colours.off)
            self._cached_led_updates = {}
        self._caching = False

    def set_pad_colour(self, pad, colour: (Colours.EnumItem, int, tuple)):
        if pad is None:
            return

        if isinstance(colour, Colours.EnumItem):
            colour = colour.value

        target = self.product_defs.Constants.LightingTargetNote.value

        if isinstance(colour, int):
            self._cached_led_updates[(target, pad)] = (target | self.product_defs.Constants.LightingTypeStatic.value,
                                                       pad, colour)
        elif isinstance(colour, tuple):
            self._cached_led_updates[(target, pad)] = (target | self.product_defs.Constants.LightingTypeRGB.value,
                                                       pad, *self.apply_gamma_correction(self.gamma, *colour))

        if not self._caching:
            self._send_cached_led_updates()

    def apply_gamma_correction(self, gamma, red, green, blue):

        # Calculate the brightness before correction
        brightness_before = self.brightness(red, green, blue)

        # Apply gamma correction
        red = 128 * ((red / 128) ** gamma)
        green = 128 * ((green / 128) ** gamma)
        blue = 128 * ((blue / 128) ** gamma)

        # Calculate brightness after correction
        brightness_after = self.brightness(red, green, blue)
        brightness_correction_factor = brightness_before / brightness_after
        # Bring colour back to original brightness
        red = red * brightness_correction_factor
        green = green * brightness_correction_factor
        blue = blue * brightness_correction_factor

        return int(round(red)), int(round(green)), int(round(blue))

    def set_button_colour(self, button, colour, *, lighting_type=LedLightingType.Static):
        led_index = self.product_defs.ButtonToLedIndex.get(button)
        if led_index is None:
            return

        target = self.product_defs.Constants.LightingTargetCC.value
        if lighting_type == LedLightingType.Pulsing:
            type_static = self.product_defs.Constants.LightingTypePulsing.value
        else:
            type_static = self.product_defs.Constants.LightingTypeStatic.value

        led_update = (target | type_static, led_index, int(colour))

        shift_pressed = self.shift_pressed
        is_shift_button = self.product_defs.IsShiftButton(button)
        if self.product_defs.ForwardButtonLedGivenShift(button, shift_pressed):
            self._cached_led_updates[(target, led_index)] = led_update

        if is_shift_button:
            self._shift_button_led_states[(target, led_index)] = led_update
        else:
            self._button_led_states[(target, led_index)] = led_update

        if not self._caching:
            self._send_cached_led_updates()

    def start_caching_led_updates(self):
        self._caching = True

    def stop_caching_led_updates(self):
        self._caching = False
        self._send_cached_led_updates()

    def _send_cached_led_updates(self):
        if not self._cached_led_updates:
            return

        message = self.sysex_led_update_header.copy()
        for led_update in self._cached_led_updates.values():
            message.extend([*led_update])

        self._cached_led_updates.clear()
        self.sender.send_sysex(message)

    def shift_modifier_pressed(self):
        self.shift_pressed = True
        self._cached_led_updates.update(self._shift_button_led_states)

    def shift_modifier_released(self):
        self.shift_pressed = False
        self._cached_led_updates.update(self._button_led_states)
