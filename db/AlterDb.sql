CREATE TABLE [Audit] (
[AuditId] INTEGER  PRIMARY KEY AUTOINCREMENT NOT NULL,
[tableName] VARCHAR(100)  NULL,
[tableColumn] VARCHAR(100)  NULL,
[kayName] VARCHAR(100)  NULL,
[kayValue] VARCHAR(100)  NULL,
[oldValue] VARCHAR(100)  NULL,
[newValue] VARCHAR(100)  NULL,
[updateDate] DATETIME  NULL);


Alter Table Orders Add Column TotalPrice FLOAT;
Alter Table Flights Add Column TicketPriceFirst FLOAT;
Alter Table Flights Add Column TicketPriceBusiness FLOAT;

Update Flights 
Set		TicketPriceFirst = TicketPrice * 1.2
		, TicketPriceBusiness = TicketPrice * 1.3
;


Update	 Orders
SET		 TotalPrice = (Select TicketPrice*Orders.TicketsOrdered From Flights f where f.FlightNumber = Orders.FlightNumber)
WHERE	 Class = 3
;

Update	 Orders
SET		 TotalPrice = (Select TicketPriceFirst*Orders.TicketsOrdered From Flights f where f.FlightNumber = Orders.FlightNumber)
WHERE	 Class = 2
;

Update	 Orders
SET		 TotalPrice = (Select TicketPriceBusiness*Orders.TicketsOrdered From Flights f where f.FlightNumber = Orders.FlightNumber)
WHERE	 Class = 1
;


Alter Table Users Add Column Profil NVARCHAR(10);

Update Users 
Set		Profil = 'User';

Update Users 
Set		Profil = 'Admin'
Where   username = 'john';

Select * from Users;


Select * from Orders o ;
