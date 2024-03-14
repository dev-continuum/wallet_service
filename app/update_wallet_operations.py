import logging
from logger_init import get_logger
from config import Settings
from utitlity.time_related_operations import get_current_date_time_format
from .db_connection_manager import DbConnectionManager
from data_store.data_schemas import TotalDataForAdditionTransactionUpdate, TotalDataForDeductionTransactionUpdate, \
    TransactionDataToAdditionUpdate, WalletDataToCalculateCurrentBalance, DataFormatToUpdateInTable, \
    DataFormatToCreateNewEntry, TransactionDataToDeductionUpdate
from exceptions.exception import DbFetchException
from utitlity.data_related_operations import get_data_for_user_table
from http import HTTPStatus


logger = get_logger(__name__)
settings = Settings()


class UpdateWallet:
    def __init__(self, total_data_for_transaction_update):
        self.total_data_for_transaction_update = total_data_for_transaction_update
        self.date_time_related_data = get_current_date_time_format()
        self.total_data_for_transaction_update["transaction_time"] = self.date_time_related_data["transaction_time"]
        self.total_data_for_transaction_update["transaction_time_user_readable"] = self.date_time_related_data["transaction_time_user_readable"]

    @staticmethod
    def bad_data_fail_early():
        return {"status_code": HTTPStatus.BAD_REQUEST,
                "message": f"Razorpay initial order id seems to be missing",
                "data": []}

    @staticmethod
    def no_flag_set_for_wallet_update():
        return {"status_code": HTTPStatus.BAD_REQUEST,
                "message": f"Either add or deduct flag needs to be set for wallet update",
                "data": []}

    def run(self):
        # based on data decide and run addition or deduction class
        if self.total_data_for_transaction_update["add"]:
            try:
                final_wallet_addition_data = TotalDataForAdditionTransactionUpdate.parse_obj(self.total_data_for_transaction_update)
            except ValueError:
                self.total_data_for_transaction_update = None
                return self.bad_data_fail_early()
            else:
                add_to_wallet = UpdateWalletAddition(final_wallet_addition_data)
                return add_to_wallet.run()

        elif self.total_data_for_transaction_update["deduct"]:
            final_wallet_deduction_data = TotalDataForDeductionTransactionUpdate.parse_obj(
                self.total_data_for_transaction_update)
            deduct_from_wallet = UpdateWalletDeduction(final_wallet_deduction_data)
            return deduct_from_wallet.run()

        else:
            return self.no_flag_set_for_wallet_update()


class UpdateWalletAddition:
    """
    1- Use update table with + or - attributes for user table
    2- Update transaction table data also with relevant data
    """

    def __init__(self, total_data_for_transaction_update: TotalDataForAdditionTransactionUpdate):
        self.db_api: DbConnectionManager = DbConnectionManager()
        self.data_to_update_to_trans_user_tables = TransactionDataToAdditionUpdate.parse_obj(
            total_data_for_transaction_update.dict())
        self.data_to_calculate_current_balance = WalletDataToCalculateCurrentBalance.parse_obj(
            total_data_for_transaction_update.dict())

    def run(self):
        try:
            final_wallet_data = self.read_and_update_balance_in_user_table()
            user_transaction_data = self.update_transaction_details_in_wallet_transaction_table()
        except Exception:
            return {"status_code": HTTPStatus.BAD_REQUEST,
                    "message": f"Unable to update table in the user or transaction table",
                    "data": []}
        else:
            if final_wallet_data and user_transaction_data:
                final_wallet_data.update(user_transaction_data)
                return {"status_code": HTTPStatus.OK,
                        "message": f"Data Update in user wallet and transaction details captured",
                        "data": final_wallet_data}
            elif final_wallet_data and not user_transaction_data:
                return {"status_code": HTTPStatus.EXPECTATION_FAILED,
                        "message": f"Data Updated in user wallet but transaction details not captured",
                        "data": {}}
            elif not final_wallet_data and user_transaction_data:
                return {"status_code": HTTPStatus.EXPECTATION_FAILED,
                        "message": f"User wallet update failed but transaction details captured",
                        "data": {}}
            else:
                return {"status_code": HTTPStatus.NOT_IMPLEMENTED,
                        "message": f"Something went wrong during update of wallet balance and transaction details",
                        "data": {}}

    def read_and_update_balance_in_user_table(self):
        current_wallet_balance = self.db_api.get_wallet_balance_for_current_user(
            get_data_for_user_table(self.data_to_calculate_current_balance.user_id))["wallet"]

        if self.data_to_calculate_current_balance.add:
            final_wallet_balance = int(current_wallet_balance) + int(
                self.data_to_calculate_current_balance.amount)
        else:
            logger.warning("We should not reach this state inside Addition operation add flag MUST be true")
            return None

        data_to_update_user_table = DataFormatToUpdateInTable.parse_obj({
            "update_table": True,
            "table_name": settings.USER_TABLE_NAME,
            "primary_key": {settings.USER_TABLE_PRIMARY_KEY: self.data_to_calculate_current_balance.user_id},
            "data_to_update": {"wallet": final_wallet_balance}
        }
        )
        try:
            self.db_api.update_table(data_to_update_user_table)
        except DbFetchException:
            logger.exception(
                f"Unable to update wallet balance for user:{self.data_to_calculate_current_balance.user_id} "
                f"amount: {final_wallet_balance}")
            return None
        else:
            logger.info(f"Updated wallet balance for user:{self.data_to_calculate_current_balance.user_id} "
                        f"amount: {final_wallet_balance}")
            return {"final_wallet_balance": final_wallet_balance}

    def update_transaction_details_in_wallet_transaction_table(self):
        data_to_update_transaction_table = DataFormatToUpdateInTable.parse_obj({
            "update_table": True,
            "table_name": "WalletTransactionTable",
            "primary_key": {"user_id": self.data_to_update_to_trans_user_tables.user_id},
            "sort_key": {"razorpay_init_order_id": self.data_to_update_to_trans_user_tables.razorpay_init_order_id},
            "data_to_update": self.data_to_update_to_trans_user_tables.dict(
                exclude={"user_id", "razorpay_init_order_id"})
        })

        try:
            self.db_api.update_table(data_to_update_transaction_table)
        except DbFetchException:
            logger.exception(f"Unable to update transaction for razorpay id: "
                             f"{self.data_to_update_to_trans_user_tables.razorpay_init_order_id} user_id: "
                             f"{self.data_to_update_to_trans_user_tables.user_id}")
            return None
        else:
            logger.exception(f"updated transaction for razorpay id: "
                             f"{self.data_to_update_to_trans_user_tables.razorpay_init_order_id} user_id: "
                             f"{self.data_to_update_to_trans_user_tables.user_id}")
            return self.data_to_update_to_trans_user_tables.dict()


