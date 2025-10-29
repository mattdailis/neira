create schema neira;

create table neira.schools(
    id integer primary key generated always as identity,
    name text not null
);

create table neira.school_aliases(
    school_id integer not null references neira.schools,
    alias text not null
);

create table neira.neira_schools_by_year(
    school_id integer references neira.schools,
    year integer not null
);

create table neira.regattas(
    id integer primary key generated always as identity,
    scrape_id integer not null,
    uid text not null,
    year integer not null,
    date text not null,
    name text not null,
    status text not null
);

create table neira.heats(
    id integer primary key generated always as identity,
    regatta_id integer references neira.regattas,
    class text,
    gender text
);

create table neira.results(
    heat_id integer not null references neira.heats,
    finish_order integer not null,
    raw_time text not null,
    margin_from_winner decimal,

    primary key (heat_id, finish_order)
);
