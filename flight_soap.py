#!/usr/bin/env python
# encoding: utf8
from wsgiref.simple_server import make_server
from spyne import Application, rpc, ServiceBase, Iterable, Integer, Unicode, Fault
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import flights_db
import logging.config

class CityError(Fault):
    __namespace__ = 'ns.flights.py'
    def __init__(self, city):
        super(CityError, self).__init__(
                faultcode='Client.City',
                faultstring='City not in list  %s' % city)

class FlightsSOAP(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, _returns=Iterable (flights_db.Flight))
    def GetFlights(ctx, DepartureCity, ArrivalCity, FlightDate):
        flights = flights_db.get_flights(DepartureCity, ArrivalCity, FlightDate)
        if (flights==-1):
            raise CityError(DepartureCity)
            return
        elif (flights==-2):
            raise CityError(ArrivalCity)
            return
        else:
            return flights


    @rpc(Unicode, Unicode, _returns=Iterable (flights_db.FlightOrder))
    def GetFlightOrders(ctx, CustomerName, OrderNumber):
        orders = flights_db.get_orders(OrderNumber, CustomerName)
        return orders

    @rpc(Unicode, Unicode, Unicode, Unicode, Unicode,  _returns=flights_db.Order)
    def CreateFlightOrder(ctx, CustomerName, DepartureDate, FlightNumber, NumberOfTickets, FlightClass):
        new_order = flights_db.create_flight_order(CustomerName, DepartureDate, FlightNumber, NumberOfTickets, FlightClass)
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
        rows = flights_db.delete_flight_order (FlightOrder)
        return (str (rows > 0))

    @rpc(Integer, Unicode, Unicode, Unicode, _returns=Unicode)
    def UpdateFlightOrder(ctx, OrderNumber, Class, CustomerName, NumberOfTickets):
        rows = flights_db.update_flight_order(OrderNumber, Class, CustomerName, NumberOfTickets)
        if (rows == -1):
            raise Fault(faultcode='Class.Error', faultstring='Class not found ' + Class)
        else:
            return (str(rows > 0))



application = Application([FlightsSOAP], 'ns.flights.py',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

wsgi_application = WsgiApplication(application)


if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logging.info("listening to http://127.0.0.1:8000")
    logging.info("wsdl is at: http://localhost:8000/?wsdl")
    print("listening to http://127.0.0.1:8000")
    print("wsdl is at: http://localhost:8000/?wsdl")

    server = make_server('127.0.0.1', 8000, wsgi_application)
    server.serve_forever()