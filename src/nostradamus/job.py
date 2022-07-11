class Job(object):
    """ Class Job """
    def __init__(self,
                 id,
                 metric_alias,
                 range_query,
                 prometheus_url,
                 forecast_horizon,
                 forecast_frequency,
                 optimize_function,
                 status,
                 last_run,
                 next_run,
                 last_run_duration,
                 retry_count):
        self.id = id
        self.metric_alias = metric_alias
        self.range_query = range_query
        self.prometheus_url = prometheus_url
        self.forecast_horizon = forecast_horizon
        self.forecast_frequency = forecast_frequency
        self.optimize_function = optimize_function
        self.status = status
        self.last_run = last_run
        self.next_run = next_run
        self.last_run_duration = last_run_duration
        self.retry_count = retry_count

    def validate(self):
        """ Check input parameters and fill calculated fields """
        pass
