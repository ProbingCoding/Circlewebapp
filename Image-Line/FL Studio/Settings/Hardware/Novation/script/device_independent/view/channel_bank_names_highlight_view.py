from script.device_independent.util_view.view import View
from script.constants import ChannelNavigationSteps, HighlightDuration, Pads


class ChannelBankNamesHighlightView(View):
    num_steps_per_page = Pads.Num.value

    def __init__(self, action_dispatcher, fl, model):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.model = model

    def _on_show(self):
        if self.model.show_all_highlights_active:
            self._highlight_selected_channel_bank_names()

    def _on_hide(self):
        self._highlight_selected_channel_bank_names(duration_ms=0)

    @property
    def highlight_duration_ms(self):
        if self.model.show_all_highlights_active:
            return HighlightDuration.WithoutEnd.value
        return HighlightDuration.Default.value

    def handle_ShowHighlightsAction(self, action):
        self._highlight_selected_channel_bank_names()

    def handle_HideHighlightsAction(self, action):
        self._highlight_selected_channel_bank_names(duration_ms=0)

    def handle_ChannelBankChangeAttemptedAction(self, action):
        self._highlight_selected_channel_bank_names(duration_ms=self.highlight_duration_ms)

    def _highlight_selected_channel_bank_names(self, *, duration_ms=HighlightDuration.WithoutEnd.value):
        selected_channel = self.model.channel_rack.active_bank * ChannelNavigationSteps.Bank.value
        self.fl.highlight_channelrack_names(first_channel=selected_channel, num_channels=Pads.Num.value,
                                            duration_ms=duration_ms)
