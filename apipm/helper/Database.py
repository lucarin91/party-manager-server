import psycopg2, psycopg2.extras, collections

sql = psycopg2.connect(
    database='pm_database',
    user='apipm',
    password='geronsi',
    host='localhost',
)
