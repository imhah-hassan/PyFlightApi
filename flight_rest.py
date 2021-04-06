#!C:\Apps\Python\Python38 python
# encoding: utf8
import flask
from flask import request, jsonify, Response
import json
import flights_db
import logging.config

import requests

app = flask.Flask(__name__)

logging.config.fileConfig('logging.conf')
print ("Lisening on http://127.0.0.1:5000")


@app.route('/', methods=['GET'])
def home():
    return '''<h1>FlightsApp Rest Api</h1>
<p>Lisening on http://127.0.0.1:5000</p>
<p>Sample request :
http://127.0.0.1:5000/flights_api/v1/resources/Flights/?DepartureCity=Paris&ArrivalCity=London&Date=2021-09-03
</p>
'''


# A route to return all of the available entries in our catalog.
@app.route('/flights_api/v1/resources/Flights', methods=['GET'])
def GetFlights():
    db = flights_db.sqlite_db()
    DepartureCity = request.args.get('DepartureCity')
    ArrivalCity = request.args.get('ArrivalCity')
    FlightDate = request.args.get('Date')
    flights = db.get_flights(DepartureCity, ArrivalCity, FlightDate)
    if (flights == -1):
        json_string = jsonify({"error": "Invalid DepartureCity : {0} ".format(DepartureCity)}), 500
    else:
        json_string = json.dumps([ob.__dict__ for ob in flights])
    return json_string

@app.route('/flights_api/v1/resources/Flights/<flight_number>', methods=['GET'])
def GetFlightByNumber(flight_number):
    db = flights_db.sqlite_db()
    flight = db.get_flight(flight_number)
    if (flight == -1):
        json_string = jsonify({"error": "Unkown Flight  : {0} ".format(flight_number)}), 404
    else:
        json_string = json.dumps(flight[0].__dict__)
    return json_string


# A route to return all of the available entries in our catalog.
@app.route('/flights_api/v1/resources/FlightOrders', methods=['GET'])
def GetOrders():
    db = flights_db.sqlite_db()
    CustomerName = request.args.get('CustomerName')
    OrderNumber = request.args.get('OrderNumber')
    orders = db.get_orders(OrderNumber, CustomerName)
    json_string = json.dumps([ob.__dict__ for ob in orders])
    return json_string

# A route to return all of the available entries in our catalog.
@app.route('/flights_api/v1/resources/FlightOrders/<OrderNumber>', methods=['GET'])
def GetOrder(OrderNumber):
    db = flights_db.sqlite_db()
    orders = db.get_orders(OrderNumber, '')
    json_string = json.dumps([ob.__dict__ for ob in orders])
    return json_string

# A route to return all of the available entries in our catalog.
@app.route('/flights_api/v1/resources/FlightOrders/<OrderNumber>', methods=['DELETE'])
def DeleteOrder(OrderNumber):
    db = flights_db.sqlite_db()
    rows = db.delete_flight_order(OrderNumber)
    if (rows==1):
        json_string = jsonify({"true": "Oder deleted {0} ".format(OrderNumber)}), 200
    else:
        json_string = jsonify({"false": "Oder not found  {0} ".format(OrderNumber)}), 200
    return json_string

# A route to return all of the available entries in our catalog.
@app.route('/flights_api/v1/resources/FlightOrders', methods=['DELETE'])
def DeleteAllOrders():
    db = flights_db.sqlite_db()
    db.delete_all_orders();
    return ('{"result":"ok"}')


@app.route('/flights_api/v1/resources/FlightOrders', methods=['POST'])
def CreateOrder():
    db = flights_db.sqlite_db()
    if (request.is_json):
        data = request.get_json()
        DepartureDate = data['DepartureDate']
        if (not db.date_in_the_past(DepartureDate)):
            return (jsonify({"error": "Flight date cannot be in the past : {0} ".format(DepartureDate)}), 500)

        CustomerName = data['CustomerName']
        FlightNumber = data['FlightNumber']
        NumberOfTickets = data['NumberOfTickets']
        FlightClass = data['Class']
        new_order = db.create_flight_order(CustomerName, DepartureDate, FlightNumber, NumberOfTickets, FlightClass)
        if (new_order==-1):
            return (jsonify({"error": "Ordered tickets too high : {0} ".format(FlightNumber)}), 500)
        elif (new_order==-2):
            return (jsonify({"error": "Unkown Flight  : {0} ".format(FlightNumber)}), 500)
        elif (new_order==-3):
            return (jsonify({"error": "No more seats available in flight  : {0} ".format(FlightNumber)}), 500)
        else:
            return Response(json.dumps(new_order.__dict__), mimetype='application/json')
    else:
        return (jsonify({"error": "Invalid json format  "}), 500)

@app.route('/flights_api/v1/resources/FlightOrders/<OrderNumber>', methods=['PATCH'])
def UpdateOrder(OrderNumber):
    db = flights_db.sqlite_db()
    if (request.is_json):
        data = request.get_json()
        DepartureDate = data['DepartureDate']
        if (not db.date_in_the_past(DepartureDate)):
            return (jsonify({"error": "Flight date cannot be in the past : {0} ".format(DepartureDate)}), 500)
        CustomerName = data['CustomerName']
        FlightNumber = data['FlightNumber']
        NumberOfTickets = data['NumberOfTickets']
        FlightClass = data['Class']
        upd_order = db.update_flight_order(OrderNumber, CustomerName, DepartureDate, FlightNumber, NumberOfTickets, FlightClass)
        if (upd_order==-1):
            return (jsonify({"error": "Ordered tickets too high : {0} ".format(FlightNumber)}), 500)
        elif (upd_order==-2):
            return (jsonify({"error": "Unkown Flight  : {0} ".format(FlightNumber)}), 500)
        elif (upd_order==-3):
            return (jsonify({"error": "No more seats available in flight  : {0} ".format(FlightNumber)}), 500)
        else:
            return Response(json.dumps(upd_order.__dict__), mimetype='application/json')
    else:
        return (jsonify({"error": "Invalid json format  "}), 500)

app.run()

