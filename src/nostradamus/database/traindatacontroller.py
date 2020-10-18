import json
import logging

logger = logging.getLogger('database.traindatacontroller')

class TrainDataController(object):
    """ TBD """

    def __init__(self,
                 db_controller):
        self.db_controller = db_controller


    def get(self):
        """ TBD """
        try:
            query = "SELECT id, job_id, data \
                FROM train_data \
            WHERE status IN ('NEW') \
            ORDER BY created_time ASC \
            LIMIT 1;"

            # get data from db and create a new job instance
            result = self.db_controller.select(query, args=None)
            if (result):
                for row in result:
                    resp = row
                    #job_id = row['job_id']
                    #data = row['data']
                #return job_id, data
                return 0, resp
            else:
                return -1, None

        except Exception as error:
            logger.error(f'Failed to execute "get" method: {error}')
            return -2, None


    def insert(self,
               job_id,
               series):
        """ TBD """
        query = "INSERT INTO train_data (job_id, status, data ) \
            VALUES (%s, %s, %s);"
        try:
            for s in series:
                self.db_controller.insert(query,
                    job_id,
                    "NEW",
                    json.dumps(s)
                )
        except Exception as e:
            logger.error(f'Failed to execute "insert" method: {e}')


    def update(self,
               id,
               **kwargs):
        """ TBD """
        set_str = ''
        values = {}
        for k,v in kwargs.items():
            set_str = set_str + f'{k}=%({k})s, '
            values[k]=v
        set_str = set_str[:-2]

        query = f'UPDATE train_data SET {set_str} WHERE id = {id};'

        try:
            self.db_controller.update(query, values)
        except Exception as e:
            logger.error(f'Failed to execute "update" method: {e}')


    def cleanup(self, job_id):
        """ Clean """
        query = "DELETE FROM train_data \
        WHERE job_id = %(id)s AND ins_time<now();"

        args = {"id": job_id}

        try:
            self.db_controller.delete(query, args)
        except Exception as error:
            logger.error(f'cleanup query failed with: {error}')