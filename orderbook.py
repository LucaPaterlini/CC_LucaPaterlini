""" orderbook as module contains the configuration parameters and the class Orderbook
that expose the functional of adding,updating and cancelling and order and retrieving
the best of ask and bid orders"""

from collections import defaultdict, namedtuple

DEC = 5
ASK = "S"
BID = "B"
CANCEL = "c"
UPDATE = "u"
ADD = "a"

Order = namedtuple('Order', ['order_id', 'timestamp', 'ticker', 'side', 'price', 'size'])


class OrderBook:
    """ OrderBook its a data structure that keep track of the orders inserted on multiple
    tickers and on both bid and ask side of the book"""

    def __init__(self):
        self.orders_dict = {}
        self.max_bid = defaultdict(int)
        self.min_ask = defaultdict(int)

    def _cancel(self, order_id: str):
        """ cancel keeps memory of side,price,and ticker, delete the order and
        search for a new min or max in the only case the order was on its side frontier"""
        order_tmp = self.orders_dict[order_id]
        del self.orders_dict[order_id]

        if order_tmp.side == ASK and self.min_ask[order_tmp.ticker] == order_tmp.price:
            self._update_best_ask(order_tmp.ticker)

        if order_tmp.side == BID and self.max_bid[order_tmp.ticker] == order_tmp.price:
            self._update_best_bid(order_tmp.ticker)

    def _update(self, order_id: str, size: int):
        """ update the size of an order """
        assert size > 0
        self.orders_dict[order_id] = self.orders_dict[order_id]._replace(size=size)

    def _add(self, order: Order):
        """ add an order to the book """
        assert int(order.size) > 0
        assert float(order.price) > 0
        tmp_price = int(float(order.price)*10**DEC)
        order = order._replace(price=tmp_price)
        self.orders_dict[order.order_id] = order
        if order.side == ASK:
            if self.min_ask[order.ticker] == 0:
                self.min_ask[order.ticker] = tmp_price
            else:
                self.min_ask[order.ticker] = min(self.min_ask[order.ticker], tmp_price)

        else:
            self.max_bid[order.ticker] = max(self.max_bid[order.ticker], tmp_price)

    def process_order(self, order: str):
        """ process takes a formatted operation and execute the appropriate operation
         on the order book"""
        timestamp, order_id, *action = order.split("|")
        if action[0] == CANCEL:
            self._cancel(order_id)
        elif action[0] == UPDATE:
            assert len(action) == 2
            self._update(order_id, int(action[1]))
        elif action[0] == ADD:
            assert len(action) == 5
            assert action[2] in [ASK, BID]
            self._add(Order(*([order_id, timestamp] + action[1:])))
        else:
            raise PermissionError("Operation %s not recognized" % action[0])

    def _update_best_bid(self, ticker: str):
        self.max_bid[ticker] = 0
        for _, order in self.orders_dict.items():
            if order.ticker == ticker and order.side == BID:
                self.max_bid[ticker] = max(self.max_bid[ticker], order.price)

    def _update_best_ask(self, ticker: str):
        self.min_ask[ticker] = 0
        for _, order in self.orders_dict.items():
            if order.ticker == ticker and order.side == ASK:
                if self.min_ask[ticker] == 0:
                    self.min_ask[ticker] = order.price
                self.min_ask[ticker] = min(self.min_ask[ticker], order.price)

    def get_best_bid_and_ask(self, ticker: str) -> (float, float):
        """ returns the best of bid and ask"""
        return self.max_bid[ticker] / 10**DEC, self.min_ask[ticker] / 10**DEC
