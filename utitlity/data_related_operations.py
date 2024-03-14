from data_store.data_schemas import DataFormatToReadTable
from config import Settings

settings = Settings()


def get_data_for_user_table(user_id):
    return DataFormatToReadTable.parse_obj(
        {
            "read_table": True,
            "table_name": settings.USER_TABLE_NAME,
            "primary_key": settings.USER_TABLE_PRIMARY_KEY,
            "primary_key_value": user_id
        }
    )