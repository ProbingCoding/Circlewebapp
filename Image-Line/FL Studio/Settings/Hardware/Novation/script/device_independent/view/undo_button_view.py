from script.actions import FunctionTriggeredAction
from script.constants import ButtonFunction
from script.device_independent.util_view.view import View


class UndoButtonView(View):

    def __init__(self, action_dispatcher, fl, product_defs):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.product_defs = product_defs

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("Undo"):
            self.fl.undo()
            self.action_dispatcher.dispatch(FunctionTriggeredAction(type=ButtonFunction.Undo))