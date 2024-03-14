from unittest import TestCase
from parameterized import parameterized
from data_store import data_schemas
from app.wallet_operations import WalletOperations, ReadWallet, UpdateWallet, CreateNewTransaction
from http import HTTPStatus


class Update_Addition_UserAndTransactionTable(TestCase):
    def setUp(self) -> None:
        self.action = "UPDATE"
        self.test_user_id = "9810936621"
        self.data = {"user_id": self.test_user_id,
                     "amount": 20,
                     "add": True,
                     "deduct": False,
                     "razorpay_init_order_id": 'order_LBT7doLOwgqdpE',
                     "razorpay_payment_id": "test_tik",
                     "razorpay_order_id": "test_abhi",
                     "razorpay_signature": "test_abhi"
                     }
        self.wallet_operations = WalletOperations(action=self.action,
                                                  data=self.data, event_data=None)

    def test_update_transaction_and_user_table(self):
        update_operation = self.wallet_operations.get_operation()
        result = update_operation.value(self.data).run()
        self.assertEqual(HTTPStatus.OK, result["status_code"], "Correct http status code")
        self.assertEqual(result["message"], "Data Update in user wallet and transaction details captured", "Correct message")
        self.assertLessEqual(0, int(result["data"]["final_wallet_balance"]), "wallet balance is greater or equal to zero")


class UpdateUserAndTransactionTableWithEmptyId(TestCase):
    def setUp(self) -> None:
        self.action = "UPDATE"
        self.test_user_id = "9810936621"
        self.data = {"user_id": self.test_user_id,
                     "amount_to_update": 200,
                     "add": True,
                     "deduct": False,
                     "razorpay_init_order_id": '',
                     "razorpay_payment_id": "test_tik",
                     "razorpay_order_id": "test_abhi",
                     "razorpay_signature": "test_abhi"
                     }
        self.wallet_operations = WalletOperations(action=self.action,
                                                  data=self.data, event_data=None)

    def test_update_transaction_and_user_table_with_empty_id(self):
        update_operation = self.wallet_operations.get_operation()
        result = update_operation.value(self.data).run()
        print(result)
        self.assertEqual(HTTPStatus.BAD_REQUEST, result["status_code"], "Correct http status code")


class UpdateDeductionUserAndTransactionTable(TestCase):
    def setUp(self) -> None:
        self.action = "UPDATE"
        self.test_user_id = "9810936621"
        self.data = {"user_id": self.test_user_id,
                     "amount": 200,
                     "add": False,
                     "deduct": True
                     }
        self.wallet_operations = WalletOperations(action=self.action,
                                                  data=self.data, event_data=None)

    def test_update_transaction_and_user_table(self):
        update_operation = self.wallet_operations.get_operation()
        result = update_operation.value(self.data).run()
        print(result)
