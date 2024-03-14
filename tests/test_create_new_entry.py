from unittest import TestCase
from parameterized import parameterized
from data_store import data_schemas
from app.wallet_operations import WalletOperations, ReadWallet, UpdateWallet, CreateNewTransaction
from http import HTTPStatus


class TestCreatingNewEntryPositive(TestCase):
    def setUp(self) -> None:
        self.action = "CREATE"
        self.data = {"user_id": 9810936621,
                     "amount": 2000,
                     "currency": "INR"}
        self.wallet_operation = WalletOperations(action=self.action, data=self.data, event_data=None)

    def test_create_new_entry_in_db(self):
        create_operation = self.wallet_operation.get_operation()
        result = create_operation.value(self.data).run()
        self.assertEqual(result["status_code"], HTTPStatus.OK)
        self.assertIsInstance(result["data"]["id"], str)
