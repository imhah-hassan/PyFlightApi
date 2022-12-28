ALTER TABLE Orders ADD TotalPrice NUMERIC;

CREATE TABLE Audit (
    audit_id integer primary key autoincrement,
    tableName TEXT,
    tableColumn TEXT,
	kayName TEXT,
	kayValue TEXT,
    oldValue TEXT,
    newValue TEXT,
    updateDate DATE); 
	
