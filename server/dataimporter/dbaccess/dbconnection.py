import psycopg2
import config

# Try to connect
try:
    conn=psycopg2.connect("dbname='" & config.get_config('db','dbname') & "' user='" & config.get_config('db','dbuser') & "' password='" & config.get_config('db','dbpassword') & "'")
except:
    print("I am unable to connect to the database.")

#TODO : Connection OK, select KO (droits user ?)
cursor = conn.cursor()
try:
    cursor.execute("SELECT * FROM coins")
except:
    print("I can't SELECT from coins")

rows = cursor.fetchall()
for row in rows:
    print("   ", row[1][1])
