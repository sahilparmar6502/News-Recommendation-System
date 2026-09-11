from datetime import datetime
import math


def truncate(value, length=220):
    value = " ".join(str(value).split())
    return value if len(value) <= length else value[:length].rsplit(" ", 1)[0] + "..."


def format_date(value):
    if not value:
        return "Date unavailable"
    if isinstance(value, float) and math.isnan(value):
        return "Date unavailable"
    if isinstance(value, datetime):
        return value.strftime("%b %d, %Y")
    return str(value)[:10]