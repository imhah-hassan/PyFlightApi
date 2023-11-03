import flights_db

db = flights_db.sqlite_db()

flights = db.get_flights('Casablanca', '', '')
while flights!=-1:
    rows = db.delete_flight(str(flights[0].FlightNumber))
    flights = db.get_flights('Casablanca', '', '')
    print(rows)

flights = db.get_flights('', 'Casablanca', '')
while flights!=-2:
    rows = db.delete_flight(str(flights[0].FlightNumber))
    flights = db.get_flights('', 'Casablanca', '')
    print(rows)

orders = db.delete_all_orders();
rows = db.delete_city("CMN")
print(rows)
