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
                    logger.info(
                        f'Job {job["id"]} finished with status: {job["status"]}'
                    )
        except Exception as e:
            logger.error(f'Job cleanup failed with {e}')

        # Schedule a restart of broken jobs
        try:
            _error, jobs_to_restart = self.job_ctrl.get_broken_jobs()
            if _error == 0:
                for job in jobs_to_restart:
                    if job['retry_count'] >= 5:
                        logger.info(f'Job {job["id"]} exceeded retries count')
                        continue

                    self.job_ctrl.update_job(job['id'],
                        status='NEW',
                        next_run="now() + interval '1' hour",
                        error_message='null',
                        retries_count=job['retry_count'] + 1
                    )
                    logger.info(
                        f'Job {job["id"]} was set for retry'
                    )
        except Exception as e:
            logger.error(f'Job retry failed with {e}')


        # Get jobs to run
        task = self.job_ctrl.get_job()
        if (task!=-1):
            logger.debug(f'current job status: {task.status}')
        else:
            logger.debug('No active tasks')
            return

        logger.info(
            f'Found a new task: job_id: {task.id}, metric: {task.metric_alias}'
        )
        logger.info(f'Cleaning previously fetched data')
        # delete previously fetched data
        self.traindata_ctrl.cleanup(task.id)

        logger.info(f'Fetching new data from {task.prometheus_url}')
        self.job_ctrl.update_job(task.id, status='FETCHING', last_run='now()')
        api_client = PrometheusClient(task.metric_alias,
                                      task.range_query,
                                      task.prometheus_url,
                                      task.forecast_horizon,
                                      task.forecast_frequency)
        error, series = api_client.getSeries()
        if error == 0:
            self.traindata_ctrl.insert(task.id, series)
            self.job_ctrl.update_job(task.id, status='RUNNING')
            logger.info(f'Running...')
        else:
            self.job_ctrl.update_job(task.id, status='ERROR')
            logger.error(f'Failed to get series from prometheus')
