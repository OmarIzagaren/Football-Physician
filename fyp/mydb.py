import psycopg2

# Replace '<your_user>' and '<your_password>' with your PostgreSQL username and password

conn = psycopg2.connect(
   database="postgres", 
   user='<your_user>', 
   password='<your_password>', 
   host='127.0.0.1', 
   port= '5432'
)

conn.autocommit = True

cursor = conn.cursor()

cursor.execute("CREATE DATABASE dbfyp")