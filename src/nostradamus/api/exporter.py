import json 
import logging
import tornado.web

from nostradamus.database.forecastcontroller import ForecastController

from prometheus_client import generate_latest
from prometheus_client.core import REGISTRY, GaugeMetricFamily
from prometheus_client.core import CounterMetricFamily, HistogramMetricFamily

class Collector(object):
    """ Worker class """

    def __init__(self, db):
        self.forecast_ctrl = ForecastController(db)


    def generate_latest_scrape(self):
        """ Return a content of Prometheus registry """
        return generate_latest(REGISTRY)


    def collect(self):
        """ Process """
        metrics = []
        try:
            _error, forecast = self.forecast_ctrl.get_forecast()
            if _error != 0:
                print(f'Error get_forecast. {_error}')
                return

            for item in forecast:
                metric = item['metric']
                yhat = item['yhat']
                yhat_lower = item['yhat_lower']
                yhat_upper = item['yhat_upper']

                _labels, _values = self.labels_str2dict(item['metric_labels'])

                m_yhat = GaugeMetricFamily(f'n9s_yhat_{metric}',
                    'YHAT. Mean value of the prediction',
                    labels=_labels
                )
                m_yhat_lower = GaugeMetricFamily(f'n9s_yhat_lower_{metric}',
                    'YHAT Lower. The low value of uncertainty interval',
                    labels=_labels
                )
                m_yhat_upper = GaugeMetricFamily(f'n9s_yhat_upper_{metric}',
                    'YHAT Upper. The high value of uncertainty interval',
                    labels=_labels
                )                                        
                m_yhat.add_metric(_values, yhat)
                m_yhat_lower.add_metric(_values, yhat_lower)
                m_yhat_upper.add_metric(_values, yhat_upper)                                

                metrics.append(m_yhat)
                metrics.append(m_yhat_lower)
                metrics.append(m_yhat_upper)

            for m in metrics:
                yield m

        except Exception as e:
            print(f'Exporter failed: {e}')


    @staticmethod
    def labels_str2dict(str):
        """ TBD """
        values = []
        labels = []

        if str[-1]==',':
            str=str[0:-1]
        if str[-1]=='"':
            str=str[0:-1]

        pairs = str.split('",')
        for pair in pairs:
            k, v = pair.split('="')
            labels.append(k)
            values.append(v)            

        return labels, values


class MetricHandler(tornado.web.RequestHandler):
    """ Tornado Handler for /metrics endpoint """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    def initialize(self, ref_object):
        self.obj = ref_object

    def get(self):
        self.obj.collect()
        value = self.obj.generate_latest_scrape()
        self.write(value)

    def on_finish(self):
        self.obj = None