import sqlite3
import pymysql

# Connect to the SQLite database
sqlite_conn = sqlite3.connect('Flights.s3db')
sqlite_cursor = sqlite_conn.cursor()

# Connect to the MariaDB/MySQL database
mysql_conn = pymysql.connect(host='localhost',
                             user='root',
                             password='Hassan$2023',
                             db='flightsdb')
mysql_cursor = mysql_conn.cursor()

# Retrieve the list of tables from the SQLite database
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

# Iterate over each table and export data to MariaDB
for table_name in tables:
    # Create the table in MariaDB
    if table_name[0] != 'Users':
        continue;
    sqlite_cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name[0]}';")
    create_table_query = sqlite_cursor.fetchone()[0]
    # print (create_table_query)
    # mysql_cursor.execute(create_table_query)

    # Retrieve data from SQLite table
    sqlite_cursor.execute(f"SELECT * FROM {table_name[0]};")
    rows = sqlite_cursor.fetchall()

    # Insert data into MariaDB table
    count=1
    for row in rows:
         mysql_cursor.execute(f"INSERT INTO {table_name[0]} VALUES {row};")
         if count > 9:
            break
         count+=1

    # Commit changes for each table
    mysql_conn.commit()

# Close the connections
sqlite_cursor.close()
sqlite_conn.close()
mysql_cursor.close()
mysql_conn.close()
