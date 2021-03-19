SELECT * FROM Orders o WHERE	o.FlightNumber not in (SELECT f.FlightNumber FROM Flights f);


SELECT * FROM Flights f WHERE	f.FlightNumber  in (SELECT o.FlightNumber FROM Orders o WHERE o.OrderNumber>80);

SELECT * FROM Orders o ;
SELECT * FROM Flights f ;
