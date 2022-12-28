Alter Table Users Add Column Profil NVARCHAR(10);

Update Users 
Set		Profil = 'User';

Update Users 
Set		Profil = 'Admin'
Where   username = 'john';

Select * from Users;

Alter Table Flights Add Column TicketPriceFirst FLOAT;
Alter Table Flights Add Column TicketPriceBusiness FLOAT;

Update Flights 
Set		TicketPriceFirst = TicketPrice * 1.2
		, TicketPriceBusiness = TicketPrice * 1.3
;

Select * from Flights;
