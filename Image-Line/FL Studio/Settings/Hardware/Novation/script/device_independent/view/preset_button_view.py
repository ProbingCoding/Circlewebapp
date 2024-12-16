from script.actions import PresetChangedAction
from script.colours import Colours
from script.constants import PluginsWithExplicitlyDisabledPresetNavigation
from script.fl_constants import RefreshFlags
from script.device_independent.util_view.view import View


class PresetButtonView(View):

    def __init__(self, action_dispatcher, button_led_writer, fl, product_defs):
        super().__init__(action_dispatcher)
        self.button_led_writer = button_led_writer
        self.fl = fl
        self.product_defs = product_defs

    @property
    def preset_navigation_available(self):
        return self.fl.channel_preset_count() > 1 and self.fl.get_instrument_plugin() not in PluginsWithExplicitlyDisabledPresetNavigation

    def _on_show(self):
        self._update_button_leds()

    def _on_hide(self):
        self._turn_off_button_leds()

    def _update_button_leds(self):
        colour = Colours.available if self.preset_navigation_available else Colours.off
        self.button_led_writer.set_button_colour(self.product_defs.FunctionToButton.get("SelectPreviousPreset"), colour)
        self.button_led_writer.set_button_colour(self.product_defs.FunctionToButton.get("SelectNextPreset"), colour)

    def _turn_off_button_leds(self):
        self.button_led_writer.set_button_colour(self.product_defs.FunctionToButton.get("SelectPreviousPreset"),
                                                 Colours.off)
        self.button_led_writer.set_button_colour(self.product_defs.FunctionToButton.get("SelectNextPreset"),
                                                 Colours.off)

    def handle_OnRefreshAction(self, action):
        if action.flags & RefreshFlags.ChannelSelection.value or action.flags & RefreshFlags.ChannelGroup.value:
            self._update_button_leds()

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get(
                "SelectPreviousPreset") and self.preset_navigation_available:
            self.button_led_writer.set_button_colour(action.button, Colours.button_pressed)
            self.fl.channel_select_previous_preset()
            self.action_dispatcher.dispatch(PresetChangedAction())

        if action.button == self.product_defs.FunctionToButton.get(
                "SelectNextPreset") and self.preset_navigation_available:
            self.button_led_writer.set_button_colour(action.button, Colours.button_pressed)
            self.fl.channel_select_next_preset()
            self.action_dispatcher.dispatch(PresetChangedAction())

    def handle_ButtonReleasedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("SelectPreviousPreset"):
            self.button_led_writer.set_button_colour(action.button,
                                                     Colours.available if self.preset_navigation_available else Colours.off)

        if action.button == self.product_defs.FunctionToButton.get("SelectNextPreset"):
            self.button_led_writer.set_button_colour(action.button,
                                                     Colours.available if self.preset_navigation_available else Colours.off)
