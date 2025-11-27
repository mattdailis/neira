 -- 1. create the new statuses table
  create table neira.regatta_statuses (
      regatta_id integer not null references neira.regattas(id) on delete cascade,
      status text not null,
      scrape_id bigint,
      created_at timestamptz not null default now(),
      primary key (regatta_id, status)
  );

  -- 3. migrate existing status data
  insert into neira.regatta_statuses (regatta_id, status, scrape_id)
  select id, status, scrape_id
  from neira.regattas;

  -- 4. drop the old status column
  alter table neira.regattas drop column status;
  alter table neira.regattas drop column scrape_id;
  