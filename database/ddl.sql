/*Clean up*/
drop table if exists publisher cascade;
drop table if exists song cascade;
drop table if exists contract_t;
drop table if exists song_stats;
drop table if exists version cascade;
drop table if exists user_t cascade;
drop table if exists user_email cascade;
drop table if exists user_stats;
drop table if exists privilege cascade;
drop table if exists have_privilege;
drop table if exists requires_privilege;
drop table if exists play_list cascade;
drop table if exists include_song;
drop domain if exists email_type cascade;
drop type if exists lang cascade;
drop type if exists label_type;

create table publisher (
    publisher_id int not null,
    publisher_name varchar(20),
    primary key (publisher_id)
);

/*Supported Language Version*/
create type lang as enum('EN-US', 'ZH-CN', 'JA-JP', 'RU-RU', 'KO-KR');

create table contract_t (
    contract_id int not null,
    publisher_id int not null,
    contract_title varchar(50),
    start_date timestamp,
    end_date timestamp,
    primary key(contract_id),
    foreign key (publisher_id) references publisher (publisher_id)
);

create table song (
    song_id int not null,
    contract_id int not null,
    title varchar(40) not null,
    language lang not null,
    description text,
    artist varchar(20),
    primary key (song_id),
    foreign key (contract_id) references contract_t (contract_id)
);

create table song_stats (
    song_id int not null,
    week_start timestamp,
    week_end timestamp,
    hit_rate int,
    avg_rating numeric(2),
    primary key (song_id, week_start, week_end),
    foreign key (song_id) references song (song_id)
);

create table version (
    song_id int not null,
    version_id int not null,
    version_name varchar(20),
    resource_url varchar(20),
    primary key (song_id, version_id),
    foreign key (song_id) references song (song_id)
);

/*only accept email of form ***@***.*** */
create domain email_type as varchar(50)
check (
    value ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'
);

create table user_t (
    user_email email_type not null,
    alias varchar(20) not null,
    password varchar(50) not null,
    primary key (user_email)
);

create table user_stats (
    user_email email_type not null,
    week_start timestamp not null,
    week_end timestamp not null,
    active_hours numeric(2),
    favorite_song int,
    primary key (user_email, week_start, week_end),
    foreign key (favorite_song) references song (song_id),
    foreign key (user_email) references user_t (user_email)
);

create table privilege (
    title varchar(10) not null,
    description text,
    primary key (title)
);

/*User can have multiple privilege, e.g., normal login user & vip*/
create table have_privilege (
    user_email email_type not null,
    privilege_title varchar(10) not null,
    primary key (user_email, privilege_title),
    foreign key (user_email) references user_t (user_email),
    foreign key (privilege_title) references privilege (title)
);

create table requires_privilege (
    song_id int not null,
    version_id int not null,
    privilege_title varchar(10) not null,
    primary key (song_id, version_id, privilege_title),
    foreign key (song_id, version_id) references version (song_id, version_id),
    foreign key (privilege_title) references privilege (title)
);

/*labels of choice*/
create type label_type as enum('Pop', 'Classic', 'Nostalgic', 'Remix', 'None');

create table play_list (
    play_list_id SERIAL,
    created_by email_type not null,
    title varchar(40),
    description text,
    creation_time timestamp,
    label label_type,
    primary key (play_list_id),
    foreign key (created_by) references user_t (user_email),
    unique(created_by, title)
);

create table include_song (
    play_list_id int not null,
    song_id int not null,
    primary key (play_list_id, song_id),
    foreign key (play_list_id) references play_list (play_list_id),
    foreign key (song_id) references song (song_id)
);