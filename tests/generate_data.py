import flights_db
from datetime import datetime, timedelta
from random import randrange

classes = ['Economy', 'First', 'Business']


db = flights_db.sqlite_db()
cities = db.get_city('')

print("Departure;Arrival;Date;FlightNumber;Class;Tickets;UnitPrice;SeatsAvailable")

for i in range(20):
    flight_date = str(datetime.now() + timedelta(randrange(15) + 21))[0:10]
    departure_city = cities[randrange(10)].CityName
    arrival_city = departure_city
    while (arrival_city == departure_city):
        arrival_city = cities[randrange(10)].CityName
    flights = db.get_flights(departure_city, arrival_city, flight_date)
    random_flight = flights[randrange(len(flights))]
    random_class = classes[randrange(len(classes))]
    if random_class == 'Economy':
        price = random_flight.Price
    elif random_class == 'First':
        price = random_flight.PriceFirst
    elif random_class == 'Business':
        price = random_flight.PriceBusiness
    else:
        price=100.0
        print ("*****************ERROR : Price not found")

    print(';'.join( (departure_city,arrival_city,flight_date,str(random_flight.FlightNumber),random_class,str(randrange(4) + 1), str(price),str(random_flight.SeatsAvailable)) ) )

db.close_db()