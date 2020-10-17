class Job(object):
    """ Class Job """
    def __init__(self,
                 id,
                 prometheus_url,
                 metric,
                 query_filter,
                 range_function,
                 optimize_function,
                 forecast_horizon,
                 forecast_frequency,
                 status,
                 last_run,
                 next_run,
                 last_run_duration,
                 last_validation):
        self.id = id
        self.prometheus_url = prometheus_url
        self.metric = metric
        self.query_filter = query_filter
        self.range_function = range_function
        self.optimize_function = optimize_function
        self.forecast_horizon = forecast_horizon
        self.forecast_frequency = forecast_frequency
        self.status = status
        self.last_run = last_run
        self.next_run = next_run
        self.last_run_duration = last_run_duration


    def validate(self):
        """ Check input parameters and fill calculated fields """
        pass
