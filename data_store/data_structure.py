from enum import Enum


class Action(Enum):
    READ = 'ReadWallet'
    CREATE = 'CreateNewTransaction'
    UPDATE = "UpdateWallet"

