CREATE TABLE public.emails (
	id serial4 NOT NULL,
	email_id varchar(150) NULL,
	is_spam bool NULL,
	sender_address varchar(150) NULL,
	sender_name varchar(150) NULL,
	subject varchar(250) NULL,
	create_datetime_utc TIMESTAMPTZ NOT NULL,
	update_datetime_utc TIMESTAMPTZ NULL,
	source VARCHAR(20) NULL
	CONSTRAINT emails_pkey PRIMARY KEY (id)
);