import tornado.web
import tornado.ioloop

from prometheus_client.core import REGISTRY

from nostradamus.worker import Worker
from nostradamus.forecaster import Forecaster
from nostradamus.api.exporter import Collector, MetricHandler


if __name__ == "__main__":
    REGISTRY.register(Collector())

    worker = Worker()
    #worker.process()

    forecaster = Forecaster()
    #forecaster.process()

    exporter = Collector()
    #exporter.collect()

    application = tornado.web.Application([
        (r"/metrics", MetricHandler, {"ref_object": exporter})
        ]
    )

    application.listen(9345)
    tornado.ioloop.IOLoop.instance().start()