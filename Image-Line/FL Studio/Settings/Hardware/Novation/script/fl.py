import util.math
from script.constants import HighlightDuration
from script.fl_constants import ChannelType

try:
    import arrangement
    import channels
    import device
    import general
    import midi
    import mixer
    import plugins
    import patterns
    import transport
    import ui
except ImportError as e:
    print(e)

from script.fl_constants import DockSide, GlobalTransportCommand, PickupFollowMode, WindowType, UndoType, \
    ChannelRackDisplayFlags

__all__ = ['FL']


class Channel:

    def get_type(self, group_channel=None):
        if group_channel is None:
            return ChannelType(channels.getChannelType(channels.selectedChannel()))
        else:
            return ChannelType(channels.getChannelType(group_channel))

    def set_parameter_value(self, parameter, value):
        rec_event_parameter = parameter + channels.getRecEventId(channels.selectedChannel())
        value = int(value * midi.FromMIDI_Max)
        mask = midi.REC_MIDIController
        general.processRECEvent(rec_event_parameter, value, mask)

    def set_pitch(self, value):
        """
            value: Normalised pitch value in range 0 to 1
        """
        bipolar_pitch_value = util.math.normalised_unipolar_to_bipolar(value)
        channels.setChannelPitch(channels.selectedChannel(), bipolar_pitch_value)


class Plugin:
    fpc_pad_colour_param_index = midi.GC_Semitone

    def get_colour(self, group_channel, param_index):
        colour_long = plugins.getColor(group_channel, -1, self.fpc_pad_colour_param_index, param_index)
        b, g, r, a = colour_long.to_bytes(4, 'little', signed=True)
        return r, g, b

    def get_note_name(self, group_channel, note):
        note_name_param_index = 2
        return plugins.getName(group_channel, -1, note_name_param_index, note)

    def get_midi_note_for_pad(self, group_channel, pad_index):
        parameter_index_midi_note = 1
        return plugins.getPadInfo(group_channel, -1, parameter_index_midi_note, pad_index)

    def set_parameter_value(self, parameter, value):
        plugins.setParamValue(value, parameter, channels.selectedChannel(), -1,
                              PickupFollowMode.FollowUserSetting.value)


class UI:

    def focus_mixer_window(self):
        if not ui.getFocused(WindowType.Mixer.value):
            ui.showWindow(WindowType.Mixer.value)
            ui.setFocused(WindowType.Mixer.value)

    def focus_channel_window(self):
        if not ui.getFocused(WindowType.ChannelRack.value):
            ui.showWindow(WindowType.ChannelRack.value)
            ui.setFocused(WindowType.ChannelRack.value)

    def focus_plugin_window(self):
        channels.showCSForm(channels.selectedChannel(), 1)

    def hide_plugin_window(self, *, channel=None):
        channels.showCSForm(channels.selectedChannel() if channel is None else channel, 0)

    def is_any_plugin_window_focused(self):
        return ui.getFocused(WindowType.Plugin.value)

    def set_hint_message(self, message):
        return ui.setHintMsg(message)


