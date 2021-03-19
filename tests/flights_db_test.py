# -*- coding: utf-8 -*-
# Illustration du fonctionnement de unitest et difference entre setUp et setUpClass, tearDown et tearDownClass
import unittest
import flights_db as flt
import logging.config

class flight_db_test(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls.created_order = 0
        logging.config.fileConfig('../logging.conf')

    @unittest.skip
    def test_city_exists(self):
        self.assertTrue(flt.city_exists ('San Francisco'))
        self.assertTrue(flt.city_exists ('Seattle'))
        self.assertTrue(flt.city_exists ('Denver'))
        self.assertTrue(flt.city_exists ('Frankfurt'))
        self.assertTrue(flt.city_exists ('London'))
        self.assertTrue(flt.city_exists ('Los Angeles'))
        self.assertTrue(flt.city_exists ('Paris'))
        self.assertTrue(flt.city_exists ('Portland'))
        self.assertTrue(flt.city_exists ('Sydney'))
        self.assertTrue(flt.city_exists ('Zurich'))

    @unittest.skip
    def test_get_flights(self):
        flights = flt.get_flights( 'Paris', 'London', '2021-02-05')
        logging.info(flights)
        self.assertEqual(len(flights), 8)

    @unittest.skip
    def test_get_orders(self):
        #orders = flt.get_orders('', 'IMHAH')
        #self.assertEqual(len(orders), 0)
        orders = flt.get_orders(180, '')
        self.assertEqual(len(orders), 0)

    # @unittest.skip
    def test_create_flight_order(self):
        flight = flt.get_flights( 'Paris', 'London', '2021-02-05')[0]
        logging.info( 'Order : %s %d %d %s', '2021-02-05', flight.FlightNumber, 3, 'First')
        order = flt.create_flight_order('IMHAH', '2021-02-05', flight.FlightNumber, 3, 'First')
        if (order == -1):
            logging.warning ('Nombre de billets commandés supérieur au places disponibles')
        elif (order == -2):
            logging.warning ('Le vol %s n\'existe pas pour cette date' , 3891)
        elif (order == -3):
             logging.warning ('Plus de place disponible sur le vol %d', 3891)
        else:
            self.created_order = order.OrderNumber
            self.assertGreater(order.OrderNumber, 80)

    @unittest.skip
    def test_update_flight_order(self):
        order = flt.update_flight_order(153, 'Economy', 'Zebra 0', 2)

    @unittest.skip
    def atest_delete_flight_order(self):
        orders = flt.get_orders('', 'IMHAH')
        for order in orders:
            flt.delete_flight_order(order.OrderNumber)



if __name__ == "__main__":
    unittest.main()
