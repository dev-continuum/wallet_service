from unittest import TestCase
from parameterized import parameterized
from app.wallet_operations import WalletOperations, ReadWallet, UpdateWallet, CreateNewTransaction
from data_store.data_schemas import TotalDataForAdditionTransactionUpdate


class TestObjectGeneration(TestCase):
    @parameterized.expand([
        ["READ", ReadWallet, ],
        ["CREATE", CreateNewTransaction, ],
        ["UPDATE", UpdateWallet, ],
    ])
    def test_positive_class_generation(self, action, expected_result):
        self.event_data = {"action": action,
                           "data": {}}
        dummy_data = TotalDataForAdditionTransactionUpdate.parse_obj({"user_id": "",
                                                              "amount_to_update": 1,
                                                              "add": True,
                                                              "deduct": False,
                                                              "razorpay_init_order_id": "fdf"})
        self.wallet_operation = WalletOperations(action=action, data=self.event_data, event_data=self.event_data)
        result = self.wallet_operation.get_operation()
        self.assertIsInstance(result.value(dummy_data), expected_result)


class TestNegativeObjectGeneration(TestCase):
    def setUp(self) -> None:
        self.action = "ERROR"
        self.event_data = {"action": self.action,
                           "data": {}}
        self.wallet_operation = WalletOperations(action=self.action, data=self.event_data, event_data=self.event_data)

    def test_negative_class_generation(self):
        try:
            result = self.wallet_operation.get_operation()
        except NotImplementedError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
