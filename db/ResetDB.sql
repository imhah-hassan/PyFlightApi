DELETE FROM Orders WHERE OrderNumber > 80;
Select * from Orders;

UPDATE Flights SET SeatsAvailable = 250;
UPDATE sqlite_sequence SET seq = 80 WHERE name='Orders';

Select FlightNumber, SeatsAvailable from Flights Where FlightNumber = 10487;
SELECT SUM(TicketsOrdered) FROM Orders o where FlightNumber = 10487;

