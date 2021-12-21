drop table job CASCADE;

create table job
(
    id serial primary key,
    metric_alias varchar(100) not null,
    range_query varchar(255),
    prometheus_url varchar(255) not null,
    forecast_horizon varchar(4) not null check
        (forecast_horizon in ('1h','6h','12h','1d','7d','30d','90d','180d','365d')),
    forecast_frequency varchar(2) not null check
        (forecast_frequency in ('5m','10m','1h','3h','1d')),
    optimize_function varchar(5) check
        (upper(optimize_function) in ('MSE','RMSE','MAE','MAPE','MDAPE')),
    status varchar(10) not null check
        (status in ('FETCHING','NEW','RUNNING','ERROR','FINISHED','DISABLED')),
    last_run timestamp with time zone default null,
    next_run timestamp with time zone default null,
    last_run_duration integer
);
comment on column job.metric_alias is 'Metric alias, used as a part of forecast metrics name';
comment on column job.range_query is 'Primary PromQL query';
comment on column job.prometheus_url is 'Prometheus API url with metrics to fetch';
comment on column job.forecast_horizon is 'Horizon of forecast. Available options: 1h, 6h, 12h, 1d, 7d, 30d, 90d, 180d, 365d';
comment on column job.forecast_frequency is 'Frequency of forecast. Available options: 5m, 10m, 1h, 3h, 1d';
comment on column job.optimize_function is 'KPI for hyper parameters tuning. Options: MSE, RMSE, MAE, MAPE, MDAPE. Use wisely';
comment on column job.status is 'Current status of the job. Available options: NEW, FETCHING, RUNNING, ERROR, FINISHED, DISABLED';
comment on column job.last_run is 'Date of job last run';
comment on column job.next_run is 'Date of job next run';
comment on column job.last_run_duration is 'Elapsed time of last job execution in seconds';


insert into job values (
    default,
    'node_cpu_seconds_total:sum_mode:increase:5m',
    'sum(increase(node_cpu_seconds_total{mode=~".*"}[5m])) by (mode)',
    'http://localhost:9090/',
    '1h',
    '5m',
    null,
    'NEW',
    null,
    null,
    null);



create table optimizer_findings
(
    ins_time timestamp with time zone not null default now(),
    status varchar(10) not null check
        (status in ('NEW','RUNNING','ACTUAL','STALE')),
    job_id integer not null,
    metric_labels varchar(512),
    optimize_function varchar(5),
    changepoint_prior_scale real,
    seasonality_prior_scale real,
    holiday_prior_scale real,
    run_duration integer
);
comment on column optimizer_findings.ins_time is 'Model evaluation date';
comment on column optimizer_findings.status is 'Status of optimizer task. Available options: NEW, FETCHING, RUNNING, ACTUAL, STALE';
comment on column optimizer_findings.job_id is 'Job Id';
comment on column optimizer_findings.metric_labels is 'Timeseries labels';
comment on column optimizer_findings.optimizer_findings is 'KPI function used to optimize a model';
comment on column optimizer_findings.changepoint_prior_scale is 'current best value of changepoint_prior_scale parameter';
comment on column optimizer_findings.seasonality_prior_scale is 'current best value of seasonality_prior_scale parameter';
comment on column optimizer_findings.holiday_prior_scale is 'current best value of holiday_prior_scale parameter';
comment on column optimizer_findings.run_duration is 'elapsed seconds';


create table forecast
(
    ins_time timestamp with time zone not null default now(),
    ds_from timestamp with time zone not null,
    ds_to timestamp with time zone not null,
    job_id integer not null,
    metric_labels varchar(512),
    yhat real not null,
    yhat_lower real not null,
    yhat_upper real not null,
    FOREIGN KEY (job_id) REFERENCES job(id)
);
comment on column forecast.ins_time is 'Modification date';
comment on column forecast.ds_from is 'Beginning of forecast interval';
comment on column forecast.ds_to is 'End of forecast interval';
comment on column forecast.job_id is 'Job Id';
comment on column forecast.metric_labels is 'Labels for forecasted timeseries';
comment on column forecast.yhat is 'Forecast';
comment on column forecast.yhat_lower is 'Lower margin of the Forecast';
comment on column forecast.yhat_upper is 'Upper margin of the Forecast';

create table train_data
(
    id serial primary key,
    ins_time timestamp with time zone not null default now(),
    job_id integer not null,
    status varchar(32) not null default 'NEW'
        check (status in ('NEW','RUNNING','FINISHED','ERROR')),
    created_time timestamp with time zone not null default (now() at time zone 'utc'),
    updated_time timestamp with time zone,
    data text,
    FOREIGN KEY (job_id) REFERENCES job(id)
);
comment on column train_data.ins_time is 'Modification date';
comment on column train_data.job_id is 'Job Id';
comment on column train_data.status is 'Status of forecasting timeseries. Available options: NEW, RUNNING, FINISHED, ERROR';
comment on column train_data.created_time is 'Time when series were loaded';
comment on column train_data.updated_time is 'Time when task was updated';
comment on column train_data.data is 'Values of historic timeseries';

create table supplemental_train_data
(
    job_id integer not null,
    data text,
    FOREIGN KEY (job_id) REFERENCES job(id)
);
comment on column train_data.job_id is 'Job Id';
comment on column train_data.data is 'Values of supplemental historical timeseries';
