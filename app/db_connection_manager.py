from logger_init import get_logger
from config import Settings
from exceptions.exception import DbFetchException
from data_store.data_schemas import WalletDataForNewEntryTransTable, DataRequiredToReadDB, \
    TransactionDataToAdditionUpdate, WalletDataToCalculateCurrentBalance, DataFormatToUpdateInTable, DataFormatToCreateNewEntry,\
    DataFormatToReadTable
import requests
import simplejson

logger = get_logger(__name__)
settings = Settings()


class DbConnectionManager:
    def __init__(self):
        self.db_api = settings.DB_API

    def update_table(self, result_to_update: DataFormatToUpdateInTable):
        # update to session db
        try:
            response = requests.post(self.db_api,
                                     json=result_to_update.dict())
        except Exception:
            raise DbFetchException(code=500, message="Not able to update data to db")
        else:
            return response

    def get_wallet_transaction_details_for_current_user(self, data_to_read_db: DataFormatToReadTable):
        # fetch data from WalletTransactionTable for latest wallet balance
        try:
            response = requests.post(self.db_api,
                                     json=data_to_read_db.dict())
            logger.debug(f"Response from reading table {response}")
        except Exception:
            logger.exception("Error while reading data from session table")
            raise DbFetchException(code=500, message="Not able to fetch data from db")
        else:
            try:
                parsed_response = response.json()
            except Exception:
                raise DbFetchException(code=500, message="No data available in response")
            else:
                return parsed_response

    def get_wallet_balance_for_current_user(self, data_to_read_db):
        # get wallet balance from user table
        try:
            response = requests.post(self.db_api,
                                     json=data_to_read_db.dict())
            logger.debug(f"Response from reading table {response}")
        except Exception:
            logger.exception("Error while reading data from User table")
            raise DbFetchException(code=500, message="Not able to fetch data from db")
        else:
            try:
                parsed_response = response.json()
            except Exception:
                raise DbFetchException(code=500, message="No data available in response")
            else:
                return parsed_response

    def create_new_wallet_transactions_for_current_user(self, data_to_create_new_entry: DataFormatToCreateNewEntry):
        # create a new entry using user id and order id in db
        try:
            response = requests.post(self.db_api,
                                     json=data_to_create_new_entry.dict())
        except Exception:
            raise DbFetchException(code=500, message="Not able to update data to db")
        else:
            return response
