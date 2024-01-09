import psycopg2

conn = psycopg2.connect(
   database="postgres", user='postgres', password='Ramo02Targu!st?', host='127.0.0.1', port= '5432'
)

conn.autocommit = True

cursor = conn.cursor()

cursor.execute("CREATE DATABASE fypDB")