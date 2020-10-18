import json
import logging
import psycopg2

from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor, execute_batch

logger = logging.getLogger('database.postgres')

class DbController(object):
    """
    Provides postgres database connection pool and methods to manage the data
    """
    def __init__(self,
                 user,
                 password,
                 host,
                 port,
                 database,
                 pool_max_size):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.pool_max_size = pool_max_size

        try:
            if (self.conn_pool):
                pass
        except:
            self.connect()


    def connect(self):
        """ Initialize database connection pool """
        try:
            self.conn_pool = SimpleConnectionPool(minconn=1,
                maxconn=self.pool_max_size,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port,
                database = self.database)

        except (Exception, psycopg2.Error) as error :
            logger.fatal(f'Error connecting to PostgreSQL: {error}')


    def close(self):
        """ Close database connection pool """
        if (self.conn_pool):
            self.conn_pool.closeall
        logger.info('PostgreSQL connection pool is closed')


    def ping(self):
        """ Method to check availability of db. Used in /healtz/ready """
        try:
            # get connection from connection pool
            conn = self.conn_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            cursor.fetchone()
            # close cursor and release connection
            cursor.close()
            self.conn_pool.putconn(conn)
            return 0

        except (Exception, psycopg2.Error) as error:
            logger.error(f'Error connecting to PostgreSQL: {error}')
            return -1


    def select(self,
               query,
               args):
        """ Execute query and return results as json """
        try:
            conn = self.conn_pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, args)
            # zip resultset into array of dictionaries
            record = json.dumps(cursor.fetchall())
            cursor.close()
            self.conn_pool.putconn(conn)
            # convert to json
            return json.loads(record)

        except (Exception, psycopg2.Error) as error:
            logger.error(f'Error executing the SELECT query: {error}')
            self.conn_pool.putconn(conn)
            return -1


    def insert(self,
               query,
               *args):
        try:
            params = tuple(arg for arg in args)

            conn = self.conn_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(query, params)
            cursor.close()
            conn.commit()
            self.conn_pool.putconn(conn)

        except (Exception, psycopg2.Error) as error:
            logger.error(f'Error executing the INSERT query: {error}')
            conn.rollback()
            self.conn_pool.putconn(conn)
            return -1


    def insert_bulk(self,
                    query,
                    params):
        try:
            conn = self.conn_pool.getconn()
            cursor = conn.cursor()
            execute_batch(cursor, query, params)
            cursor.close()
            conn.commit()
            self.conn_pool.putconn(conn)

        except (Exception, psycopg2.Error) as error:
            logger.error(f'Error executing BULK INSERT query: {error}')
            conn.rollback()
            self.conn_pool.putconn(conn)
            return -1


    def update(self,
               query,
               args):
        try:
            params = args
            conn = self.conn_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(query, params)
            cursor.close()
            conn.commit()
            self.conn_pool.putconn(conn)

        except (Exception, psycopg2.Error) as error:
            logger.error(f'Error executing UPDATE query: {error}')
            conn.rollback()
            self.conn_pool.putconn(conn)
            return -1


    def delete(self,
               query,
               args):
        try:
            params = args
            conn = self.conn_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(query, params)
            cursor.close()
            conn.commit()
            self.conn_pool.putconn(conn)

        except (Exception, psycopg2.Error) as error:
            logger.error(f'Error executing DELETE query: {error}')
            conn.rollback()
            self.conn_pool.putconn(conn)
            return -1