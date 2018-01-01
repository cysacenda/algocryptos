import psycopg2

# Try to connect

try:
    conn=psycopg2.connect("dbname='algocryptos' user='dbuser' password='algocryptos'")
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