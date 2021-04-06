# -*- coding: utf-8 -*-
# Illustration du fonctionnement de unitest et difference entre setUp et setUpClass, tearDown et tearDownClass
import unittest
import flights_db
import logging.config

class flight_db_test(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls.created_order = 0
        cls.cities = ('San Francisco', 'Seattle', 'Denver', 'Frankfurt', 'London', 'Los Angeles', 'Paris', 'Portland', 'Sydney', 'Zurich')
        cls.sl = flights_db.sqlite_db()
        logging.config.fileConfig('../logging.conf')


    def test_city_exists(self):
        for city in self.cities:
            self.assertTrue(self.sl.city_exists (city))

    def test_get_flights(self):
        flights = self.sl.get_flights( 'Paris', 'London', '2021-02-05')
        logging.info(flights)
        self.assertEqual(len(flights), 8)

    def test_create_flight_order(self):
        flight = self.sl.get_flights( 'Paris', 'London', '2021-02-05')[0]
        logging.info( 'Order : %s %d %d %s', '2021-02-05', flight.FlightNumber, 3, 'First')
        order = self.sl.create_flight_order('IMHAH', '2021-02-05', flight.FlightNumber, 3, 'First')
        if (order == -1):
            logging.warning ('Nombre de billets commandés supérieur au places disponibles')
        elif (order == -2):
            logging.warning ('Le vol %s n\'existe pas pour cette date' , 3891)
        elif (order == -3):
             logging.warning ('Plus de place disponible sur le vol %d', 3891)
        else:
            self.created_order = order.OrderNumber
            self.assertGreater(order.OrderNumber, 80)
            print (order)


    def test_get_orders(self):
        #orders = flt.get_orders('', 'IMHAH')
        #self.assertEqual(len(orders), 0)
        orders = self.sl.get_orders('82', '')
        self.assertEqual(len(orders), 1)

    def test_update_flight_order(self):
        order = self.sl.update_flight_order('82', 'Economy', 'Zebra 0', 2)

    def test_delete_flight_order(self):
        orders = self.sl.get_orders('', 'IMHAH')
        for order in orders:
            self.sl.delete_flight_order(str(order.OrderNumber))



if __name__ == "__main__":
    unittest.main()
