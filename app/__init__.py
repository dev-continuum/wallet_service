import boto3
from config import Settings
from utitlity.secret_manager import get_aws_secret

settings = Settings()

session = boto3.session.Session()

secret_razor_pay_credentials = get_aws_secret(session, "razorpay_test")
