import psycopg2
# connect to the db
conn = psycopg2.connect(
    host = "localhost",
    database = "dggs",
    user = "postgres",
    password = "hrnsd823",
  )
#cursor
cur = conn.cursor()

# cur.execute("INSERT INTO company (name, age) values ('Yang', 49)")
#
# conn.commit()

cur.execute("select * from cells")

rows = cur.fetchall()
for r in rows:
    print(r)




#close the connection
cur.close()
conn.close()