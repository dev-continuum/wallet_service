import logging
from logger_init import get_logger
from config import Settings
from .db_connection_manager import DbConnectionManager
from data_store.data_schemas import WalletDataForNewEntryTransTable, OrderDataSchemaToSendToRazorPay, DataFormatToCreateNewEntry
from app import secret_razor_pay_credentials
from http import HTTPStatus
import razorpay
logger = get_logger(__name__)
settings = Settings()


class CreateNewTransaction:
    """
    A class
    1- Get a new order_id from razorpay based on the data provided
    2- Create a new transaction in Wallet transaction table
    """

    def __init__(self, data_to_create_new_entry_for_payment_order):
        self.db_api: DbConnectionManager = DbConnectionManager()
        self.data_to_create_new_entry_for_payment_order = WalletDataForNewEntryTransTable.parse_obj(
            data_to_create_new_entry_for_payment_order)
        self.data_to_send_to_razorpay_for_order_id = OrderDataSchemaToSendToRazorPay.parse_obj(
            self.data_to_create_new_entry_for_payment_order.dict())

    def get_new_order_id_from_razorpay(self):
        client = razorpay.Client(auth=(secret_razor_pay_credentials["razorpay_key_id"],
                                       secret_razor_pay_credentials["razorpay_key_secret"]))
        response = client.order.create(self.data_to_send_to_razorpay_for_order_id.dict())
        logger.debug(f"response from razorpay is {response}")
        if response["status"] == "created":
            logger.debug(f"Here is the success response from razorpay api {response}")
            return {"status_code": HTTPStatus.OK, "message": f"here is the order id",
                    "data": response}
        else:
            return {"status_code": HTTPStatus.SERVICE_UNAVAILABLE, "message": f"unable to create order id for "
                                                                              f"payment gateway",
                    "data": response}

    def run(self):
        result = self.get_new_order_id_from_razorpay()
        if result["status_code"] == HTTPStatus.OK:
            self.data_to_create_new_entry_for_payment_order.razorpay_init_order_id = result["data"]["id"]
            self.data_to_create_new_entry_for_payment_order.amount = int(self.data_to_create_new_entry_for_payment_order.amount/100)
            data_to_send_to_create_new_entry = DataFormatToCreateNewEntry.parse_obj({
                "add_row": True,
                "table_name": settings.TRANSACTION_TABLE_NAME,
                "row_data": self.data_to_create_new_entry_for_payment_order.dict()
            })
            self.db_api.create_new_wallet_transactions_for_current_user(data_to_send_to_create_new_entry)
            return result
        else:
            return result
