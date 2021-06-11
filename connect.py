import psycopg2
from config import config

def connect():
    # Connect to db server
    conn = None
    try:
        # read connection params
        params = config()

        # connect to Postgres server
        print('Connecting to PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL db server version
        db_version = cur.fetchone()
        print(db_version)

        	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()