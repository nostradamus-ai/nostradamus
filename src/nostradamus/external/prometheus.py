import time
import json
import requests
from nostradamus.external import constant


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
        try:
            resp = requests.get(url=url, params=params, timeout=10)             
            resp.raise_for_status()
            if resp.status_code==200:
                resp = resp.json()
                if resp['status']=='success':
                    return resp['data']['result']
            else:
                return -1
        except Exception as e:
            print (f'Exception: {e}')


    def getKeys(self):
        """ TBD """
        values = []

        api_url = self.prometheus_url + constant.API_QUERY_ENDPOINT

        if self.query_filter is not None and len(self.query_filter)>0:
            metric = self.metric + '{' + self.query_filter + '}'
        else:
            metric = self.metric

        payload = {"query":metric}
        keys = self.http_get(api_url, payload)
        for key in keys:
            # remove __name__ from the list of labels
            del key['metric']['__name__']
            values.append(key['metric'])
        
        return values


    def getSeries(self):
        """ TBD """
        series = []
        current_time = int(time.time())
        start_time = current_time - self.calcTimeShift(self.forecast_horizon)

        api_url = self.prometheus_url + constant.API_QUERY_RANGE_ENDPOINT        

        keys = self.getKeys()
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
            data = self.http_get(api_url, payload)
            #make a dict of [metric_labels: dict of metric values]
            for item in data:
                series.append( {query: item['values']} )
        
        return(series)


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
