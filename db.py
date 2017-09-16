from tinydb import TinyDB, Query

db = TinyDB('db.json')
orders_table = db.table('orders')
order_control = db.table('order_control')


def upsert_order(order):
    Order = Query()
    if not orders_table.search(Order.OrderID == order['OrderID']):
        orders_table.insert(order)
    else:
        orders_table.update(order, Order.OrderID == order['OrderID'])


def get_order(orderID):
    Order = Query()
    result = orders_table.search(Order.OrderID == orderID)
    return result[0] if result else None


def increment_cl_ord_id():
    result = order_control.all()
    control = result[0] if result else {'cl_ord_id': 0}
    control['cl_ord_id'] += 1
    if result:
        order_control.update(control, eids=[control.eid])
    else:
        order_control.insert(control)
    return control['cl_ord_id']
