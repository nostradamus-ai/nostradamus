import os
import logging

from datetime import datetime

from nostradamus.database.jobcontroller import JobController
from nostradamus.database.traindatacontroller import TrainDataController
from nostradamus.external.prometheus import Client as PrometheusClient

logger = logging.getLogger('worker')

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
            logger.error(f'Job cleanup failed with {e}')

        task = self.job_ctrl.get_job()
        if (task!=-1):
            logger.debug(f'current job status: {task.status}')
        else:
            logger.info('No active tasks')
            return

        self.job_ctrl.update_job(task.id, status='FETCHING', last_run='now()')
        api_client = PrometheusClient(task.prometheus_url,
                                      task.metric,
                                      task.query_filter,
                                      task.forecast_horizon,
                                      task.forecast_frequency)
        error, series = api_client.getSeries()
        if error == 0:
            self.traindata_ctrl.insert(task.id, series)
            self.job_ctrl.update_job(task.id, status='RUNNING')
        else:
            self.job_ctrl.update_job(task.id, status='ERROR')
            logger.error(f'Failed to get series from prometheus')
