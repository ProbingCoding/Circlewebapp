from script.device_independent.util_view.view import View
from script.constants import HighlightDuration, Pads


class ChannelSelectNameHighlightView(View):
    num_steps_per_page = Pads.Num.value

    def __init__(self, action_dispatcher, fl, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model

    def _on_show(self):
        if self.model.show_all_highlights_active:
            self._highlight_selected_channel()

    def _on_hide(self):
        self._highlight_selected_channel(duration_ms=0)

    @property
    def highlight_duration_ms(self):
        if self.model.show_all_highlights_active:
            return HighlightDuration.WithoutEnd.value
        return HighlightDuration.Default.value

    def handle_ShowHighlightsAction(self, action):
        self._highlight_selected_channel()

    def handle_HideHighlightsAction(self, action):
        self._highlight_selected_channel(duration_ms=0)

    def handle_FlGuiChannelSelectAction(self, action):
        self._highlight_selected_channel(duration_ms=self.highlight_duration_ms)

    def handle_ChannelSelectAttemptedAction(self, action):
        self._highlight_selected_channel(duration_ms=self.highlight_duration_ms)

    def _highlight_selected_channel(self, *, duration_ms=HighlightDuration.WithoutEnd.value):

        if self.fl.is_any_channel_selected():
            channel = self.fl.selected_channel()
            self.fl.highlight_channelrack_names(first_channel=channel, num_channels=1,
                                                duration_ms=duration_ms)

        else:
            self.fl.highlight_channelrack_names(first_channel=0, num_channels=1,
                                                duration_ms=0)
