import os
from datetime import datetime

from nostradamus.database.postgres import DbController
from nostradamus.database.jobcontroller import JobController
from nostradamus.database.traindatacontroller import TrainDataController
from nostradamus.external.prometheus import Client as PrometheusClient


class Worker(object):
    """ Worker class """

    def __init__(self):
        db = DbController(user='postgres',
                          password='n9s-pgpass',
                          host='localhost',
                          port=5432,
                          database='postgres',
                          pool_max_size=2)   
        if db.ping() == 0:
            print ("Worker: Ping OK")

        self.job_ctrl = JobController(db)
        self.traindata_ctrl = TrainDataController(db)

    def process(self):
        """ Process """
        task = self.job_ctrl.get_job()
        if (task!=-1):
            print(f'current job status: {task.status}')
        else:
            print('No active tasks')
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
        self.job_ctrl.update_job(task.id, status='FINISHED')