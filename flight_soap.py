#!/usr/bin/env python
# encoding: utf8
from spyne import Application, rpc, ServiceBase, Iterable, Integer, Unicode, Fault
import http.cookies
import flights_db
from random import randrange
import config, datetime
from dateutil.relativedelta import relativedelta
from spyne.protocol.soap import Soap11
from wsgiref.simple_server import make_server
from spyne.server.wsgi import WsgiApplication
import logging.config


class FlightError(Fault):
    __namespace__ = 'ns.flights.py'
    def __init__(self, flightNumber):
        super(FlightError, self).__init__(
            faultcode='Filight.FlightNumber',
            faultstring='Filight  not found %s' % flightNumber)
class CityError(Fault):
    __namespace__ = 'ns.flights.py'
    def __init__(self, city):
        super(CityError, self).__init__(
            faultcode='Client.City',
            faultstring='City not in list  %s' % city)
class DateError(Fault):
    __namespace__ = 'ns.flights.py'
    def __init__(self, dt):
        super(DateError, self).__init__(
            faultcode='Client.Date',
            faultstring='Incorrect date format (use YYYY-MM-DD)  %s ' % dt)
class FlightsSOAP(ServiceBase):
    @rpc(Unicode, _returns=Iterable (flights_db.City))
    def GetCities(ctx, city_initials):
        db = flights_db.sqlite_db()
        db = flights_db.sqlite_db()
        if (city_initials is None):
            city_initials = ''
        cities = db.get_city(city_initials)
        if len(cities)==0:
            raise CityError(city_initials)
        else:
            return cities

    @rpc(Unicode, _returns=Iterable (flights_db.Flight))
    def GetRandomFlights(ctx, Count):
        db = flights_db.sqlite_db()
        random_fligths = []
        cities = db.get_city('')
        if Count is None:
            Count = 10
        else:
            Count = int (Count)
        for i in range(Count):
            futur = randrange(20) + 30
            date = datetime.date.today() + relativedelta(days=futur)
            date = date.strftime('%Y-%m-%d')
            DepartureCity = cities[randrange(10)].CityName
            ArrivalCity = DepartureCity
            while (ArrivalCity == DepartureCity):
                ArrivalCity = cities[randrange(10)].CityName

            flights = db.get_flights(DepartureCity, ArrivalCity, date)
            index = randrange(len(flights))
            random_fligths.append(flights[index])

        return random_fligths

    @rpc(Unicode, Unicode, Unicode, _returns=Iterable (flights_db.Flight))
    def GetFlights(ctx, DepartureCity, ArrivalCity, FlightDate):
        db = flights_db.sqlite_db()
        flights = db.get_flights(DepartureCity, ArrivalCity, FlightDate)
        if (flights==-1):
            raise CityError(DepartureCity)
            return
        elif (flights==-2):
            raise CityError(ArrivalCity)
            return
        elif (flights == -3):
            raise DateError(FlightDate)
            return
        else:
            return flights

    @rpc(Unicode, _returns=Iterable (flights_db.Flight))
    def GetFlight(ctx, FlightNumber):
        db = flights_db.sqlite_db()
        flights = db.get_flight(FlightNumber)
        if (flights==-1):
            raise FlightError(FlightNumber)
            return
        else:
            return flights

    @rpc(Unicode, Unicode, _returns=Iterable (flights_db.FlightOrder))
    def GetFlightOrders(ctx, CustomerName, OrderNumber):
        db = flights_db.sqlite_db()
        orders = db.get_orders(OrderNumber, CustomerName)
        return orders

    @rpc(Unicode, Unicode, Unicode, Unicode, Unicode,  _returns=flights_db.Order)
    def CreateFlightOrder(ctx, CustomerName, DepartureDate, FlightNumber, NumberOfTickets, FlightClass):
        db = flights_db.sqlite_db()
        NumberOfTickets = int(NumberOfTickets)
        new_order = db.create_flight_order(CustomerName, DepartureDate, FlightNumber, NumberOfTickets, FlightClass)
        if (new_order==-1):
            raise Fault(faultcode='SeatsAvailable.Error', faultstring='No more seats available for flight  ' + str(FlightNumber))
        elif (new_order==-2):
            raise Fault(faultcode='FlightNumber.Error', faultstring='Aucun vol   ' + str(FlightNumber))
        elif (new_order==-3):
            raise Fault(faultcode='SeatsAvailable.Error', faultstring='Aucun dispo   ' + str(FlightNumber))
        else:
            return (new_order)

    @rpc(Integer, _returns=Unicode)
    def DeleteFlightOrder(ctx, FlightOrder):
        db = flights_db.sqlite_db()
        rows = db.delete_flight_order (str(FlightOrder))
        return (str (rows > 0))

    @rpc(Integer, Unicode, Unicode, Unicode, Unicode, Unicode, _returns=flights_db.FlightOrder)
    def UpdateFlightOrder(ctx, OrderNumber, FlightNumber, DepartureDate, FlightClass, CustomerName, NumberOfTickets):
        db = flights_db.sqlite_db()
        NumberOfTickets = int(NumberOfTickets)
        OrderNumber = int (OrderNumber)
        FlightNumber = int (FlightNumber)
        upd_order = db.update_flight_order(OrderNumber, FlightNumber, DepartureDate, FlightClass, CustomerName, NumberOfTickets)
        if (upd_order == -1):
            raise Fault(faultcode='Class.Error', faultstring='Class not found ' + FlightClass)
        else:
            return (upd_order)

application = Application([FlightsSOAP], 'ns.flights.py',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logging.info("listening to http://127.0.0.1:" + config.port)
    logging.info("wsdl is at: http://localhost:" + config.port+ "/?wsdl")
    print("listening to http://127.0.0.1:"+config.port)
    print("wsdl is at: http://localhost:"+ config.port +"/?wsdl")

    server = make_server('127.0.0.1', int(config.port), wsgi_application)
    server.serve_forever()