import logging
import tornado.web

from prometheus_client import generate_latest
from prometheus_client.core import (REGISTRY, GaugeMetricFamily,
    CounterMetricFamily)

class HealthzUpHandler(tornado.web.RequestHandler):
    """ Tornado Handler for /healthz/metrics endpoint """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    def initialize(self, ref_object):
        self.obj = ref_object

    def get(self):
        value = self.obj.ping()
        self.write(value)

    def on_finish(self):
        self.obj = None


class HealthzReadyHandler(tornado.web.RequestHandler):
    """ Tornado Handler for /healthz/metrics endpoint """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    def initialize(self, ref_object):
        self.obj = ref_object

    def get(self):
        value = self.obj.ping()
        self.write(value)

    def on_finish(self):
        self.obj = None


class HealthzMetricHandler(tornado.web.RequestHandler):
    """ Tornado Handler for /healthz/metrics endpoint """
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    def initialize(self, ref_object):
        self.obj = ref_object

    def get(self):
        value = self.obj.ping()
        self.write(value)

    def on_finish(self):
        self.obj = None