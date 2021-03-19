import sqlite3 as sl
from spyne.model.complex import ComplexModel
from spyne.model.primitive import Integer
from spyne.model.primitive import String
from spyne.model.primitive import Float
from datetime import date
import calendar
import logging
import config
from datetime import datetime, timedelta
from os.path import abspath

logger = logging.getLogger(__name__)

class Flight(ComplexModel):
    __namespace__ = 'Flight'
    Airline = String
    ArrivalCity = String
    ArrivalTime = String
    DepartureCity = String
    DepartureTime = String
    FlightNumber = Integer
    Price = Float
    SeatsAvailable = Integer

class FlightOrder(ComplexModel):
   __namespace__ = 'FlightOrder'
   Class = String
   CustomerName = String
   DepartureDate = String
   FlightNumber = Integer
   NumberOfTickets = Integer
   OrderNumber = Integer

class Order(ComplexModel):
   __namespace__ = 'Order'
   OrderNumber = Integer
   TotalPrice = Float

def get_week_day(year, month, day):
    dt = date(year, month, day)
    return (calendar.day_name[dt.weekday()])

def flight_class_name (flght_class):
    flght_class_name = 'N/A'
    if flght_class == 1:
        flght_class_name = 'Business'
    elif flght_class == 2:
        flght_class_name = 'First'
    elif flght_class == 3:
        flght_class_name = 'Economy'
    return (flght_class_name)

def date_in_the_past(flight_date):
    flight_date = datetime.strptime(flight_date, "%Y-%m-%d")
    return(flight_date > datetime.now())

def flight_class_numer(flght_class_name):
    flight_class = 0
    if flght_class_name == 'Business':
        flight_class = 1
    elif flght_class_name == 'First':
        flight_class = 2
    elif flght_class_name == 'Economy':
        flight_class = 3
    return (flight_class)

def get_flight_datetime (departure_date, departure_time):
    time_parts = departure_time.split(' ')[0].split(':')
    date_parts = departure_date.split('-')
    hour = time_parts[0]
    if (departure_time.split(' ')[1] == 'PM'):
        hour = str(int(hour) + 12)
    return (date_parts[0] + '-' + str(int(date_parts[1])) + '-' +  str(int(date_parts[2])) + ' ' +  str(hour) +':' +  time_parts[1])

def city_exists (city_name):
    con = sl.connect(abspath(config.flight_db))
    row = 0
    sql = 'SELECT c.CityInitials, c.CityName FROM Cities c WHERE c.CityName = \'' + city_name + '\';'
    logging.info ('city_exists %s : ', city_name)
    logging.info (sql)
    with con:
        cur = con.cursor()
        res = cur.execute(sql)
        for r in res:
            row += 1
    con.close()
    return (row>0)

