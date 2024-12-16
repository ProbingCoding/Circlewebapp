import math

from .fl_actions import AllMixerTracksChangedAction, ChannelSelectionToggleAction, FirstTimeConnectedAction, \
    OnRefreshAction, PlayingStepChangedAction, TempoChangedAction, TimerEventAction
from script.fl_constants import DirtyChannelUpdateType, RefreshFlags


class FLActionGenerator:

    def __init__(self, action_dispatcher, fl):
        self.action_dispatcher = action_dispatcher
        self.fl = fl
        self.most_recent_playing_step_in_current_pattern = "Initial value. Not set"
        self.most_recent_tempo = -1
        self.previously_any_channel_selected = True

        self.cached_dirty_channel_flags = 0
        self.cached_dirty_mixer_called = False

    def handle_refresh_event(self, flags):
        if self.cached_dirty_mixer_called and flags & RefreshFlags.MixerControls.value:
            self.action_dispatcher.dispatch(AllMixerTracksChangedAction())
            self.cached_dirty_mixer_called = False

        if flags & RefreshFlags.ChannelEvent.value:
            flags |= self.cached_dirty_channel_flags
            self.cached_dirty_channel_flags = 0
        self.action_dispatcher.dispatch(OnRefreshAction(flags=flags))
        self._generate_actions_for_channel_toggle()

    def handle_idle_event(self):
        current_step = self.fl.get_playing_step_in_current_pattern()
        if current_step != self.most_recent_playing_step_in_current_pattern:
            self.most_recent_playing_step_in_current_pattern = current_step
            self.action_dispatcher.dispatch(PlayingStepChangedAction(step=current_step))

        current_tempo = self.fl.get_tempo()
        if not math.isclose(current_tempo, self.most_recent_tempo):
            self.most_recent_tempo = current_tempo
            self.action_dispatcher.dispatch(TempoChangedAction())

        self.action_dispatcher.dispatch(TimerEventAction())

    def handle_dirty_channel_event(self, channel, update_type):
        if update_type == DirtyChannelUpdateType.New.value or \
                update_type == DirtyChannelUpdateType.Delete.value or \
                channel == -1:
            self.cached_dirty_channel_flags |= RefreshFlags.ChannelGroup.value

        elif update_type == DirtyChannelUpdateType.Replace.value or \
                update_type == DirtyChannelUpdateType.Rename.value:
            self.cached_dirty_channel_flags |= RefreshFlags.ChannelSelection.value

    def handle_dirty_mixer_track_event(self, track):
        if track == -1:
            self.cached_dirty_mixer_called = True

    def handle_first_connect_event(self):
        self.action_dispatcher.dispatch(FirstTimeConnectedAction())

    def _generate_actions_for_channel_toggle(self):
        currently_any_channel_selected = self.fl.is_any_channel_selected()
        if self.previously_any_channel_selected != currently_any_channel_selected:
            self.action_dispatcher.dispatch(
                ChannelSelectionToggleAction(any_channel_selected=currently_any_channel_selected))
        self.previously_any_channel_selected = currently_any_channel_selected
