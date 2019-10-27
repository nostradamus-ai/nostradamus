import os
import json
import pandas as pd
from datetime import datetime

from nostradamus.models.prophet import Prophet
from nostradamus.database.postgres import DbController
from nostradamus.database.jobcontroller import JobController
from nostradamus.database.forecastcontroller import ForecastController
from nostradamus.database.traindatacontroller import TrainDataController

class Forecaster(object):
    """ TBD """

    def __init__(self):
        db = DbController(user='postgres',
                          password='n9s-pgpass',
                          host='localhost',
                          port=5432,
                          database='postgres',
                          pool_max_size=2)   
        if db.ping() == 0:
            print ("Forecaster: Ping OK")

        self.job_ctrl = JobController(db)
        self.traindata_ctrl = TrainDataController(db)
        self.forecast_ctrl = ForecastController(db)


    def process(self):
        """ TBD """
        args = []

        _error, _data = self.traindata_ctrl.get()
        if _error == -1:
            print('No active tasks')            
            return
        elif _error == -2:
            print('Failed to get tasks')
            return

        rec_id = _data['id']
        job_id = _data['job_id']
        data = _data['data']

        self.traindata_ctrl.update(rec_id, status='RUNNING')

        # get job attributes
        job = self.job_ctrl.get_job_by_id(job_id)

        # get preloaded data for futher training
        data = json.loads(data)
        for item in data:
            labels = item
            df = pd.DataFrame.from_dict(data[item])           
        df.columns = ['ds','y']
        df['ds'] = pd.to_datetime(df['ds'], unit='s')

        # create model and forecast
        model = Prophet(
            train_df=df,
            forecast_horizon=job.forecast_horizon,
            forecast_frequency=job.forecast_frequency
        )
        forecast = model.forecast()

        #prepare dict of params for bulk insert
        for item in forecast:
            item['job_id']=job.id
            item['metric_labels']=labels
            args.append(item)
        
        # save forecast into database
        try:
            self.forecast_ctrl.save_forecast_bulk(args)
            self.traindata_ctrl.update(rec_id, status='FINISHED')
        except Exception as e:
            self.traindata_ctrl.update(rec_id, status='ERROR')
            print(f'Save forecast failed: {e}')

        #self.job_ctrl.update_job(task.id, status='RUNNING', last_run='now()')
        #self.traindata_ctrl.saveSeries(task.id, series)