class Job(object):
    """ Class Job """
    def __init__(self,
                 id,
                 prometheus_url,
                 metric,
                 query_filter,
                 forecast_horizon,
                 forecast_frequency,
                 status,
                 last_run,
                 next_run,
                 last_run_duration):
        self.id = id
        self.prometheus_url = prometheus_url
        self.metric = metric
        self.query_filter = query_filter
        self.forecast_horizon = forecast_horizon
        self.forecast_frequency = forecast_frequency
        self.status = status
        self.last_run = last_run
        self.next_run = next_run
        self.last_run_duration = last_run_duration


    def validate(self):
        """ Check input parameters and fill calculated fields """
        pass
