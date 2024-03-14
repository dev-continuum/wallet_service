import datetime
from pydantic import BaseSettings, AnyHttpUrl
from typing import Optional
import pathlib
import os

env_name = os.getenv("ACTIVE_ENVIRONMENT")
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

class Settings(BaseSettings):
    DB_API: AnyHttpUrl
    DB_NAME: str
    DB_REGION: str
    TRANSACTION_TABLE_NAME: str
    USER_TABLE_NAME: str
    USER_TABLE_PRIMARY_KEY: str
    TRANSACTION_TABLE_PRIMARY_KEY: str
    TRANSACTION_TABLE_SORT_KEY: str
    AWS_ACCESS_KEY_ID: str = aws_access_key_id
    AWS_SECRET_ACCESS_KEY: str = aws_secret_access_key


    class Config:
        print(pathlib.Path(__file__).resolve().parents[0])
        env_file = pathlib.Path.joinpath(pathlib.Path(__file__).resolve().parents[0], f"configs/{env_name}.env")
        print(env_file)


if __name__ == "__main__":
    settings = Settings()
    print(settings.dict())
