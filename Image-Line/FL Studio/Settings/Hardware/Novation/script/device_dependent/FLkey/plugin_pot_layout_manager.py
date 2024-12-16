from script.constants import Pots
from script.device_independent.view import PluginParameterScreenView, PluginParameterView
from script.native_pot_parameters import native_plugin_parameters


class PluginPotLayoutManager:

    def __init__(self, action_dispatcher, fl, screen_writer):
        control_to_index = {Pots.FirstControlIndex.value + control: index for index, control in
                            enumerate(range(0, Pots.Num.value))}
        self.views = {
            PluginParameterView(action_dispatcher, fl, native_plugin_parameters, control_to_index=control_to_index),
            PluginParameterScreenView(action_dispatcher, fl, screen_writer, native_plugin_parameters)
        }

    def show(self):
        for view in self.views:
            view.show()

    def hide(self):
        for view in self.views:
            view.hide()

    def focus_windows(self):
        pass
