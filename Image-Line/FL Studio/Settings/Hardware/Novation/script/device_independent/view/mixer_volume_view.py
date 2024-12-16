from script.device_independent.util_view.view import View
from script.constants import Pots
from script.actions import MixerTrackVolumeChangedAction
from util.deadzone_value_converter import DeadzoneValueConverter


class MixerVolumeView(View):
    tracks_per_bank = Pots.Num.value

    def __init__(self, action_dispatcher, fl, model, *, control_to_index):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model
        self.control_to_index = control_to_index
        self.deadzone_value_converter = DeadzoneValueConverter(max=1.0, centre=0.8, width=0.05)
        self.reset_pickup_on_first_movement = False

    def _on_show(self):
        self.reset_pickup_on_first_movement = True

    def handle_MixerBankChangedAction(self, action):
        self.reset_pickup_on_first_movement = True

    def handle_ControlChangedAction(self, action):
        index = self.control_to_index.get(action.control)
        if index is None or index >= len(self.model.mixer_tracks_in_active_bank):
            return

        if self.reset_pickup_on_first_movement:
            self.reset_pickup_on_first_movement = False
            self._reset_pickup_for_current_mixer_bank()

        volume = self.deadzone_value_converter(action.position)
        track = self.model.mixer_tracks_in_active_bank[index]
        self.fl.set_mixer_track_volume(track, volume)

        self.action_dispatcher.dispatch(MixerTrackVolumeChangedAction(track=track, control=action.control))

    def _reset_pickup_for_current_mixer_bank(self):
        for track in self.model.mixer_tracks_in_active_bank:
            self.fl.reset_track_volume_pickup(track)
