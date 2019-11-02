import os
from datetime import datetime

from nostradamus.database.jobcontroller import JobController
from nostradamus.database.traindatacontroller import TrainDataController
from nostradamus.external.prometheus import Client as PrometheusClient


class Worker(object):
    """ Worker class """

    def __init__(self, db):
        self.job_ctrl = JobController(db)
        self.traindata_ctrl = TrainDataController(db)

    def process(self):
        """ Process """
        #First of all clean up
        try:
            _error, jobs_to_finish = self.job_ctrl.get_finished_jobs()
            if _error == 0:
                for job in jobs_to_finish:
                    self.job_ctrl.update_job(job['id'], 
                        status=job['status'],
                        last_run=job['updated_time'],
                        next_run=job['next_time'],
                        last_run_duration=job['run_duration']
                    )            
        except Exception as e:           
            print(f'Job cleanup failed with {e}')

        task = self.job_ctrl.get_job()
        if (task!=-1):
            print(f'current job status: {task.status}')
        else:
            print('Worker: No active tasks')
            return

        #current_time = datetime.utcnow().strftime("%Y/%m/%d %H:%M%:%S")
        self.job_ctrl.update_job(task.id, status='RUNNING', last_run='now()')
        api_client = PrometheusClient(task.prometheus_url,
                                      task.metric,
                                      task.query_filter,
                                      task.forecast_horizon,
                                      task.forecast_frequency)
        series = api_client.getSeries()
        self.traindata_ctrl.insert(task.id, series)
    
        #self.job_ctrl.update_job(task.id, status='FINISHED')