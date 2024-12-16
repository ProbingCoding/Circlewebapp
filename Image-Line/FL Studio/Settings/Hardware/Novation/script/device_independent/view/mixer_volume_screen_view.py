from script.device_independent.util_view.view import View


class MixerVolumeScreenView(View):

    def __init__(self, action_dispatcher, screen_writer, fl):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl

    def handle_MixerTrackVolumeChangedAction(self, action):
        volume = self.fl.get_mixer_track_volume_dB(action.track)
        volume_str = '-Inf dB' if volume < -200 else f'{format(volume, ".1f")} dB'
        track_name = self.fl.get_mixer_track_name(action.track)
        self.screen_writer.display_parameter(action.control, name=track_name, value=volume_str)
