# -*- coding: utf-8 -*-
# Illustration du fonctionnement de unitest et difference entre setUp et setUpClass, tearDown et tearDownClass
import pytest
import requests, json
url = 'http://localhost:5000'

def test_search_flight():
    resp = requests.get(url + '/Flights?DepartureCity=Paris&ArrivalCity=London&Date=2024-12-23')
    assert resp.status_code==200
    data = json.loads(resp.content)
    assert data[0]['ArrivalCity'] == 'London'

def test_search_flight_city():
    resp = requests.get(url + '/Flights?DepartureCity=Cairo&ArrivalCity=London&Date=2024-12-23')
    assert resp.status_code==200
    data = json.loads(resp.content)
    assert data['error'].startswith('Invalid')

def test_search_flight_date():
    resp = requests.get(url + '/Flights?DepartureCity=Paris&ArrivalCity=London&Date=$238765')
    assert resp.status_code==200
    data = json.loads(resp.content)
    print (data)