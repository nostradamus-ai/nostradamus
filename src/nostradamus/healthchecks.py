import tornado.web

class LivenessProbeHandler(tornado.web.RequestHandler):
    """ Tornado Handler for /healthz/up endpoint """
    def initialize(self):
        pass

    def get(self):
        self.set_status(200)

    def on_finish(self):
        pass

class ReadinessProbeHandler(tornado.web.RequestHandler):
    """ Tornado Handler for /healthz/ready endpoint """
    def initialize(self,ref_object):
        self.obj = ref_object

    def get(self):
        res = self.obj.ping()
        if res == 0:
            self.set_status(200)
        else:
            self.set_status(503)

    def on_finish(self):
        self.obj = None