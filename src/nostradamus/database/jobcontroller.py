import logging
from nostradamus.job import Job

logger = logging.getLogger('database.jobcontroller')

class JobController(object):
    def __init__(self,
                 db_controller):
        self.db_controller = db_controller


    def get_next_job_id(self):
        """ TBD """
        pass


    def get_job_by_id(self,
                      job_id):
        """ TBD """
        query = "SELECT id, prometheus_url, metric, query_filter, \
            forecast_horizon, forecast_frequency, status, \
            to_char(last_run,'yyyy/mm/dd hh24:mi:ss') as last_run, \
            to_char(next_run,'yyyy/mm/dd hh24:mi:ss') as next_run, \
            last_run_duration \
            FROM job \
        WHERE id = %(id)s \
        LIMIT 1;"

        try:
            args = { 'id': job_id }
            result = self.db_controller.select(query, args)
            logger.debug(f'Query result: {result}')
            if (result):
                for row in result:
                    job = Job(id = row['id'],
                        prometheus_url = row['prometheus_url'],
                        metric = row['metric'],
                        query_filter = row['query_filter'],
                        forecast_horizon = row['forecast_horizon'],
                        forecast_frequency = row['forecast_frequency'],
                        status = row['status'],
                        last_run = row['last_run'],
                        next_run = row['next_run'],
                        last_run_duration = row['last_run_duration']
                    )
                return job
            else:
                return -1
        except Exception as error :
            logger(f'Failed to execute "get_job_by_id" method: {error}')
            return -1


    def get_job(self):
        """ TBD """
        query = "SELECT id, prometheus_url, metric, query_filter, \
            forecast_horizon, forecast_frequency, status, \
            to_char(last_run,'yyyy/mm/dd hh24:mi:ss') as last_run, \
            to_char(next_run,'yyyy/mm/dd hh24:mi:ss') as next_run, \
            last_run_duration \
            FROM job \
        WHERE status IN ('NEW','FINISHED') \
            AND coalesce(next_run, \
                            null, \
                            now() - interval '1' second ) < now() \
        ORDER BY next_run ASC \
        LIMIT 1;"

        try:
            # get data from db and create a new job instance
            result = self.db_controller.select(query, args=None)
            if (result):
                for row in result:
                    job = Job(id = row['id'],
                        prometheus_url = row['prometheus_url'],
                        metric = row['metric'],
                        query_filter = row['query_filter'],
                        forecast_horizon = row['forecast_horizon'],
                        forecast_frequency = row['forecast_frequency'],
                        status = row['status'],
                        last_run = row['last_run'],
                        next_run = row['next_run'],
                        last_run_duration = row['last_run_duration']
                    )
                return job
            else:
                return -1

        except Exception as error :
            logger(f'Failed to execute "get_job" method: {error}')
            return -1


    def get_finished_jobs(self):
        """ TBD """
        query="SELECT j.id, \
            coalesce(d.status,'ERROR','FINISHED') status, \
            to_char( \
                max(d.updated_time), \
                'yyyy/mm/dd hh24:mi:ss' \
            ) as updated_time, \
            to_char( \
                max(f.ds_to) - interval '10' minute, \
                'yyyy/mm/dd hh24:mi:ss' \
            ) as next_time, \
            extract( \
                epoch from max(d.updated_time) - j.last_run \
            )::int as run_duration \
        FROM job j \
            LEFT JOIN train_data d ON j.id = d.job_id \
            LEFT JOIN forecast f on j.id = f.job_id \
        WHERE j.status = 'RUNNING' \
            AND NOT EXISTS \
            (SELECT 1 FROM train_data d \
                WHERE d.job_id = j.id \
                    AND d.status not in ('FINISHED','ERROR')) \
        GROUP BY j.id, d.status;"

        try:
            # Get already finished job tasks
            result = self.db_controller.select(query, args=None)
            if (result):
                logger.debug(f'[get_finished_jobs]: {result}')
                return 0, result
            else:
                return -1, None

        except Exception as error :
            logger(f'Failed to execute "get_finished_jobs" method: {error}')
            return -2, None



    def update_job(self,
                   job_id,
                   **kwargs):
        """ Update job attributes """
        set_str = ''
        values = {}
        for k,v in kwargs.items():
            set_str = set_str + f'{k}=%({k})s, '
            values[k]=v
        set_str = set_str[:-2]

        query = f'UPDATE job SET {set_str} WHERE id = {job_id};'
        logger.debug(f'Query: {query}\nBinds: {values}')

        try:
            self.db_controller.update(query, values)
        except Exception as error:
            logger(f'Failed to execute "update_job" method: {error}')


    def insert_job(self):
        """ Insert a new job """
        pass


    def delete_job(self):
        """ Delete a job """
        pass