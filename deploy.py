import psycopg2
DEBUG=False
SQL = psycopg2.connect(
    database='pm_database',
    user='apipm',
    host='localhost',
)
WHERE='deployment'