class UpdateWalletDeduction:
    def __init__(self, total_data_for_transaction_update: TotalDataForDeductionTransactionUpdate):
        self.db_api: DbConnectionManager = DbConnectionManager()
        self.data_to_update_to_trans_user_tables = TransactionDataToDeductionUpdate.parse_obj(
            total_data_for_transaction_update.dict())
        self.data_to_calculate_current_balance = WalletDataToCalculateCurrentBalance.parse_obj(
            total_data_for_transaction_update.dict())

    def run(self):
        try:
            final_wallet_data = self.read_and_update_balance_in_user_table()
            user_transaction_data = self.update_transaction_details_in_wallet_transaction_table()
        except Exception:
            return {"status_code": HTTPStatus.BAD_REQUEST,
                    "message": f"Unable to update table in the user or transaction table",
                    "data": []}
        else:
            if final_wallet_data and user_transaction_data:
                final_wallet_data.update(user_transaction_data)
                return {"status_code": HTTPStatus.OK,
                        "message": f"Data Update in user wallet and transaction details captured",
                        "data": final_wallet_data}
            elif final_wallet_data and not user_transaction_data:
                return {"status_code": HTTPStatus.EXPECTATION_FAILED,
                        "message": f"Data Updated in user wallet but transaction details not captured",
                        "data": {}}
            elif not final_wallet_data and user_transaction_data:
                return {"status_code": HTTPStatus.EXPECTATION_FAILED,
                        "message": f"User wallet update failed but transaction details captured",
                        "data": {}}
            else:
                return {"status_code": HTTPStatus.NOT_IMPLEMENTED,
                        "message": f"Something went wrong during update of wallet balance and transaction details",
                        "data": {}}

    def read_and_update_balance_in_user_table(self):
        current_wallet_balance = self.db_api.get_wallet_balance_for_current_user(
            get_data_for_user_table(self.data_to_calculate_current_balance.user_id))["wallet"]

        if self.data_to_calculate_current_balance.deduct:
            final_wallet_balance = int(current_wallet_balance) - int(
                self.data_to_calculate_current_balance.amount)
        else:
            logger.warning("We should not reach this state inside Deduction operation deduct flag MUST be true")
            return None

        data_to_update_user_table = DataFormatToUpdateInTable.parse_obj({
            "update_table": True,
            "table_name": settings.USER_TABLE_NAME,
            "primary_key": {settings.USER_TABLE_PRIMARY_KEY: self.data_to_calculate_current_balance.user_id},
            "data_to_update": {"wallet": final_wallet_balance}
        }
        )
        try:
            self.db_api.update_table(data_to_update_user_table)
        except DbFetchException:
            logger.exception(
                f"Unable to update wallet balance for user:{self.data_to_calculate_current_balance.user_id} "
                f"amount: {final_wallet_balance}")
            return None
        else:
            logger.info(f"Updated wallet balance for user:{self.data_to_calculate_current_balance.user_id} "
                        f"amount: {final_wallet_balance}")
            return {"final_wallet_balance": final_wallet_balance}

    def update_transaction_details_in_wallet_transaction_table(self):
        data_to_send_to_create_new_entry = DataFormatToCreateNewEntry.parse_obj({
            "add_row": True,
            "table_name": "WalletTransactionTable",
            "row_data": self.data_to_update_to_trans_user_tables.dict()
        })
        try:
            self.db_api.create_new_wallet_transactions_for_current_user(data_to_send_to_create_new_entry)
        except DbFetchException:
            logger.exception(f"Unable to update transaction for razorpay id: "
                             f"{self.data_to_update_to_trans_user_tables.razorpay_init_order_id} user_id: "
                             f"{self.data_to_update_to_trans_user_tables.user_id}")
            return None
        else:
            logger.exception(f"updated transaction for razorpay id: "
                             f"{self.data_to_update_to_trans_user_tables.razorpay_init_order_id} user_id: "
                             f"{self.data_to_update_to_trans_user_tables.user_id}")
            return self.data_to_update_to_trans_user_tables.dict()
