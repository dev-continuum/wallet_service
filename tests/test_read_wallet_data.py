from unittest import TestCase
from parameterized import parameterized
from data_store import data_schemas
from app.wallet_operations import WalletOperations, ReadWallet, UpdateWallet, CreateNewTransaction
from http import HTTPStatus


class TestReadingDataFromTransactionTable(TestCase):
    def setUp(self) -> None:
        self.action = "READ"
        self.test_user_id = "9810936621"
        self.data = {"user_id": self.test_user_id}
        self.wallet_operations = WalletOperations(action=self.action,
                                                  data=self.data, event_data=None)

    def test_read_data_from_wallet_transaction_table(self):
        read_operation = self.wallet_operations.get_operation()
        result = read_operation.value(self.data).run()
        print(result)
        self.assertEqual(result["status_code"], HTTPStatus.OK, "Correct http status code")
        self.assertEqual(result["message"], "Here is the data from DB", "Correct message")
        # TODO: We need 5 transactions at least when we fix crud read
        self.assertTrue(result["data"]["wallet"], "Wallet data is available")
        self.assertGreater(len(result["data"]["transaction_data"]), 0, "More than one transaction data")

