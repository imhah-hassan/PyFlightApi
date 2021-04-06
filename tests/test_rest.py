# -*- coding: utf-8 -*-
# Illustration du fonctionnement de unitest et difference entre setUp et setUpClass, tearDown et tearDownClass
import unittest
import logging
import requests, json
import config
from random import randrange


class test_rest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.INFO, filename='test_soap.log', filemode='w',
                            format='%(name)s - %(levelname)s - %(message)s')
        cls.date = '2021-12-21'
        cls.flight = 0
        cls.order=0


    @property
    def flight(self):
        return self.__flight

    # @unittest.skip
    def test_a_GetFlights(self):
        resp = requests.get (config.url + '/Flights?DepartureCity=Paris&ArrivalCity=London&Date='+ self.date)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.__class__.flight = data[0]['FlightNumber'];
        print (data)
        resp = requests.get (config.url + '/Flights?DepartureCity=Casablanca&ArrivalCity=London&Date='+ self.date)
        self.assertEqual(resp.status_code, 500)
        data = json.loads(resp.content)

        resp = requests.get (config.url + '/Flights?DepartureCity=&ArrivalCity=&Date='+ self.date)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        for i in range(20):
            random_flight = data[randrange(len(data))]
            print(random_flight['DepartureCity'], random_flight['ArrivalCity'], random_flight['FlightNumber'], self.date)

    #@unittest.skip
    def test_b_GetFlight(self):
        resp = requests.get (config.url + '/Flights/' + str(self.__class__.flight+9999))
        self.assertEqual(resp.status_code, 404)
        data = json.loads(resp.content)
        print (data)

        resp = requests.get (config.url + '/Flights/'+ str(self.__class__.flight))
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        print (data)

    #@unittest.skip
    def test_c_CreateFlightOrder(self):
        header = {"content-type":"application/json"}
        data = {"DepartureDate":self.date, "FlightNumber":self.__class__.flight,"CustomerName":"IMHAH","NumberOfTickets":"2", "Class":"Economy"}
        resp = requests.post (config.url + '/FlightOrders', data=json.dumps(data), headers=header)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.__class__.order = data['OrderNumber']

    @unittest.skip
    def test_DeleteFlightOrder(self):
        pass

    #@unittest.skip
    def test_d_GetOrdersByCustomerName(self):
        resp = requests.get (config.url + '/FlightOrders?CustomerName=IMHAH')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        print(data)


    #@unittest.skip
    def test_e_GetOrdersByOrderNumber(self):
        resp = requests.get(config.url + '/FlightOrders?OrderNumber=' + str(self.__class__.order ))
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        print(data)

    #@unittest.skip
    def test_f_DeleteFlightOrder(self):
        print(str(self.__class__.order ))
        resp = requests.delete(config.url + '/FlightOrders/' + str(self.__class__.order ))
        self.assertEqual(resp.status_code, 200)
