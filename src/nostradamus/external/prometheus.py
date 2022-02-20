import os
import re
import time
import logging
import requests

from nostradamus.external import constant

logger = logging.getLogger('external.prometheus')

class Client(object):
    """ TBD """
    def __init__(self,
                 metric_alias,
                 range_query,
                 prometheus_url,
                 forecast_horizon,
                 forecast_frequency):
        self.metric = metric_alias
        self.range_query = range_query
        self.prometheus_url = prometheus_url
        self.forecast_horizon = forecast_horizon
        self.forecast_frequency = forecast_frequency

        try:
            self.timeout = os.environ['N9S_PS_TIMEOUT']
        except:
            self.timeout = 10


    def http_get(self,
                 url,
                 params):
        """ TBD """
        result = []

        try:
            resp = requests.get(url=url, params=params, timeout=self.timeout)
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

        payload = {"query": self.range_query}
        error, keys = self.http_get(api_url, payload)

        if error == 0:
            for key in keys:
                # remove __name__ from the list of labels
                try:
                    del key['metric']['__name__']
                except:
                    pass
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
            filters, query = '', ''
            for item in key:
                filters = filters + f'{item}="{key[item]}",'
            query = self.makeQuery(self.range_query, filters)

            # add additional required parameters for range query
            payload = {
                "query": query,
                "step": self.forecast_frequency,
                "start": start_time,
                "end": current_time
            }
            error, data = self.http_get(api_url, payload)
            if error == 0:
                #make a dict of [metric_labels: dict of metric values]
                for item in data:
                    series.append( {filters: item['values']} )
            else:
                logger.error(
                    f'http_get failed with error {error}. payload: {payload}'
                )

        if len(series) > 0:
            return 0, series
        else:
            return -1, series


    @staticmethod
    def makeQuery(range_query, filter):
        """ Prepare a range query by inserting additional labels
        in the filter statement: {} """

        if re.search(pattern='({.*})',string=range_query) is None:
            query = range_query+'{'+filter+'}'
            return query

        m=re.sub(pattern='}',
            repl=','+filter+'}',
            string=range_query,
            count=1)
        m.replace(',,',',')
        m.replace('{,','{')
        m.replace(',}','}')
        return m


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
