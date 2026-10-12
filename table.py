from database import get_connection

def create_table():
    con = get_connection()
    if con:
        cursor = con.cursor()
        
        # वर्कशॉपसाठी सीट किंवा विद्यार्थ्यांचे टेबल तयार करण्याची क्वेरी
        create_table_query = """
        CREATE TABLE IF NOT EXISTS participants (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            seat_number INT DEFAULT NULL
        )
        """
        
        cursor.execute(create_table_query)
        print("Table 'participants' created successfully!")
        
        cursor.close()
        con.close()
    else:
        print("Database connection failed.")

if __name__ == "__main__":
    create_table()