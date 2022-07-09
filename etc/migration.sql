alter table job add column retry_count integer;

comment on column job.retry_count is 'Count of retries';