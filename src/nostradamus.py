import os
import time
import tornado.web
import tornado.ioloop

from prometheus_client.core import REGISTRY

from nostradamus.worker import Worker
from nostradamus.forecaster import Forecaster
from nostradamus.database.postgres import DbController
from nostradamus.api.exporter import Collector, MetricHandler


def get_config(config_name,
               default_value):
    try:
        value = os.environ[config_name]
    except:
        value = default_value
    finally:
        return value


if __name__ == "__main__":
    #Init config
    work_mode = get_config('N9S_WORK_MODE', 'WORKER')
    interval = get_config('N9S_WORKER_INVOKE_INTERVAL', 10)

    pg_host = get_config('N9S_PG_HOST', 'localhost')
    pg_port = get_config('N9S_PG_PORT', 5432)
    pg_db   = get_config('N9S_PG_DATABASE', 'postgres')
    pg_user = get_config('N9S_PG_USER', 'postgres')
    pg_pass = get_config('N9S_PG_PASS', 'n9s-pgpass')
    pg_pool = get_config('N9S_PG_POOL_SIZE', 5)

    db = DbController(user=pg_user,
                      password=pg_pass,
                      host=pg_host,
                      port=pg_port,
                      database=pg_db,
                      pool_max_size=pg_pool)   
    if db.ping() == 0:
        print ("Database connection pool initialized successfully")

    if work_mode == 'WORKER':
        while True:
            worker = Worker(db)
            worker.process()

            forecaster = Forecaster(db)
            forecaster.process()

            time.sleep(interval)
    else:
        REGISTRY.register(Collector(db))
        exporter = Collector(db)

        application = tornado.web.Application([
            (r"/metrics", MetricHandler, {"ref_object": exporter})
        ])

        application.listen(9345)
        tornado.ioloop.IOLoop.instance().start()