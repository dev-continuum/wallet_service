import simplejson
from exceptions.exception import DataMissingError, DbFetchException
from app.wallet_operations import WalletOperations
from logger_init import get_logger

logger = get_logger(__name__)


def run_operation(operation_object, data_to_pass):
    try:
        logger.info(f"Data for operation {data_to_pass}")
        result = operation_object.value(data_to_pass).run()
    except DbFetchException:
        raise
    else:
        return result


def lambda_handler(event, context):
    try:
        action = event["action"]
        data = event["data"]
    except KeyError:
        raise DataMissingError(code=401, message="action and data keys are necessary in the request field")
    else:
        try:
            logger.info(f"Passing this event to wallet operations handler {event}")
            wallet_operation_object = WalletOperations(action=action, data=data, event_data=event)
            operation_object = wallet_operation_object.get_operation()
        except ModuleNotFoundError:
            raise
        else:
            return run_operation(operation_object, data)

