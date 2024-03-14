import logging
from logger_init import get_logger
from config import Settings
from .create_new_razorpay_order import CreateNewTransaction
from .read_wallet_data import ReadWallet
from .update_wallet_operations import UpdateWallet
from .db_connection_manager import DbConnectionManager
from enum import Enum
from http import HTTPStatus
from exceptions.exception import DbFetchException

logger = get_logger(__name__)
settings = Settings()


class Action(Enum):
    READ = ReadWallet
    CREATE = CreateNewTransaction
    UPDATE = UpdateWallet


class WalletOperations:
    """
    A class to perform all wallet related operations
    1- create a new transaction
    2- Update the transaction
    3- update wallet balance
    4- get balance and transaction
    """

    def __init__(self, action, data, event_data):
        self.action = action
        self.data = data
        self.event_data = event_data

    def get_operation(self):
        try:
            action_class = Action[self.action]
        except KeyError:
            raise NotImplementedError(f"{self.action} is not implemented")
        else:
            return action_class
