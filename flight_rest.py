#!C:\Apps\Python\Python38 python
# encoding: utf8
import flask
from flask import request, jsonify, Response, make_response
import json
import flights_db
import logging.config
import config, datetime
from random import randrange
from dateutil.relativedelta import relativedelta

import requests
import urllib.parse
import jwt
from functools import wraps

app = flask.Flask(__name__)
app.config['SECRET_KEY']='XBhbnJM8IaQwaWVVv9RK'

logging.config.fileConfig('logging.conf')
print ("FlightsApp Rest Api")
print ("Listening on http://localhost:" + str(config.port))
print ("Sample request :  http://localhost:"+str(config.port)+"/Flights/10487")


@app.route('/', methods=['GET'])
def home():
    return '''<h1>FlightsApp Rest Api</h1>
<p>Listening on http://localhost:{0}</p>
<p>Sample request :
http://localhost:{0}/Flights/?DepartureCity=Paris&ArrivalCity=London&Date=2021-09-03
</p>
'''.format (str(config.port))


# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        db = flights_db.sqlite_db()
        token = None
        # ensure the jwt-token is passed with the headers
        if 'Authorization' in request.headers:
            token = str(request.headers['Authorization'])
            token = token.replace(' ', '').replace('Bearer:', '')
        if not token: # throw error if no token provided
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        try:
           # decode the token to obtain user public_id
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db.get_user_by_id(data['public_id'])[0]
        except:
            return make_response(jsonify({"message": "Invalid token!"}), 401)
         # Return the user information attached to the token
        return f(current_user, *args, **kwargs)
    return decorator


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    db = flights_db.sqlite_db()
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    user = db.get_user(auth.username)[0]

    if user.password == auth.password:
        token = jwt.encode(
            {'public_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})


#   GET http://localhost:5000/Cities?CityName=Paris
@app.route('/Cities', methods=['GET'])
def GetCities():
    db = flights_db.sqlite_db()
    city_initials = request.args.get('CityCode')
    if (city_initials is None):
        city_initials=''
    cities = db.get_city(city_initials)
    json_string = json.dumps([ob.__dict__ for ob in cities])
    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response

# POST  http://localhost:5000/Cities
#   {
#     "CityInitials":"CMN",
#     "CityName":"Casablanca"
# }
@app.route('/Cities', methods=['POST'])
@token_required
def CreateCity(user):
    if user.profil == 'Admin':
        db = flights_db.sqlite_db()
        if (request.is_json):
            data = request.get_json()
            city = db.create_city(data['CityInitials'], data['CityName'])
        json_string = json.dumps(city.__dict__)
    else:
        json_string = {"false": "Admin profil needed to delete city "}

    response = make_response(json_string,201,)
    response.headers["Content-Type"] = "application/json"
    return response

#  PATCH http://localhost:5000/Cities/CMN
#   {"TicketPrice":185.2}
@app.route('/Cities/<CityInitials>', methods=['PATCH'])
@token_required
def UpdateCity(user, CityInitials):
    if user.profil == 'Admin':
        db = flights_db.sqlite_db()
        upd_city = db.get_city(CityInitials)
        if len(upd_city)==0:
            json_string = {"false": "City not found  {0} ".format(CityInitials)}
        elif (request.is_json):
            data = request.get_json()
            new_city_initials = data['CityInitials']
            new_city_name = data['CityName']
            upd_city = db.update_city(CityInitials, new_city_initials, new_city_name)
            json_string = json.dumps(upd_city.__dict__)
    else:
        json_string = {"false": "Admin profil needed to delete city "}

    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response


# DELETE  http://localhost:5000/Cities/Casablanca
@app.route('/Cities/<CityInitials>', methods=['DELETE'])
@token_required
def DeleteCity(user, CityInitials):
    if user.profil == 'Admin':
        db = flights_db.sqlite_db()
        rows = db.delete_city(CityInitials)
        if (rows==1):
            json_string = {"true": "City deleted {0} ".format(CityInitials)}
        elif rows==0:
            json_string = {"false": "City not found  {0} ".format(CityInitials)}
        elif rows==-1:
            json_string = {"false": "Flight exists from or to this city  {0} ".format(CityInitials)}
    else:
        json_string = {"false": "Admin profil needed to delete city "}

    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response

# GET http://localhost:5000/RandomFlights?Count=10
@app.route('/RandomFlights', methods=['GET'])
def GetRandomFlights():
    db = flights_db.sqlite_db()
    random_fligths = []
    cities = db.get_city('')
    if (request.args.get('Count') is None):
        Count = 10
    else:
        Count = int(request.args.get('Count'))
    for i in range (Count):
        futur = randrange (20) + 30
        date = datetime.date.today()+ relativedelta(days=futur)
        date = date.strftime('%Y-%m-%d')
        DepartureCity = cities[randrange(10)].CityName
        ArrivalCity = DepartureCity
        while (ArrivalCity == DepartureCity):
            ArrivalCity = cities[randrange(10)].CityName

        flights = db.get_flights(DepartureCity, ArrivalCity, date)
        index = randrange (len(flights))
        random_fligths.append (flights[index])

    json_string = json.dumps([ob.__dict__ for ob in random_fligths])
    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response


#   GET http://localhost:5000/Flights?DepartureCity=Paris&ArrivalCity=Denver&Date=2021-12-08
@app.route('/Flights', methods=['GET'])
def GetFlights():
    db = flights_db.sqlite_db()
    DepartureCity = "" if request.args.get('DepartureCity') is None else request.args.get('DepartureCity')
    ArrivalCity = "" if request.args.get('ArrivalCity') is None else request.args.get('ArrivalCity')
    FlightDate = "" if request.args.get('Date') is None else request.args.get('Date')
    flights = db.get_flights(DepartureCity, ArrivalCity, FlightDate)
    json_string = ''
    if (flights == -1):
        json_string = {"error": "Invalid DepartureCity : {0} ".format(DepartureCity)}
    elif (flights == -2):
        json_string = {"error": "Invalid ArrivalCity : {0} ".format(ArrivalCity)}
    else:
        json_string = json.dumps([ob.__dict__ for ob in flights])
    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response

#   GET http://localhost:5000/Flights/16939
@app.route('/Flights/<flight_number>', methods=['GET'])
def GetFlightByNumber(flight_number):
    db = flights_db.sqlite_db()
    flight = db.get_flight(flight_number)
    if (flight == -1):
        json_string = {"error": "Unkown Flight  : {0} ".format(flight_number)}
    else:
        json_string = json.dumps(flight.__dict__)
    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response

#  PATCH http://localhost:5000/Flights/16939
#   {"TicketPrice":185.2}
@app.route('/Flights/<flight_number>', methods=['PATCH'])
@token_required
def UpdateFlightPrice(user, flight_number):
    db = flights_db.sqlite_db()
    upd_fligth = db.get_flight(flight_number)
    if upd_fligth == -1:
        response = make_response({"error":"Unkown flight"}, 200, )
        response.headers["Content-Type"] = "application/json"
        return response

    json_string = ""
    if (request.is_json):
        data = request.get_json()
        upd_fligth = db.update_flight_price(flight_number, data)
        json_string = json.dumps(upd_fligth.__dict__)

    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response

# POST  http://localhost:5000/Flights
#   {"Airline":"AF", "ArrivalCity":"Casablanca", "ArrivalTime":"10:30 AM", "DepartureCity":"Paris", "DepartureTime":"08:00 AM", "FlightNumber":99558, "Price":185.2, "DayOfWeek":"Monday"}
@app.route('/Flights', methods=['POST'])
@token_required
def CreateFlight(user):
    if user.profil == 'Admin':
        db = flights_db.sqlite_db()
        if (request.is_json):
            data = request.get_json()
            flt_number = db.create_flight(data)
            if flt_number>0:
                flt = db.get_flight(flt_number)
            else:
                flt = {"error":"Error creating flight"}
        json_string = json.dumps(flt.__dict__)
    else:
        json_string = {"false": "Admin profil needed to delete city "}
    response = make_response(json_string,201,)
    response.headers["Content-Type"] = "application/json"
    return response

# DELETE  http://localhost:5000/Flights/12654
@app.route('/Flights/<FlightNumber>', methods=['DELETE'])
@token_required
def DeleteFlight(user, FlightNumber):
    if user.profil == 'Admin':
        db = flights_db.sqlite_db()
        rows = db.delete_flight(FlightNumber)
        if (rows==1):
            json_string = {"true": "Flight deleted {0} ".format(FlightNumber)}
        elif rows==0:
            json_string = {"false": "FlightNumber not found  {0} ".format(FlightNumber)}
    else:
        json_string = {"false": "Admin profil needed to delete city "}
    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response


# GET  http://localhost:5000/FlightOrders?CustomerName=IMHAH
@app.route('/FlightOrders', methods=['GET'])
def GetOrders():
    db = flights_db.sqlite_db()
    CustomerName = request.args.get('CustomerName')
    orders = db.get_orders('', CustomerName)
    json_string = json.dumps([ob.__dict__ for ob in orders])
    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response

# GET  http://localhost:5000/FlightOrders/81
@app.route('/FlightOrders/<OrderNumber>', methods=['GET'])
def GetOrder(OrderNumber):
    db = flights_db.sqlite_db()
    orders = db.get_orders(OrderNumber, '')
    if (len(orders)>0):
        json_string = json.dumps(orders[0].__dict__)
    else:
        json_string = {"error":"invalid order number {0}".format(OrderNumber)}
    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response

# DELETE  http://localhost:5000/FlightOrders/81
@app.route('/FlightOrders/<OrderNumber>', methods=['DELETE'])
def DeleteOrder(OrderNumber):
    db = flights_db.sqlite_db()
    rows = db.delete_flight_order(OrderNumber)
    if (rows==1):
        json_string = {"true": "Order deleted {0} ".format(OrderNumber)}
    else:
        json_string = {"false": "Order not found  {0} ".format(OrderNumber)}
    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response

# DELETE  http://localhost:5000/FlightOrders
@app.route('/FlightOrders', methods=['DELETE'])
def DeleteAllOrders():
    db = flights_db.sqlite_db()
    orders = db.delete_all_orders();
    json_string = json.dumps([ob.__dict__ for ob in orders])
    response = make_response(json_string,200,)
    response.headers["Content-Type"] = "application/json"
    return response


# POST  http://localhost:5000/FlightOrders
#   {   "DepartureDate":"2021-12-08",
#     "FlightNumber":16939,
#     "CustomerName": "IMHAH",
#     "NumberOfTickets":2,
#     "Class":"Economy"
# }
@app.route('/FlightOrders', methods=['POST'])
def CreateOrder():
    db = flights_db.sqlite_db()
    if (request.is_json):
        data = request.get_json()
        DepartureDate = data['DepartureDate']
        if (not db.date_in_the_past(DepartureDate)):
            return (jsonify({"error": "Flight date cannot be in the past : {0} ".format(DepartureDate)}), 500)
        json_string=''
        CustomerName = data['CustomerName']
        FlightNumber = data['FlightNumber']
        NumberOfTickets = data['NumberOfTickets']
        FlightClass = data['Class']
        new_order = db.create_flight_order(CustomerName, DepartureDate, FlightNumber, NumberOfTickets, FlightClass)
        if (new_order==-1):
            flight = db.get_flight(FlightNumber)
            json_string = jsonify({"error": "Ordered tickets too high. Seats available : {0} ".format(flight.SeatsAvailable)})
            response = make_response(json_string, 500, )
            response.headers["Content-Type"] = "application/json"
            return response
        elif (new_order==-2):
            json_string = jsonify({"error": "Unkown Flight  : {0} ".format(FlightNumber)})
            response = make_response(json_string, 500, )
            response.headers["Content-Type"] = "application/json"
            return response
        elif (new_order == -4):
            return (jsonify({"error": "Flight not exists ".format(FlightNumber)}), 500)
        elif (new_order==-3):
            json_string = jsonify({"error": "No more seats available in flight  : {0} ".format(FlightNumber)})
            response = make_response(json_string, 500, )
            response.headers["Content-Type"] = "application/json"
            return response
        elif (new_order == -5):
            json_string = jsonify({"error": "Number Of Tickets cannot be more than 10 "})
            response = make_response(json_string, 500, )
            response.headers["Content-Type"] = "application/json"
            return response
        elif (new_order == -6):
            return (jsonify({"error": "Flight not available for departure date ".format(FlightNumber)}), 500)
        else:
            json_string = json.dumps(new_order.__dict__)
            response = make_response(json_string, 200, )
            response.headers["Content-Type"] = "application/json"
            return response
    else:
        json_string = jsonify({"error": "Invalid json format  "})
        response = make_response(json_string,500,)
        response.headers["Content-Type"] = "application/json"
        return response

#   PATCH http://localhost:5000/FlightOrders/81
# {   "DepartureDate":"2021-12-08",
#     "FlightNumber":16939,
#     "CustomerName": "IMHAH",
#     "NumberOfTickets":2,
#     "Class":"Economy"
# }
@app.route('/FlightOrders/<OrderNumber>', methods=['PATCH'])
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
        upd_order = db.update_flight_order(OrderNumber, FlightNumber, DepartureDate, FlightClass, CustomerName, NumberOfTickets)
        if (upd_order==0):
            return (jsonify({"error": "Order not found : {0} ".format(OrderNumber)}), 500)
        elif (upd_order==-1):
            return (jsonify({"error": "Ordered tickets too high : {0} ".format(FlightNumber)}), 500)
        elif (upd_order==-2):
            return (jsonify({"error": "Unkown Flight  : {0} ".format(FlightNumber)}), 500)
        elif (upd_order==-3):
            return (jsonify({"error": "No more seats available in flight  : {0} ".format(FlightNumber)}), 500)
        elif (upd_order == -4):
            return (jsonify({"error": "Ordered tickets cannot be more than 10 ".format(FlightNumber)}), 500)
        elif (upd_order == -5):
            return (jsonify({"error": "Flight not available for departure date ".format(FlightNumber)}), 500)
        else:
            json_string = json.dumps(upd_order.__dict__)
            response = make_response(json_string, 200, )
            response.headers["Content-Type"] = "application/json"
            return response
    else:
        return (jsonify({"error": "Invalid json format  "}), 500)

app.run(host='0.0.0.0', port=config.port)