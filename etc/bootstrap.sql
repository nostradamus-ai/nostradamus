create table job
(
    id serial primary key,
    prometheus_url varchar(255) not null,
    metric varchar(255) not null,
    query_filter varchar(512),
    forecast_horizon varchar(4) not null check 
        (forecast_horizon in ('1h','6h','12h','1d','7d','30d','90d','180d','365d')),
    forecast_frequency varchar(4) not null check 
        (forecast_frequency in ('5m','10m','1h','3h','1d')),
    status varchar(32) not null check 
        (status in ('NEW','RUNNING','ERROR','FINISHED','DISABLED')),
    last_run timestamp with time zone default null,
    next_run timestamp with time zone default null,
    last_run_duration integer
);
comment on column job.prometheus_url is 'Prometheus API url with metrics to fetch';
comment on column job.metric is 'Metric name';
comment on column job.query_filter is 'PromQL filter query';
comment on column job.forecast_horizon is 'Horizon of forecast. Available options: 1h, 6h, 12h, 1d, 7d, 30d, 90d, 180d, 365d';
comment on column job.forecast_frequency is 'Frequency of forecast. Available options: 5m, 10m, 1h, 3h, 1d';
comment on column job.status is 'Current status of the job. Available options: NEW, RUNNING, ERROR, FINISHED, DISABLED';
comment on column job.last_run is 'Date of job last run';
comment on column job.next_run is 'Date of job next run';
comment on column job.last_run_duration is 'Elapsed time of last job execution';

create table forecast
(
    ds_from timestamp with time zone not null,
    ds_to timestamp with time zone not null,  
    job_id integer not null,
    metric_labels varchar(512),
    yhat real not null,
    yhat_lower real not null,
    yhat_upper real not null,
    FOREIGN KEY (job_id) REFERENCES job(id)
);
comment on column forecast.ds_from is 'Begining of forecast interval';
comment on column forecast.ds_to is 'End of forecast interval';
comment on column forecast.job_id is 'Job id';
comment on column forecast.metric_labels is 'Labels for forecasted timeseries';
comment on column forecast.yhat is 'Forecast';
comment on column forecast.yhat_lower is 'Lower margin of the Forecast';
comment on column forecast.yhat_upper is 'Upper margin of the Forecast';

--create extension hstore;
create table train_data
(
    id serial primary key,
    job_id integer not null,
    status varchar(32) not null default 'NEW'
        check (status in ('NEW','RUNNING','FINISHED','ERROR')),
    created_time timestamp with time zone not null default (now() at time zone 'utc'),
    data text,
    FOREIGN KEY (job_id) REFERENCES job(id)
);
comment on column train_data.status is 'Status of forecasting timeseries. Available options: NEW, RUNNING, FINISHED, ERROR';
comment on column train_data.created_time is 'Time when series were loaded';
comment on column train_data.data is 'Values of historic timeseries';

insert into job values (default,'http://n9s-ps/','some_metric',null,'1d','10m','NEW',null,null);