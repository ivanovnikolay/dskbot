import json
from time import monotonic
from urllib.request import urlopen


_spred = 0.5
_last_request_time = 0
_last_rate = 0


def yuan_exchange_rate():
    global _last_request_time
    global _last_rate

    if not _last_rate or monotonic() - _last_request_time > 3600:
        with urlopen('https://api.exchangerate-api.com/v4/latest/CNY') as response:
            exchange = json.load(response)
        _last_rate = round(exchange['rates']['RUB'] + _spred, 2)
        _last_request_time = monotonic()
    return _last_rate
