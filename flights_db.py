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

class   sqlite_db ():
    __namespace__ = 'sqlite_db'

    def __init__(self):
        logging.info (abspath(config.flight_db))
        self.con = sl.connect(abspath(config.flight_db))
        logging.info (self.con)

    def close_db(self):
        self.con.close()

    def get_week_day(self, year, month, day):
        dt = date(year, month, day)
        return (calendar.day_name[dt.weekday()])

    def flight_class_name (self, flght_class):
        flght_class_name = 'N/A'
        if flght_class == 1:
            flght_class_name = 'Business'
        elif flght_class == 2:
            flght_class_name = 'First'
        elif flght_class == 3:
            flght_class_name = 'Economy'
        return (flght_class_name)

    def date_in_the_past(self, flight_date):
        flight_date = datetime.strptime(flight_date, "%Y-%m-%d")
        return(flight_date > datetime.now())

    def flight_class_numer(self, flght_class_name):
        flight_class = 0
        if flght_class_name == 'Business':
            flight_class = 1
        elif flght_class_name == 'First':
            flight_class = 2
        elif flght_class_name == 'Economy':
            flight_class = 3
        return (flight_class)

    def get_flight_datetime (self, departure_date, departure_time):
        time_parts = departure_time.split(' ')[0].split(':')
        date_parts = departure_date.split('-')
        hour = time_parts[0]
        if (departure_time.split(' ')[1] == 'PM'):
            hour = str(int(hour) + 12)
        return (date_parts[0] + '-' + str(int(date_parts[1])) + '-' +  str(int(date_parts[2])) + ' ' +  str(hour) +':' +  time_parts[1])

    def city_exists (self, city_name):
        if (len(city_name)==0):
            return (True);
        row = 0
        sql = 'SELECT c.CityInitials, c.CityName FROM Cities c WHERE c.CityName = \'' + city_name + '\';'
        logging.info ('city_exists %s : ', city_name)
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                row += 1
        return (row>0)

    def get_flights (self, departure_city, arrival_city, flight_date):
        logging.info ('get_flights departure_city : %s - arrival_city : %s - flight_date : %s ', departure_city, arrival_city, flight_date)
        flights = []
        day_name = ''
        if (not self.city_exists(departure_city)):
            return -1

        if (not self.city_exists(arrival_city)):
            return -2

        if (flight_date.find('-') > 0):
            date_parts = flight_date.split('-')
            day_name = self.get_week_day (int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
        sql = 'SELECT 	f.Airline , f.Arrival , f.ArrivalTime, f.Departure,f.DepartureTime , f.FlightNumber , f.TicketPrice, f.SeatsAvailable, f.DayOfWeek FROM 	Flights f  '
        criterias = ''
        if (len(departure_city) > 0):
            criterias += ' f.Departure = \'' + departure_city + '\' '

        if (len(arrival_city) > 0):
            if (len(criterias) > 0):
                criterias += ' AND '
            criterias += ' f.Arrival = \'' + arrival_city + '\' '

        if (len(day_name) > 0):
            if (len(criterias) > 0):
                criterias += ' AND '
            criterias += ' f.DayOfWeek = \'' + day_name + '\' '

        if (len(criterias) > 0):
            sql = sql + ' WHERE ' + criterias

        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
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
                flight.DayOfWeek = r[8]
                flights.append( flight )
        return (flights)

    def get_flight (self, flight_number):
        logging.info ('get_flight flight_number : %s  ', flight_number)
        sql = 'SELECT 	f.Airline , f.Arrival , f.ArrivalTime, f.Departure,f.DepartureTime , f.FlightNumber , f.TicketPrice, f.SeatsAvailable, f.DayOfWeek FROM 	Flights f  '
        sql += ' WHERE f.FlightNumber  = ' + str(flight_number) + ';'
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
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
                flight.DayOfWeek = row[8]
            else:
                flight=-1
        return (flight)

    def get_orders (self, order_number, customer_name):
        orders = []
        if order_number is None or len(order_number)==0:
            order_number=0
        if customer_name is None:
            customer_name=''
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
        with self.con:
            cur = self.con.cursor()
            res = cur.execute(sql)
            for r in res:
                flight_class = self.flight_class_name (r[5])
                order = FlightOrder()
                order.Class = flight_class
                order.Class = flight_class
                order.CustomerName = r[1]
                order.DepartureDate = r[2]
                order.FlightNumber = r[3]
                order.NumberOfTickets = r[4]
                order.OrderNumber = r[0]
                orders.append (order)
        return (orders)

    def get_seats_available (self, flight_number):
        sql = 'Select SeatsAvailable from Flights Where FlightNumber = ' + str(flight_number) + ';'
        logging.info(sql)
        cursor = self.con.cursor()
        cursor.execute(sql)
        seats = cursor.fetchone()[0]
        return (seats)

    def update_seats_available (self, flight_number, seats):
        if (seats > 0):
            seats = '+' + str (seats)
        elif (seats < 0):
            seats =  str (seats)
        elif (seats == 0):
            seats=''
        sql = 'UPDATE Flights SET SeatsAvailable =  SeatsAvailable ' + seats + ' WHERE FlightNumber =' + str(flight_number) + ';'
        logging.info(sql)
        self.con.execute(sql)

    def update_all_seats_available (self):
        sql = 'UPDATE Flights SET SeatsAvailable = 250 ;'
        logging.info(sql)
        self.con.execute(sql)

    def create_flight_order (self, customer_name, departure_date, flight_number, tickets_ordered, flight_class):
        flight = self.get_flight(flight_number)
        if (flight.FlightNumber is None):
            return(-2)
        seats_availabe = flight.SeatsAvailable
        if (seats_availabe <= 0):
            return(-3)
        #  departure_date = get_flight_datetime('2021-02-05', flight.DepartureTime)
        if (int(tickets_ordered) > seats_availabe):
            return (-1)

        last_id = 0
        departure_date = self.get_flight_datetime(departure_date, flight.DepartureTime)
        sql = 'INSERT INTO Orders (CustomerName, DepartureDate, FlightNumber, TicketsOrdered, Class) values(?, ?, ?, ?, ?)'
        data = (customer_name, departure_date, flight_number, tickets_ordered, self.flight_class_numer(flight_class))
        with self.con:
            self.con.execute(sql, data)
            cursor = self.con.cursor()
            cursor.execute('select last_insert_rowid();')
            last_id = cursor.fetchone()[0]
            self.update_seats_available(flight_number, -1*int(tickets_ordered))
            flight = self.get_flight(flight_number)
            total_price = flight.Price*float(tickets_ordered)
        new_order = Order()
        new_order.OrderNumber = last_id
        new_order.TotalPrice = total_price
        return (new_order)

    def update_flight_order (self, order_number, flight_class, customer_name, number_of_tickets):
        orders =  self.get_orders (str(order_number), '')
        if (len(orders)==0):
            return 0
        flight_number= orders[0].FlightNumber
        tickets_ordered_old = orders[0].NumberOfTickets
        class_numer = self.flight_class_numer(flight_class)
        if (class_numer==0):
            return (-1)
        sql = 'UPDATE Orders SET Class = '+ str(class_numer)+', CustomerName = \''+customer_name+'\', TicketsOrdered = '+str(number_of_tickets)+' WHERE OrderNumber=' + str(order_number)
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            cur.execute(sql)
            row_updated = cur.rowcount
            self.update_seats_available(flight_number, tickets_ordered_old)
            self.update_seats_available(flight_number, -1 * int(number_of_tickets))
        return (row_updated)

    def delete_flight_order (self, order_number):
        orders = self.get_orders (order_number, '')
        if (len(orders) == 0):
            return 0
        tickets_ordered = orders[0].NumberOfTickets
        flight_number= orders[0].FlightNumber
        sql = 'DELETE FROM  Orders WHERE OrderNumber=' + str(order_number)
        logging.info (sql)
        with self.con:
            cur = self.con.cursor()
            cur.execute(sql)
            row_deleted = cur.rowcount
            self.update_seats_available(flight_number, tickets_ordered)
        return (row_deleted)

    def delete_all_orders (self):
        logging.info ("Delete all")
        with self.con:
            cur = self.con.cursor()
            try:
                cur.execute("DELETE FROM  Orders ;")
                cur.execute('UPDATE sqlite_sequence  SET seq = 80 WHERE name="Orders";')
                cur.execute('Update Flights Set SeatsAvailable = 250;')
            except:
                logging.error("Delete all")

if __name__ == '__main__':
    sl = sqlite_db()
    print (sl.con)
    print (sl.city_exists ('Paris'))
    print (sl.city_exists ('Denver'))
    print (sl.get_flights ('Paris', 'London', '2021-12-25'))
    print (sl.get_flights ('Paris', 'Denver', '2021-12-25'))
    print (sl.get_flight ('10454'))
    print (sl.create_flight_order ('IMHAH',  '2021-12-25', 10454, 2, 'Economy'))
    print (sl.get_orders('', 'IMHAH'))
    print (sl.get_orders('81', ''))
    print (sl.update_flight_order('81', 'First', 'IMHAH', 5))
    print(sl.get_orders('81', ''))
    print(sl.delete_flight_order('81'))
    print(sl.delete_all_orders())
    sl.close_db()
