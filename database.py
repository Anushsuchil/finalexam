from datetime import datetime
from sql_connection import get_sql_connection
import mysql.connector

def tounix(date):
    date_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M')
    return int(date_obj.timestamp())

def insert_user(connection, user_id, role, password):
    try:
        query = "INSERT INTO users (user_id, role, password) VALUES (%s,%s,%s);"
        cur = connection.cursor(buffered=True)
        cur.execute(query, (user_id, role, password))
        connection.commit()
        cur.close()
    except mysql.connector.Error as e:
        print(f"Error inserting user: {e}")
        try:
            connection.rollback()
        except:
            pass
    
def insert_request(connection, exam_id, release_date, teacher_id):
    try:
        query = "INSERT INTO requests (exam_id, release_date, user_id) VALUES (%s,%s,%s);"
        cur = connection.cursor(buffered=True)
        cur.execute(query, (exam_id, release_date, teacher_id))
        connection.commit()
        cur.close()
    except mysql.connector.Error as e:
        print(f"Error inserting request: {e}")
        try:
            connection.rollback()
        except:
            pass

def fetch_request(connection, user_id):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT exam_id FROM requests WHERE user_id = %s AND update_status = 0;"
        cur.execute(query, (user_id,))
        response = [row[0] for row in cur.fetchall()]  # Fetch all results
        return response
    except mysql.connector.Error as e:
        print(f"Error fetching requests: {e}")
        return []  # Return an empty list on error
    finally:
        cur.close()  # Ensure the cursor is closed
    
def fetch_teacher(connection, exam_id):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT user_id FROM requests WHERE exam_id = %s AND update_status = 1;"
        cur.execute(query, (exam_id,))
        response = [row[0] for row in cur.fetchall()]  # Fetch all results
        return response
    except mysql.connector.Error as e:
        print(f"Error fetching teachers: {e}")
        return []  # Return an empty list on error
    finally:
        cur.close()  # Ensure the cursor is closed

def is_valid(connection, user_id, role, password):
    cur = connection.cursor(buffered=True)
    
    try:
        query = "SELECT user_id FROM users WHERE user_id=%s AND role=%s AND password=%s;"
        cur.execute(query, (user_id, role, password))
        
        response = cur.fetchone()
        
        return response is not None
    except mysql.connector.Error as e:
        print(f"Error validating user: {e}")
        return False
    finally:
        cur.close()

def delete_request(connection, exam_id, user_id):
     try:
         query = "DELETE FROM requests WHERE exam_id=%s and user_id=%s;"
         cur = connection.cursor(buffered=True)
         cur.execute(query, (exam_id, user_id))
         connection.commit()
         print("deleted")
         cur.close()
     except mysql.connector.Error as e:
         print(f"Error deleting request: {e}")
         try:
             connection.rollback()
         except:
             pass

def get_time(connection, exam_id):
    cur = connection.cursor(buffered=True)

    try:
        query = "SELECT release_date FROM requests WHERE exam_id=%s;"
        cur.execute(query, (exam_id,))
        response = cur.fetchone()

        if response is not None:
            return int(response[0])
        else:
            raise ValueError("No results found for the given exam ID.")
    except (mysql.connector.Error, ValueError) as e:
        print(f"Error getting time: {e}")
        raise
    finally:
        cur.close()  # Ensure the cursor is closed

def updated(connection, exam_id, user_id):
    try:
        query = "UPDATE requests SET update_status = '1' WHERE exam_id = %s AND user_id = %s;"
        cur = connection.cursor(buffered=True)
        cur.execute(query, (exam_id, user_id))
        connection.commit()
        print("updated")
        cur.close()
    except mysql.connector.Error as e:
        print(f"Error updating request status: {e}")
        try:
            connection.rollback()
        except:
            pass

def reset_connection(connection):
    try:
        connection.reset_session()
    except Exception as e:
        print(f"Error resetting connection: {e}")

# # Main execution
# connection = get_sql_connection()

# try:
#     a = get_time(connection, "e1")
#     print(a)
#     reset_connection(connection)
#     updated(connection, "e1", "t1")
# except Exception as e:
#     print(f"An error occurred: {e}")
# finally:
#     if connection.is_connected():
#         connection.close()