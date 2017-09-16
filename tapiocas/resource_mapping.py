# coding: utf-8

RESOURCE_MAPPING = {
    'balance': {
        'resource': '',
        'message_type': 'balance',
    },
    'open_orders': {
        'resource': '',
        'message_type': 'open_orders',
    },
    'cancel_order': {
        'resource': '',
        'message_type': 'cancel_order',
    },
    'buy_order': {
        'resource': '',
        'message_type': 'buy_order',
    }
}

MESSAGE_TYPES = {
    'balance': {
        "MsgType": "U2",
        "BalanceReqID": 1
    },
    'open_orders': {
        "MsgType": "U4",
        "OrdersReqID": 1,
        "Page": 0,
        "PageSize": 100,
        "Filter": ["has_leaves_qty eq 1"],
    },
    'cancel_order': {
        "MsgType": "F",
    },
    'buy_order': {
        "MsgType": "D",
        "Symbol": "BTCBRL",
        # "1" = Buy
        "Side": "1",
        # "2" = Limited
        "OrdType": "2",
    }
}

PUBLIC_RESOURCE_MAPPING = {
    'orderbook': {
        'resource': 'orderbook',
    }
}
