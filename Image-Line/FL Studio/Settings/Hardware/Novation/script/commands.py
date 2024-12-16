from util.plain_data import PlainData

"""
Commands are dispatched to be handled by one specific handler indicating
that a particular thing should happen as a result. Commands should be named with
imperative phrases such as "StartSequencerCommand" or "ExitModeCommand". 
"""


@PlainData
class ExitStepEditModeCommand:
    pass
