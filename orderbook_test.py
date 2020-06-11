""" orderbook execution tests"""

import unittest
from orderbook import OrderBook


class OrderBookTest(unittest.TestCase):
    """ OrderBookTest collection of class test"""
    def test_cancel_invalid(self):
        """ ancel missing order """
        obj = OrderBook()
        self.assertRaises(KeyError, obj.process_order, "1568390243|abbb11|c")

    def test_update_invalid(self):
        """ check: invalid size and update missing order"""
        obj = OrderBook()
        # invalid size
        self.assertRaises(AssertionError, obj.process_order, "1568390243|abbb11|u|0")
        # update missing order
        self.assertRaises(KeyError, obj.process_order, "1|abbb11|u|1")

    def test_add_invalid(self):
        """ check: invalid type , order size, order price"""
        obj = OrderBook()
        # invalid type
        self.assertRaises(AttributeError, obj.process_order, 11)
        # invalid order size
        self.assertRaises(AssertionError, obj.process_order,
                          "1568390243|abbb11|a|AAPL|B|209.00000|0")
        # invalid order price
        self.assertRaises(AssertionError, obj.process_order,
                          "1568390243|abbb11|a|AAPL|B|-209.00000|2")

    def test_process_order(self):
        """ check: order,add,update,missing parameters; unsupported action"""
        obj = OrderBook()
        # missing parameters
        self.assertRaises(IndexError, obj.process_order, "1568390243|abbb11")
        # add missing parameters
        self.assertRaises(AssertionError, obj.process_order, "1568390243|abbb11|a")
        # update missing parameters
        self.assertRaises(AssertionError, obj.process_order, "1568390243|abbb11|u")
        # unsupported action
        self.assertRaises(PermissionError, obj.process_order, "1568390243|abbb11|x")

    def test_sequence1(self):
        """ test sequence 1: add, update, cancel """
        obj = OrderBook()
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (0, 0))
        obj.process_order("1568390243|abbb11|a|AAPL|B|209.00000|100")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.0, 0.0))
        obj.process_order("1568390244|abbb11|u|101")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.0, 0.0))
        obj.process_order("1568390245|abbb11|c")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (0.0, 0.0))

    def test_sequence2(self):
        """ test sequence 1: add ,add ,update, update, cancel"""
        obj = OrderBook()
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (0, 0))
        obj.process_order("1568390201|abbb11|a|AAPL|B|209.00000|100")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.0, 0))
        obj.process_order("1568390202|abbb12|a|AAPL|S|210.00000|10")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.0, 210.0))
        obj.process_order("1568390204|abbb11|u|10")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.0, 210.0))
        obj.process_order("1568390203|abbb12|u|101")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.0, 210.0))
        obj.process_order("1568390243|abbb11|c")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (0, 210.0))

    def test_sequence3(self):
        """ test sequence 1: add ,add ,add,add,cancel,cancel """
        obj = OrderBook()
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (0, 0))
        obj.process_order("1568390201|abbb11|a|AAPL|B|209.00000|100")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.0, 0))
        obj.process_order("1568390201|abbb12|a|AAPL|B|209.50000|100")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.5, 0))
        obj.process_order("1568390203|abbb13|a|AAPL|S|210.00000|10")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.5, 210.0))
        obj.process_order("1568390204|abbb14|a|AAPL|S|209.90000|10")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.5, 209.9))
        obj.process_order("1568390243|abbb12|c")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.0, 209.9))
        obj.process_order("1568390244|abbb14|c")
        self.assertEqual(obj.get_best_bid_and_ask('AAPL'), (209.0, 210.0))
