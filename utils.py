import decimal
from decimal import Decimal as D

from conf import settings

# precision used by blink trade DO NOT CHANGE
FIAT_PRECISION = settings.PRECISION
BTC_PRECISION = settings.PRECISION


def int_to_decimal_fiat(val, precision=FIAT_PRECISION):
    return D(val) / precision


def int_to_decimal_btc(val, precision=BTC_PRECISION):
    return D(val) / precision


def float_to_decimal(val, decimal_places):
    quantize_str = '.' + '0' * (decimal_places - 1) + '1'
    # floats can be misrepresentation,
    # this can cause odd things like 1999,9999999 instead of 2000,00
    # we need to use ROUND_HALF_UP
    return D(val).quantize(D(quantize_str), decimal.ROUND_HALF_UP)


def cap_decimal_fiat(val):
    cents = D('.01')
    return val.quantize(cents, decimal.ROUND_DOWN)


def cap_decimal_btc(val):
    satoshi = D('0.00000001')
    return val.quantize(satoshi, decimal.ROUND_DOWN)


def decimal_to_int(val):
    integer_quantize = D('1.')

    return int(val.quantize(integer_quantize, decimal.ROUND_DOWN))
