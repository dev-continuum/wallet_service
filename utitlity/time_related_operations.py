import datetime
import pytz


def get_current_date_time_format(timezone="UTC", time_format="isoformat"):
    data_to_return = {}
    if time_format == "isoformat":
        date_time_object = datetime.datetime.now(pytz.timezone(timezone))
        data_to_return["transaction_time"] = date_time_object.strftime('%Y-%m-%d %H:%M:%S')
        data_to_return["transaction_time_user_readable"] = date_time_object.astimezone(pytz.timezone("Asia/Calcutta")).strftime('%d %b, %I:%M %p')
        data_to_return["date"] = date_time_object.date().isoformat()
        data_to_return["time"] = date_time_object.time().isoformat(timespec='seconds')
        data_to_return["timezone"] = str(date_time_object.tzinfo)
        return data_to_return
    else:
        return data_to_return
