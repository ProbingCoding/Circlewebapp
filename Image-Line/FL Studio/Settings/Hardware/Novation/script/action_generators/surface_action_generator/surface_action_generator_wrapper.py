class SurfaceActionGeneratorWrapper:

    def __init__(self, action_dispatcher, action_generator):
        self.action_dispatcher = action_dispatcher
        self.action_generator = action_generator

    def handle_midi_event(self, fl_event):
        actions = self.action_generator.handle_midi_event(fl_event)
        if actions:
            for action in actions:
                self.action_dispatcher.dispatch(action)
