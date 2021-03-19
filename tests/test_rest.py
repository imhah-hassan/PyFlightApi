# -*- coding: utf-8 -*-
# Illustration du fonctionnement de unitest et difference entre setUp et setUpClass, tearDown et tearDownClass
import unittest
import logging
import requests, json

class test_rest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.INFO, filename='test_soap.log', filemode='w',
                            format='%(name)s - %(levelname)s - %(message)s')


    @unittest.skip
    def test_GetFlightOrders(self):
        pass

    # @unittest.skip
    def test_GetFlights(self):
        resp = requests.get ('http://localhost:5000/flights_api/v1/resources/Flights?DepartureCity=Paris&ArrivalCity=London&Date=2021-12-31')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        print (data)
        resp = requests.get ('http://localhost:5000/flights_api/v1/resources/Flights?DepartureCity=Casablanca&ArrivalCity=London&Date=2021-12-31')
        self.assertEqual(resp.status_code, 500)
        data = json.loads(resp.content)

    @unittest.skip
    def test_GetFlight(self):
        resp = requests.get ('http://localhost:5000/flights_api/v1/resources/Flights/45267')
        self.assertEqual(resp.status_code, 404)
        data = json.loads(resp.content)
        print (data)

        resp = requests.get ('http://localhost:5000/flights_api/v1/resources/Flights/10499')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        print (data)

    # @unittest.skip
    def test_CreateFlightOrder(self):
        header = {"content-type":"application/json"}
        data = {"DepartureDate":"2021-12-31", "FlightNumber":"10535","CustomerName":"IMHAH","NumberOfTickets":"2", "Class":"Economy"}
        resp = requests.post ('http://localhost:5000/flights_api/v1/resources/FlightOrders', data=json.dumps(data), headers=header)
        self.assertEqual(resp.status_code, 200)


    @unittest.skip
    def test_DeleteFlightOrder(self):
        pass

    def test_GetOrdersByCustomerName(self):
        resp = requests.get ('http://localhost:5000/flights_api/v1/resources/GetOrdersByCustomerName?CustomerName=IMHAH')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        print(data)

if __name__ == "__main__":
    unittest.main()
