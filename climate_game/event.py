import pythonnet

pythonnet.load("coreclr")
from enum import Enum, auto  ## noqa


class LiveEventType(Enum):
    ButtonPress = 0
    VoiceActivity = auto()
    LookAtParticipant = auto()
