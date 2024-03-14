import datetime
from pydantic import BaseModel, validator
from typing import Optional, Union
from decimal import Decimal
import uuid


class OrderDataSchemaToSendToRazorPay(BaseModel):
    amount: int
    currency: Optional[str] = "INR"
    receipt: Optional[str] = "test"
    notes: Optional[dict] = {}


class WalletDataForNewEntryTransTable(OrderDataSchemaToSendToRazorPay):
    user_id: str
    razorpay_init_order_id: Optional[str] = None


class WalletDataToCalculateCurrentBalance(BaseModel):
    user_id: str
    amount: int
    add: bool
    deduct: bool


class TotalDataForAdditionTransactionUpdate(BaseModel):
    user_id: str
    amount: int
    add: Optional[bool] = None
    deduct: Optional[bool] = False
    razorpay_init_order_id: str
    razorpay_payment_id: Optional[str]
    razorpay_order_id: Optional[str]
    razorpay_signature: Optional[str]
    transaction_time: Optional[str] = None
    transaction_time_user_readable: Optional[str] = None

    @validator('razorpay_init_order_id')
    def id_should_not_be_empty(cls, v):
        if v is "":
            raise ValueError('razorpay_init_order_id can not be empty')
        return v


class TransactionDataToAdditionUpdate(BaseModel):
    user_id: str
    razorpay_init_order_id: str
    transaction_type: str = "added"
    razorpay_payment_id: Optional[str]
    razorpay_order_id: Optional[str]
    razorpay_signature: Optional[str]
    transaction_time: Optional[str] = None
    transaction_time_user_readable: Optional[str] = None


class TotalDataForDeductionTransactionUpdate(BaseModel):
    user_id: str
    amount: int
    add: Optional[bool] = False
    deduct: Optional[bool] = None
    razorpay_init_order_id: Optional[str] = "electrolite_order_{}".format(uuid.uuid4())
    razorpay_payment_id: Optional[str]
    razorpay_order_id: Optional[str]
    razorpay_signature: Optional[str]
    transaction_time: Optional[str] = None
    transaction_time_user_readable: Optional[str] = None


class TransactionDataToDeductionUpdate(BaseModel):
    user_id: str
    razorpay_init_order_id: str
    amount: int
    razorpay_payment_id: Optional[str]
    razorpay_order_id: Optional[str]
    razorpay_signature: Optional[str]
    transaction_type: str = "deducted"
    transaction_time: Optional[str] = None
    transaction_time_user_readable: Optional[str] = None



class DataRequiredToReadDB(BaseModel):
    user_id: str
    razorpay_init_order_id: Optional[str] = None


class DataRequiredToReadUserDB(BaseModel):
    phonenumber: str
    razorpay_init_order_id: Optional[str] = None


class DataFormatToUpdateInTable(BaseModel):
    update_table: bool
    table_name: str
    primary_key: dict
    sort_key: Optional[dict] = None
    data_to_update: dict


class DataFormatToCreateNewEntry(BaseModel):
    add_row: bool
    table_name: str
    row_data: dict


class DataFormatToReadTable(BaseModel):
    read_table: bool
    table_name: str
    primary_key: str
    primary_key_value: str
    sort_key: Optional[str] = None
    sort_key_value: Optional[str] = None
    all_results: Optional[bool] = None

