from script.constants import Pots
from script.device_independent.view import MixerBankHighlightView, MixerBankView, MixerPanScreenView, MixerPanView


class MixerPanPotLayoutManager:

    def __init__(self, action_dispatcher, button_led_writer, fl, screen_writer, product_defs, model, fl_window_manager):
        self.fl_window_manager = fl_window_manager
        control_to_index = {Pots.FirstControlIndex.value + control: index for index, control in
                            enumerate(range(0, Pots.Num.value))}
        self.views = {
            MixerBankView(action_dispatcher, button_led_writer, fl, product_defs, model),
            MixerBankHighlightView(action_dispatcher, fl, model),
            MixerPanView(action_dispatcher, fl, model, control_to_index=control_to_index),
            MixerPanScreenView(action_dispatcher, screen_writer, fl)
        }

    def show(self):
        for view in self.views:
            view.show()

    def hide(self):
        for view in self.views:
            view.hide()

    def focus_windows(self):
        self.fl_window_manager.hide_last_focused_plugin_window()
        self.fl_window_manager.focus_mixer_window()
