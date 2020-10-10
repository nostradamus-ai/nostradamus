import time
import json
import logging
import requests

from nostradamus.external import constant

logger = logging.getLogger('external.prometheus')

class Client(object):
    """ TBD """
    def __init__(self,
                 prometheus_url,
                 metric,
                 query_filter,
                 forecast_horizon,
                 forecast_frequency):
        self.prometheus_url = prometheus_url
        self.metric = metric
        self.query_filter = query_filter
        self.forecast_horizon = forecast_horizon
        self.forecast_frequency = forecast_frequency


    def http_get(self,
                 url,
                 params):
        """ TBD """
        result = []

        try:
            resp = requests.get(url=url, params=params, timeout=10)
            #resp.raise_for_status()
            if resp.status_code==200:
                resp = resp.json()
                if resp['status']=='success':
                    result = resp['data']['result']
                    return 0, result
            else:
                logger.error(f'http_get {result}')
                return -1, result
        except Exception as e:
            logger.error(f'Failed to execute "http_get method": {e}')
            return -1, result


    def getKeys(self):
        """ TBD """
        values = []

        api_url = self.prometheus_url + constant.API_QUERY_ENDPOINT

        if self.query_filter is not None and len(self.query_filter)>0:
            metric = self.metric + '{' + self.query_filter + '}'
        else:
            metric = self.metric

        payload = {"query":metric}
        error, keys = self.http_get(api_url, payload)
        print(f'{error}: {keys}')
        if error == 0:
            for key in keys:
                # remove __name__ from the list of labels
                del key['metric']['__name__']
                values.append(key['metric'])
            return 0, values
        else:
            return -1, values


    def getSeries(self):
        """ TBD """
        series = []
        current_time = int(time.time())
        start_time = current_time - self.calcTimeShift(self.forecast_horizon)

        api_url = self.prometheus_url + constant.API_QUERY_RANGE_ENDPOINT

        error, keys = self.getKeys()
        if error != 0:
            logger.error('Failed to get keys for a metric')
            return error, None

        for key in keys:
            # convert dict to promql filter format
            query = ''
            for item in key:
                query = query + f'{item}="{key[item]}",'

            # add additional required parameters for range query
            payload = {
                "query": self.metric + '{' + query + '}',
                "step": self.forecast_frequency,
                "start": start_time,
                "end": current_time
            }
            error, data = self.http_get(api_url, payload)
            if error == 0:
                #make a dict of [metric_labels: dict of metric values]
                for item in data:
                    series.append( {query: item['values']} )
            else:
                logger.error(
                    f'http_get failed with error {error}. payload: {payload}'
                )

        if len(series) > 0:
            return 0, series
        else:
            return -1, series


    @staticmethod
    def calcTimeShift(horizon):
        """ TBD """

        day = 24 * 60 * 60
        time_shift = 0

        if horizon == '1h':
            time_shift = 1 * day
        elif horizon == '6h':
            time_shift = 7 * day
        elif horizon == '12h':
            time_shift = 14 * day
        elif horizon == '1d':
            time_shift = 28 * day
        elif horizon == '7d':
            time_shift = 56 * day
        elif horizon == '30d':
            time_shift = 180 * day
        elif horizon == '90d':
            time_shift = 540 * day
        elif horizon == '180d':
            time_shift = 1080 * day
        elif horizon == '365d':
            time_shift = 1825 * day
        else:
            pass

        return time_shift