def get_flights (departure_city, arrival_city, flight_date):
    logging.info ('get_flights departure_city : %s - arrival_city : %s - flight_date : %s ', departure_city, arrival_city, flight_date)
    logging.info (abspath(config.flight_db))
    con = sl.connect(abspath(config.flight_db))
    flights = []
    day_name = ''
    if (not city_exists(departure_city)):
        return -1

    if (not city_exists(arrival_city)):
        return -2

    if (flight_date.find('-') > 0):
        date_parts = flight_date.split('-')
        day_name = get_week_day (int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
    sql = 'SELECT 	f.Airline , f.Arrival , f.ArrivalTime, f.Departure,f.DepartureTime , f.FlightNumber , f.TicketPrice, f.SeatsAvailable FROM 	Flights f  '
    sql += ' WHERE f.Departure = \'' + departure_city + '\' '
    sql += ' AND  f.Arrival = \'' + arrival_city + '\' '
    if (len(day_name) > 0):
        sql += ' AND  f.DayOfWeek = \'' + day_name + '\' '

    logging.info (sql)
    with con:
        cur = con.cursor()
        res = cur.execute(sql)
        for r in res:
            flight = Flight()
            flight.Airline = r[0]
            flight.ArrivalCity = r[1]
            flight.ArrivalTime = r[2]
            flight.DepartureCity = r[3]
            flight.DepartureTime = r[4]
            flight.FlightNumber = r[5]
            flight.Price = r[6]
            flight.SeatsAvailable = r[7]
            flights.append( flight )
    con.close()
    return (flights)

def get_flight (flight_number):
    logging.info ('get_flight flight_number : %s  ', flight_number)
    con = sl.connect(abspath(config.flight_db))
    sql = 'SELECT 	f.Airline , f.Arrival , f.ArrivalTime, f.Departure,f.DepartureTime , f.FlightNumber , f.TicketPrice, f.SeatsAvailable FROM 	Flights f  '
    sql += ' WHERE f.FlightNumber  = ' + str(flight_number) + ';'
    logging.info (sql)
    with con:
        cur = con.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        if (not row is None):
            flight = Flight()
            flight.Airline = row[0]
            flight.ArrivalCity = row[1]
            flight.ArrivalTime = row[2]
            flight.DepartureCity = row[3]
            flight.DepartureTime = row[4]
            flight.FlightNumber = row[5]
            flight.Price = row[6]
            flight.SeatsAvailable = row[7]
        else:
            flight=-1

    con.close()
    return (flight)

def get_orders (order_number, customer_name):
    orders = []
    if order_number is None or len(order_number)==0:
        order_number=0
    if customer_name is None:
        customer_name=''
    con = sl.connect(abspath(config.flight_db))
    sql = 'SELECT 	o.OrderNumber , o.CustomerName , o.DepartureDate, o.FlightNumber , o.TicketsOrdered , o.Class FROM	Orders o'
    if (order_number == 0) and (len(customer_name) == 0) :
        orders.append(FlightOrder())
        return (orders)
    elif (order_number!=0):
        sql = sql + ' WHERE o.OrderNumber =  '  + str(order_number)
    elif (customer_name != ''):
        sql = sql + ' WHERE o.CustomerName =  \'' + customer_name + '\''
    sql = sql + ';'
    logging.info (sql)
    with con:
        cur = con.cursor()
        res = cur.execute(sql)
        for r in res:
            flight_class = flight_class_name (r[5])
            order = FlightOrder()
            order.Class = flight_class
            order.Class = flight_class
            order.CustomerName = r[1]
            order.DepartureDate = r[2]
            order.FlightNumber = r[3]
            order.NumberOfTickets = r[4]
            order.OrderNumber = r[0]
            orders.append (order)
    con.close()
    return (orders)


def get_seats_available (flight_number):
    con = sl.connect(abspath(config.flight_db))
    sql = 'Select SeatsAvailable from Flights Where FlightNumber = ' + str(flight_number) + ';'
    logging.info(sql)
    cursor = con.cursor()
    cursor.execute(sql)
    seats = cursor.fetchone()[0]
    con.close()
    return (seats)

def update_seats_available (con, flight_number, seats):
    if (seats > 0):
        seats = '+' + str (seats)
    elif (seats < 0):
        seats =  str (seats)
    elif (seats == 0):
        seats=''
    sql = 'UPDATE Flights SET SeatsAvailable = SeatsAvailable ' + seats + ' WHERE FlightNumber =' + str(flight_number) + ';'
    logging.info(sql)
    con.execute(sql)

def create_flight_order (customer_name, departure_date, flight_number, tickets_ordered, flight_class):
    flight = get_flight(flight_number)
    if (flight.FlightNumber is None):
        return(-2)
    seats_availabe = flight.SeatsAvailable
    if (seats_availabe <= 0):
        return(-3)
    #  departure_date = get_flight_datetime('2021-02-05', flight.DepartureTime)
    if (int(tickets_ordered) > seats_availabe):
        return (-1)

    con = sl.connect(abspath(config.flight_db))
    last_id = 0
    departure_date = get_flight_datetime(departure_date, flight.DepartureTime)
    sql = 'INSERT INTO Orders (CustomerName, DepartureDate, FlightNumber, TicketsOrdered, Class) values(?, ?, ?, ?, ?)'
    data = (customer_name, departure_date, flight_number, tickets_ordered, flight_class_numer(flight_class))
    with con:
        con.execute(sql, data)
        cursor = con.cursor()
        cursor.execute('select last_insert_rowid();')
        last_id = cursor.fetchone()[0]
        update_seats_available(con, flight_number, -1*int(tickets_ordered))
        flight = get_flight(flight_number)
        total_price = flight.Price*float(tickets_ordered)
    con.close()
    new_order = Order()
    new_order.OrderNumber = last_id
    new_order.TotalPrice = total_price
    return (new_order)

def update_flight_order (order_number, flight_class, customer_name, number_of_tickets):
    con = sl.connect(abspath(config.flight_db))
    orders =  get_orders (str(order_number), '')
    if (len(orders)==0):
        return 0
    flight_number= orders[0].FlightNumber
    tickets_ordered_old = orders[0].NumberOfTickets
    class_numer = flight_class_numer(flight_class)
    if (class_numer==0):
        return (-1)
    sql = 'UPDATE Orders SET Class = '+ str(class_numer)+', CustomerName = \''+customer_name+'\', TicketsOrdered = '+str(number_of_tickets)+' WHERE OrderNumber=' + str(order_number)
    logging.info (sql)
    with con:
        cur = con.cursor()
        cur.execute(sql)
        row_updated = cur.rowcount
        update_seats_available(con, flight_number, tickets_ordered_old)
        update_seats_available(con, flight_number, -1 * int(number_of_tickets))
    con.close()
    return (row_updated)

def delete_flight_order (order_number):
    orders = get_orders (order_number, '')
    if (len(orders) == 0):
        return 0
    tickets_ordered = orders[0].NumberOfTickets
    flight_number= orders[0].FlightNumber
    con = sl.connect(abspath(config.flight_db))
    sql = 'DELETE FROM  Orders WHERE OrderNumber=' + str(order_number)
    logging.info (sql)
    with con:
        cur = con.cursor()
        cur.execute(sql)
        row_deleted = cur.rowcount
        update_seats_available(con, flight_number, tickets_ordered)

    con.close()
    return (row_deleted)

