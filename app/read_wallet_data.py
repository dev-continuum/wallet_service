import logging
from logger_init import get_logger
from config import Settings
from .db_connection_manager import DbConnectionManager
from data_store.data_schemas import DataRequiredToReadDB, DataFormatToReadTable
from utitlity.data_related_operations import get_data_for_user_table
from http import HTTPStatus

logger = get_logger(__name__)
settings = Settings()


class ReadWallet:
    """
    1- Read user table for final balance
    2- Read top 5 transactions for that user
    """

    def __init__(self, data_to_read_from_db):
        self.db_api: DbConnectionManager = DbConnectionManager()
        self.data_to_read_from_db = DataRequiredToReadDB.parse_obj(data_to_read_from_db)
        logger.info(f"Parsed data to read db {self.data_to_read_from_db}")

    def parse_and_make_final_data(self, user_data):
        try:
            wallet_data = {"wallet": user_data["wallet"]}
        except KeyError:
            logger.exception("There is no wallet attribute in the user data")
            return None
        else:
            return wallet_data

    def run(self):
        final_data_to_send_to_read_trans_table = DataFormatToReadTable.parse_obj(
            {
                "read_table": True,
                "table_name": settings.TRANSACTION_TABLE_NAME,
                "primary_key": settings.TRANSACTION_TABLE_PRIMARY_KEY,
                "primary_key_value": self.data_to_read_from_db.user_id,
                "all_results": True
                # "sort_key": settings.TRANSACTION_TABLE_SORT_KEY,
                # "sort_key_value": self.data_to_read_from_db.razorpay_init_order_id
            }
        )
        final_data_to_send_to_read_user_table = get_data_for_user_table(self.data_to_read_from_db.user_id)
        try:
            user_data = self.db_api.get_wallet_balance_for_current_user(final_data_to_send_to_read_user_table)
            user_wallet_transaction_data = self.db_api.get_wallet_transaction_details_for_current_user(
                final_data_to_send_to_read_trans_table)
        except Exception:
            return {"status_code": HTTPStatus.SERVICE_UNAVAILABLE, "message": f"Unable to fetch data from the db",
                    "data": []}
        else:
            wallet_data = self.parse_and_make_final_data(user_data)
            wallet_data.update({"transaction_data": user_wallet_transaction_data})
            return {"status_code": HTTPStatus.OK, "message": f"Here is the data from DB",
                    "data": wallet_data}
