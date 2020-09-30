import json
import logging

logger = logging.getLogger('database.forecastcontroller')

class ForecastController(object):
    """ TBD """

    def __init__(self,
                 db_controller):
        self.db_controller = db_controller


    def get_forecast(self):
        """ TBD """
        data = []
        try:
            query = "SELECT j.metric, f.metric_labels, \
                    f.yhat, f.yhat_lower, f.yhat_upper \
                    FROM forecast f JOIN \
                        job j ON f.job_id = j.id \
                WHERE now() BETWEEN f.ds_from AND f.ds_to \
                LIMIT 1;"

            result = self.db_controller.select(query, args=None)
            if (result):
                for row in result:
                    data.append(row)
                return 0, data
            else:
                return -1, None

        except Exception as error :
            logger(f'Failed to execute "get_forecast" method: {error}')
            return -1, None


    def save_forecast_bulk(self,
                           forecast):
        """ TBD """
        query = "INSERT INTO forecast (ds_from, ds_to, job_id, metric_labels,\
            yhat, yhat_lower, yhat_upper) \
        VALUES (%(ds_from)s, %(ds_to)s, %(job_id)s, %(metric_labels)s, \
            %(yhat)s, %(yhat_lower)s, %(yhat_upper)s);"
        try:
            self.db_controller.insert_bulk(query, forecast)
        except Exception as error:
            logger(f'Failed to execute "save_forecast_bulk" method: {error}')