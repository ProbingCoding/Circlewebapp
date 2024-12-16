from script.constants import Faders
from script.device_independent.view import MixerMasterVolumeView, MixerVolumeScreenView, MixerVolumeView


class VolumeFaderLayoutManager:

    def __init__(self, action_dispatcher, fl, screen_writer, model, fl_window_manager):
        self.fl_window_manager = fl_window_manager
        control_to_index = {Faders.FirstControlIndex.value + control: index for index, control in
                            enumerate(range(0, Faders.NumRegularFaders.value))}
        self.views = {
            MixerVolumeView(action_dispatcher, fl, model, control_to_index=control_to_index),
            MixerVolumeScreenView(action_dispatcher, screen_writer, fl),
            MixerMasterVolumeView(action_dispatcher, fl,
                                  control=Faders.FirstControlIndex.value + Faders.MasterFaderIndex.value)
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
