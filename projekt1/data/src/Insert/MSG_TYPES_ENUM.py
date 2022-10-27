from enum import Enum


class MSGTYPE(Enum):
    CANCELED = 'Canceled'
    REROUTE = 'Reroute'
    PLANNED = 'Planned'
