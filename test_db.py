from database import get_connection

print("Checking Connection...") # हे ॲड करा

con = get_connection()

if con:
    print("MySQL Connected Successfully!")
    con.close()
else:
    print("Connection Failed!")