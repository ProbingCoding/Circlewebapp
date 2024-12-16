from script.device_independent.util_view.view import View
from script.actions import MixerTrackVolumeChangedAction
from util.deadzone_value_converter import DeadzoneValueConverter


class MixerMasterVolumeView(View):
    track_for_master_volume = 0

    def __init__(self, action_dispatcher, fl, *, control):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.control = control
        self.deadzone_value_converter = DeadzoneValueConverter(max=1.0, centre=0.8, width=0.05)
        self.reset_pickup_on_first_movement = False

    def _on_show(self):
        self.reset_pickup_on_first_movement = True

    def handle_ControlChangedAction(self, action):
        if action.control != self.control:
            return

        if self.reset_pickup_on_first_movement:
            self.reset_pickup_on_first_movement = False
            self._reset_pickup()

        volume = self.deadzone_value_converter(action.position)
        self.fl.set_mixer_track_volume(self.track_for_master_volume, volume)

        self.action_dispatcher.dispatch(
            MixerTrackVolumeChangedAction(track=self.track_for_master_volume, control=action.control))

    def _reset_pickup(self):
        self.fl.reset_track_volume_pickup(self.track_for_master_volume)
