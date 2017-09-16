#!/usr/bin/env python3


from conf import settings
from tapiocas.tapioca_blinktrade import BlinkTrade, BlinkTradePublic
from utils import (
    cap_decimal_fiat, cap_decimal_btc, int_to_decimal_fiat, int_to_decimal_btc,
    decimal_to_int, float_to_decimal
)
from db import upsert_order, get_order, increment_cl_ord_id


class BalanceFiat:
    def __init__(self, balance, balance_locked):
        self.balance = balance
        self.balance_locked = balance_locked

    @property
    def pretty_balance(self):
        return cap_decimal_fiat(int_to_decimal_fiat(self.balance))

    @property
    def pretty_balance_locked(self):
        return cap_decimal_fiat(int_to_decimal_fiat(self.balance_locked))

    @property
    def balance_available(self):
        return self.balance - self.balance_locked

    @property
    def pretty_balance_available(self):
        return cap_decimal_fiat(int_to_decimal_fiat(self.balance_available))


api = BlinkTrade(
    api_url=settings.BLINKTRADE_API_URL,
    key=settings.BLINKTRADE_API_KEY,
    secret=settings.BLINKTRADE_API_SECRET)

api_public = BlinkTradePublic(
    api_url=settings.BLINKTRADE_API_URL,
    currency=settings.CURRENCY)


def get_fiat_balance_from_response(response):
    balance_obj = response.Responses[0][settings.BROKER]
    balance = balance_obj[settings.CURRENCY]().data
    balance_locked = balance_obj[settings.CURRENCY + '_locked']().data
    return BalanceFiat(balance, balance_locked)


def get_orders_from_response(response, check_if_created_by_us=True):
    keys = response.Responses[0].Columns().data
    orders = []

    for order_raw in response.Responses[0].OrdListGrp:
        order = dict(zip(keys, order_raw().data))
        if check_if_created_by_us and not get_order(order['OrderID']):
            continue
        orders.append(order)

    return orders


def get_order_from_orders_response(response, order_id):
    keys = response.Responses[0].Columns().data

    for order_raw in response.Responses[0].OrdListGrp:
        order = dict(zip(keys, order_raw().data))
        if order['OrderID'] == order_id:
            return order

    return None


def main():
    fiat_balance = get_fiat_balance_from_response(api.balance().post())

    print('Balance BRL:', fiat_balance.pretty_balance)
    print('Balance BRL (locked):', fiat_balance.pretty_balance_locked)
    print('Balance BRL (available):', fiat_balance.pretty_balance_available)

    orders = get_orders_from_response(api.open_orders().post())

    if not orders:
        print("No previous order created by us.")
    else:
        print("Found previous order created by us, canceling them.")

    for order in orders:
        print("ORDER:")
        print('OrderId', order['OrderID'])
        print('OrderQty', cap_decimal_btc(int_to_decimal_btc(order['OrderQty'])))
        print('Price', cap_decimal_fiat(int_to_decimal_fiat(order['Price'])))
        print('Canceling...')
        response = api.cancel_order().post(
            data={
                "ClOrdID": order['ClOrdID'],
            }
        )
    if orders:
        assert not get_orders_from_response(api.open_orders().post()), (
            "Something went wrong, order not canceled")

    response = api_public.orderbook(crypto_currency='BTC').get()

    assert response.pair().data == 'BTCBRL', 'Something wrong, this is not BTCBRL'

    bid_prices = sorted(set([bid[0]().data for bid in response.bids]), reverse=True)

    # get the second higher price
    bid_price = float_to_decimal(bid_prices[1], decimal_places=2)
    volume = int_to_decimal_fiat(settings.PER_ORDER_IN_CENTS, precision=100)
    qty = volume / bid_price

    assert volume < fiat_balance.balance_available, "Not enough balance"

    max_acceptable_price = int_to_decimal_fiat(settings.MAX_ACCEPTABLE_PRICE_IN_CENTS,
                                               precision=100)

    assert bid_price < max_acceptable_price, (
        'Price is over threshold (${}): ${}'.format(
            cap_decimal_fiat(max_acceptable_price),
            cap_decimal_fiat(bid_price)))

    print("Placing an order as second larger price (${}) volume (${}) qty ({}BTC)".format(
        cap_decimal_fiat(bid_price), cap_decimal_fiat(volume), cap_decimal_btc(qty)
    ))

    data = {
        'ClOrdID': increment_cl_ord_id(),
        'Price': decimal_to_int(bid_price * settings.PRECISION),
        'OrderQty': decimal_to_int(qty * settings.PRECISION),
        'BrokerID': settings.BROKER,
    }

    response = api.buy_order().post(
        data=data
    )
    order_id = response.Responses[0]['OrderID']().data
    order = get_order_from_orders_response(api.open_orders().post(), order_id)

    if order:
        upsert_order(order)


if __name__ == '__main__':
    main()
