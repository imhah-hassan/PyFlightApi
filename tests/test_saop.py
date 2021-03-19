# -*- coding: utf-8 -*-
# Illustration du fonctionnement de unitest et difference entre setUp et setUpClass, tearDown et tearDownClass
import unittest
import logging
from zeep import Client

class test_soap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.INFO, filename='test_soap.log', filemode='w',
                            format='%(name)s - %(levelname)s - %(message)s')

        cls.wsdl = "http://localhost:8000/?wsdl"
        cls.client = Client(cls.wsdl)
        cls.fligth_date = '2021-03-23'
        cls.customer_name = 'IMHAH'
        logging.info ('Connected to saop %s ', cls.wsdl)

    @unittest.skip
    def test_GetFlightOrders(self):
        request_data = {'CustomerName': self.customer_name,
                        'OrderNumber': ''}
        response = self.client.service.GetFlightOrders(**request_data)
        self.assertEqual(len(response), 2)


    @unittest.skip
    def test_GetFlights(self):
        request_data = {'DepartureCity': 'IMHAH',
                        'ArrivalCity': '',
                        'FlightDate':''}
        try:
            response = self.client.service.GetFlights(**request_data)
            print (response)
        except Exception as e:
            print(e)

        request_data = {'DepartureCity': 'Paris',
                        'ArrivalCity': '',
                        'FlightDate':''}
        response = self.client.service.GetFlights(**request_data)
        print(response)

        request_data = {'DepartureCity': 'Paris',
                        'ArrivalCity': 'London',
                        'FlightDate':''}
        response = self.client.service.GetFlights(**request_data)
        print(response)
        request_data = {'DepartureCity': 'Paris',
                        'ArrivalCity': 'London',
                        'FlightDate': self.fligth_date}
        response = self.client.service.GetFlights(**request_data)
        print(response)


    # @unittest.skip
    def test_CreateFlightOrder(self):
        request_data = {'DepartureCity': 'Paris',
                        'ArrivalCity': 'London',
                        'FlightDate': '2021-03-23'}
        response = self.client.service.GetFlights(**request_data)
        self.assertEqual (response[0].FlightNumber, 10487)
        self.assertEqual (response[0].DepartureTime, '08:00 AM')

        request_data = {'CustomerName': 'IMHAH',
                        'DepartureDate': '2021-03-23',
                        'FlightNumber': 27861,                       # response[0].FlightNumber
                        'NumberOfTickets': 2,
                        'FlightClass': 'Business'}
        try:
            response = self.client.service.CreateFlightOrder(**request_data)
            self.assertEqual (response.TotalPrice, 214.94)
            self.assertGreater(response.OrderNumber, 80)
        except Exception as e:
            print (e)

    @unittest.skip
    def test_DeleteFlightOrder(self):
        request_data = {'CustomerName': 'Economy',
                        'OrderNumber': ''}
        response = self.client.service.GetFlightOrders(**request_data)
        for order in response:
            request_data = {'FlightOrder': order.OrderNumber}
            response = self.client.service.DeleteFlightOrder(**request_data)
            self.assertEqual(response, 'True')


if __name__ == "__main__":
    unittest.main()
