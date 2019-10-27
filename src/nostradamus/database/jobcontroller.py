from nostradamus.job import Job

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
        try:
            query = "SELECT id, prometheus_url, metric, query_filter, \
                forecast_horizon, forecast_frequency, status, \
                to_char(last_run,'yyyy/mm/dd hh24:mi:ss') as last_run, \
                to_char(next_run,'yyyy/mm/dd hh24:mi:ss') as next_run, \
                last_run_duration \
             FROM job \
            WHERE id = %(id)s \
            LIMIT 1;"

            args = { 'id': job_id }
            result = self.db_controller.select(query, args)
            print(result)
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
            print ("Error", error)
            return -1        


    def get_job(self):
        """ TBD """
        try:
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
            print ("Error", error)
            return -1

    
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
        print(f'{query} WITH {values}')

        try:
            self.db_controller.update(query, values)
        except Exception as e:
            print(e)


    def insert_job(self):
        """ Insert a new job """
        pass


    def delete_job(self):
        """ Delete a job """
        pass