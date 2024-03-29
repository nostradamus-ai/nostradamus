import os
import json
import logging
import pandas as pd
from datetime import datetime

from nostradamus.models.prophet import Prophet
from nostradamus.database.jobcontroller import JobController
from nostradamus.database.forecastcontroller import ForecastController
from nostradamus.database.traindatacontroller import TrainDataController

logger = logging.getLogger('forecaster')

class Forecaster(object):
    """ TBD """

    def __init__(self, db):
        self.job_ctrl = JobController(db)
        self.traindata_ctrl = TrainDataController(db)
        self.forecast_ctrl = ForecastController(db)


    def process(self):
        """ TBD """
        args = []

        _error, _data = self.traindata_ctrl.get()
        if _error == -1:
            logger.debug('No active tasks')
            return
        elif _error == -2:
            logger.error('Failed to get train data')
            return

        rec_id = _data['id']
        job_id = _data['job_id']
        data = json.loads(_data['data'])

        _error, _data = self.traindata_ctrl.get_supplemental_data(job_id)
        if _error==0:
            if _data and len(_data)>0:
                sup_data = json.loads(_data['data'])

                for labels in data.keys():
                    if labels in sup_data.keys():
                        for sup_values in sup_data[labels]:
                            data[labels].append(sup_values)

        self.traindata_ctrl.update(rec_id, status='RUNNING')
        logger.info(f'Forecasting for job_id: {job_id} started')

        # get job attributes
        job = self.job_ctrl.get_job_by_id(job_id)

        # get preloaded data for futher training
        for item in data:
            labels = item
            df = pd.DataFrame.from_dict(data[item])
        df.columns = ['ds','y']
        df['ds'] = pd.to_datetime(df['ds'], unit='s')

        # Delete previously generated forecast for the metric
        logger.info(f'Cleaning up forecast for labels: {labels}')
        self.forecast_ctrl.cleanup(job_id, labels)

        # create model and forecast
        model = Prophet(
            train_df=df,
            forecast_horizon=job.forecast_horizon,
            forecast_frequency=job.forecast_frequency
        )
        _error, forecast = model.predict()

        if _error != 0:
            self.traindata_ctrl.update(rec_id,
                status='ERROR',
                updated_time='now()'
            )
            logger.error('Prediction failed')
            return

        #prepare dict of params for bulk insert
        for item in forecast:
            item['job_id']=job.id
            item['metric_labels']=labels
            args.append(item)

        # save forecast into database
        try:
            self.forecast_ctrl.save_forecast_bulk(args)
            self.traindata_ctrl.update(rec_id,
                status='FINISHED',
                updated_time='now()'
            )
            logger.info('Forecast finished successfully')
        except Exception as e:
            self.traindata_ctrl.update(rec_id,
                status='ERROR',
                updated_time='now()'
            )
            logger.error(f'Failed to save forecast. Error: {e}')