class FL:

    def __init__(self):
        self.channel = Channel()
        self.plugin = Plugin()
        self.ui = UI()

    def mixer_track_count(self):
        """
        Final track is the 'current' track, which is a special analysis track that has no
        volume or pan controls. We are not interested in this track as we cannot control it.
        """
        return mixer.trackCount() - 1

    def get_mixer_track_volume_dB(self, track):
        return mixer.getTrackVolume(track, 1)

    def reset_track_volume_pickup(self, track):
        mixer.setTrackVolume(track, mixer.getTrackVolume(track), PickupFollowMode.NoPickup.value)

    def reset_track_pan_pickup(self, track):
        mixer.setTrackPan(track, mixer.getTrackPan(track), PickupFollowMode.NoPickup.value)

    def set_mixer_track_volume(self, track, volume):
        mixer.setTrackVolume(track, volume, PickupFollowMode.FollowUserSetting.value)

    def set_mixer_track_pan(self, track, pan):
        mixer.setTrackPan(track, pan, PickupFollowMode.FollowUserSetting.value)

    def get_mixer_track_name(self, track):
        return mixer.getTrackName(track)

    def get_channel_volume_dB(self, channel):
        return channels.getChannelVolume(channel, 1)

    def reset_channel_volume_pickup(self, channel):
        channels.setChannelVolume(channel, channels.getChannelVolume(channel), PickupFollowMode.NoPickup.value)

    def reset_channel_pan_pickup(self, channel):
        channels.setChannelPan(channel, channels.getChannelPan(channel), PickupFollowMode.NoPickup.value)

    def reset_parameter_pickup(self, parameter):
        plugins.setParamValue(plugins.getParamValue(parameter, self.selected_channel()), parameter,
                              self.selected_channel(), -1, PickupFollowMode.NoPickup.value)

    def set_channel_volume(self, channel, volume):
        channels.setChannelVolume(channel, volume, PickupFollowMode.FollowUserSetting.value)

    def set_channel_pan(self, channel, pan):
        channels.setChannelPan(channel, pan, PickupFollowMode.FollowUserSetting.value)

    def get_channel_name(self, channel):
        return channels.getChannelName(channel)

    def channel_select_previous_preset(self, channel=None):
        plugins.prevPreset(self.selected_channel() if channel is None else channel)

    def channel_select_next_preset(self, channel=None):
        plugins.nextPreset(self.selected_channel() if channel is None else channel)

    def channel_preset_count(self, channel=None):
        channel = self.selected_channel() if channel is None else channel
        if channel is None or not plugins.isValid(channel):
            return 0
        return plugins.getPresetCount(channel)

    def get_preset_name(self):
        return plugins.getName(channels.selectedChannel(), -1, 6)

    def selected_channel(self):
        '''
        :return: group channel index of selected channel if channel selected
                 None if no channel is selected

        FL API params:
                canBeNone   == 1: None is returned if no channel selected
        '''
        group_channel = channels.selectedChannel(1)
        return group_channel if group_channel != -1 else None

    def get_selected_global_channel(self):
        '''
        :return: global channel index of selected channel if channel selected
                 None if no channel is selected

        FL API params:
                canBeNone   == 1: None is returned if no channel selected
                offset      == 0: No channel offset
                indexGlobal == 1: Returns global index
        '''
        global_channel = channels.selectedChannel(1, 0, 1)
        return global_channel if global_channel != -1 else None

    def channel_count(self):
        return channels.channelCount()

    def get_global_channel(self, group_channel):
        return channels.getChannelIndex(group_channel)

    def select_channel_exclusively(self, channel):
        channels.selectOneChannel(channel)

    def is_any_channel_selected(self):
        return self.selected_channel() is not None

    def get_instrument_plugin(self):
        selected_channel = self.selected_channel()

        if selected_channel is None:
            return None

        type = self.channel.get_type()
        if type == ChannelType.Sampler:
            return 'Sampler'
        if type == ChannelType.AudioClip:
            return 'AudioClip'
        if type == ChannelType.Layer:
            return 'Layer'
        if type == ChannelType.Generator and plugins.isValid(selected_channel):
            return plugins.getPluginName(selected_channel)
        return None

    def send_note_on(self, note, velocity, *, group_channel=None, global_channel=None):
        if global_channel is not None:
            pass
        elif group_channel is not None:
            global_channel = self.get_global_channel(group_channel)
        else:
            global_channel = self.get_selected_global_channel()

        channels.midiNoteOn(global_channel, note, velocity)

    def send_note_off(self, note, *, group_channel=None, global_channel=None):
        if global_channel is not None:
            pass
        elif group_channel is not None:
            global_channel = self.get_global_channel(group_channel)
        else:
            global_channel = self.get_selected_global_channel()

        channels.midiNoteOn(global_channel, note, 0)

    def get_channel_colour(self, group_channel=None):
        if group_channel is None:
            group_channel = self.selected_channel()
        colour_long = channels.getChannelColor(group_channel)
        b, g, r, a = colour_long.to_bytes(4, 'little', signed=True)
        return r, g, b

    def transport_toggle_playing(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.Play, 1, midi.PME_System, midi.GT_Global)

    def transport_toggle_recording(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.Record, 1, midi.PME_System, midi.GT_Global)

    def toggle_metronome(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.Metronome, 1)

    def transport_stop(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.Stop, 1, midi.PME_System, midi.GT_Global)

    def metronome_is_enabled(self):
        return ui.isMetronomeEnabled()

    def transport_is_playing(self):
        return transport.isPlaying()

    def transport_is_paused(self):
        if self.transport_is_playing():
            return False
        mode_absolute_ticks = 2
        return transport.getSongPos(mode_absolute_ticks) != 0

    def transport_is_recording(self):
        return transport.isRecording()

    def get_channel_rack_active_step(self):
        return arrangement.currentTimeHint(0)

    def set_step_active(self, step, active):
        self.store_current_state_in_undo_history(UndoType.PianoRoll.value, "Step seq edit")
        return channels.setGridBit(self.selected_channel(), step, active)

    def get_step_active(self, step):
        return channels.getGridBit(self.selected_channel(), step)

    def store_current_state_in_undo_history(self, undo_type, description):
        general.saveUndo(description, undo_type)

    def undo(self):
        general.undoUp()

    def redo(self):
        general.undoDown()

    def quantise_start_only(self):
        channels.quickQuantize(self.selected_channel(), 1)

    def highlight_channelrack_steps(self, first_channel, num_channels, first_step, num_steps, *,
                                    duration_ms=HighlightDuration.WithoutEnd.value):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt
        ui.crDisplayRect(first_step, first_channel, num_steps, num_channels, duration_ms,
                         ChannelRackDisplayFlags.Steps | ChannelRackDisplayFlags.ScrollToView)

    def highlight_channelrack_names(self, first_channel, num_channels, *,
                                    duration_ms=HighlightDuration.WithoutEnd.value):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt
        ui.crDisplayRect(0, first_channel, 0, num_channels, duration_ms,
                         ChannelRackDisplayFlags.Name | ChannelRackDisplayFlags.ScrollToView)

    def highlight_channelrack_controls(self, first_channel, num_channels, *,
                                       duration_ms=HighlightDuration.WithoutEnd.value):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt
        first_step, num_steps = 0, 0
        ui.crDisplayRect(first_step, first_channel, num_steps, num_channels, duration_ms,
                         ChannelRackDisplayFlags.PanAndVolume | ChannelRackDisplayFlags.ScrollToView)

    def highlight_tracks(self, relative_index_of_first_track_in_dock, num_tracks, first_track_index, last_track_index,
                         duration_ms=HighlightDuration.WithoutEnd.value):
        if duration_ms == HighlightDuration.WithoutEnd.value:
            duration_ms = midi.MaxInt
        ui.miDisplayDockRect(1 + relative_index_of_first_track_in_dock, num_tracks, DockSide.Center.value, duration_ms)
        if duration_ms > 1:
            # Check against 1 or 0 as mixer highlight does not yet accept 0 as duration
            ui.scrollWindow(0, last_track_index)
            ui.scrollWindow(0, first_track_index)

    def get_selected_pattern_index(self):
        return patterns.patternNumber()

    def get_pattern_length_in_steps(self):
        return patterns.getPatternLength(patterns.patternNumber())

    def get_playing_step_in_current_pattern(self):
        playing_step = mixer.getSongStepPos()
        if playing_step == -1:
            return None
        if playing_step >= self.get_pattern_length_in_steps():
            return None
        return playing_step

    def get_dock_side_for_track(self, track):
        return mixer.getTrackDockSide(track)

    def dump_score_log(self, duration_seconds):
        general.dumpScoreLog(duration_seconds, 1)

    def get_parameter_name(self, parameter):
        return plugins.getParamName(parameter, self.selected_channel())

    def get_parameter_value(self, parameter):
        return plugins.getParamValue(parameter, self.selected_channel())

    def get_parameter_value_as_string(self, parameter):
        return plugins.getParamValueString(parameter, self.selected_channel())

    def send_tap_tempo_event(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.TapTempoEvent, 1, midi.PME_System, midi.GT_Global)

    def loop_record_is_active(self):
        return ui.isLoopRecEnabled()

    def toggle_loop_record(self):
        # Second parameter is value, any non-zero argument will suffice
        transport.globalTransport(GlobalTransportCommand.LoopRecord, 1, midi.PME_System, midi.GT_Global)

    def show_graph_editor(self, step, parameter):
        channels.showGraphEditor(False, parameter, step, self.get_selected_global_channel(), 1)

    def hide_graph_editor(self):
        channels.closeGraphEditor(True)

    def set_step_parameter(self, step, parameter, value, *, updateGraphEditor=True):
        channels.setStepParameterByIndex(self.selected_channel(), patterns.patternNumber(), step, parameter, value)
        if updateGraphEditor:
            channels.updateGraphEditor()

    def get_step_parameter(self, step, parameter):
        return channels.getCurrentStepParam(self.selected_channel(), step, parameter)

    def get_recording_pulses_per_second(self):
        return mixer.getRecPPS()

    def get_tempo(self):
        return mixer.getCurrentTempo(True)

    def enable_master_sync(self):
        device.setMasterSync(1)

    def get_master_sync_enabled(self):
        return device.getMasterSync()
