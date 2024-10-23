set dest=c:\temp\PyFlightApi
mkdir %dest%
copy flightapi.ini %dest%
copy flights_db.py %dest%
copy logging.conf %dest%
copy flight_rest.py %dest%
copy config.py %dest%
mkdir %dest%\db
copy db\Flights.s3db %dest%\db
copy requirements.txt %dest%
copy install.txt %dest%