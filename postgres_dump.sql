--
-- PostgreSQL database cluster dump
--

\restrict mXGMjqFSwiMp4z8JSYk27gwQblEENJcToDgHnk6j0QV3moVgOJTgAX3bp4re7Ci

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE college_user;
ALTER ROLE college_user WITH NOSUPERUSER INHERIT NOCREATEROLE CREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:8q3UHVMmypGuiNdgP3lZJg==$4m8uPq58AtmCyqwjt9eLMtdPVP/SLyfFrn0XWyMrgSg=:OmzjM6UKpL9tq0r0FlhlGap6sFlgIirXNMaeCaUk3Kg=';
CREATE ROLE dbeaver_user;
ALTER ROLE dbeaver_user WITH NOSUPERUSER INHERIT NOCREATEROLE CREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:W/vakxpf6qUi4EC1249rvA==$7OyfldRtXbMKpNtJsLexg9AOSkw4D2W3t0Q8pgRRNHU=:YqiUGbNTo00XwkY7iy2Fh41OXdeZu4Ectnuj87orjOM=';
CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS;






\unrestrict mXGMjqFSwiMp4z8JSYk27gwQblEENJcToDgHnk6j0QV3moVgOJTgAX3bp4re7Ci

--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

\restrict WNOhEmBozCqohPkdMb5k1iuo0DynKmpeLIPdhZIvkWgose1qU0OJGweW4J9e9wr

-- Dumped from database version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

\unrestrict WNOhEmBozCqohPkdMb5k1iuo0DynKmpeLIPdhZIvkWgose1qU0OJGweW4J9e9wr

--
-- Database "auth_db" dump
--

--
-- PostgreSQL database dump
--

\restrict Orniy7z6X60fK6kfyzfpPSOAnPOAKrPAgTOBZqGNVZuaqB3iPxfGsCy2O3aieR7

-- Dumped from database version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: auth_db; Type: DATABASE; Schema: -; Owner: college_user
--

CREATE DATABASE auth_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'C.UTF-8';


ALTER DATABASE auth_db OWNER TO college_user;

\unrestrict Orniy7z6X60fK6kfyzfpPSOAnPOAKrPAgTOBZqGNVZuaqB3iPxfGsCy2O3aieR7
\connect auth_db
\restrict Orniy7z6X60fK6kfyzfpPSOAnPOAKrPAgTOBZqGNVZuaqB3iPxfGsCy2O3aieR7

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: users; Type: SCHEMA; Schema: -; Owner: college_user
--

CREATE SCHEMA users;


ALTER SCHEMA users OWNER TO college_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: users; Type: TABLE; Schema: public; Owner: college_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    full_name character varying NOT NULL,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO college_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: college_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO college_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: college_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users; Type: TABLE; Schema: users; Owner: college_user
--

CREATE TABLE users.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    full_name character varying NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE users.users OWNER TO college_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: users; Owner: college_user
--

CREATE SEQUENCE users.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE users.users_id_seq OWNER TO college_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: users; Owner: college_user
--

ALTER SEQUENCE users.users_id_seq OWNED BY users.users.id;


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: users; Owner: college_user
--

ALTER TABLE ONLY users.users ALTER COLUMN id SET DEFAULT nextval('users.users_id_seq'::regclass);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: college_user
--

COPY public.users (id, email, password_hash, full_name, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: users; Owner: college_user
--

COPY users.users (id, email, password_hash, full_name, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: college_user
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: users; Owner: college_user
--

SELECT pg_catalog.setval('users.users_id_seq', 1, false);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: users; Owner: college_user
--

ALTER TABLE ONLY users.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: users; Owner: college_user
--

ALTER TABLE ONLY users.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: college_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: college_user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: idx_users_email; Type: INDEX; Schema: users; Owner: college_user
--

CREATE INDEX idx_users_email ON users.users USING btree (email);


--
-- Name: idx_users_id; Type: INDEX; Schema: users; Owner: college_user
--

CREATE INDEX idx_users_id ON users.users USING btree (id);


--
-- PostgreSQL database dump complete
--

\unrestrict Orniy7z6X60fK6kfyzfpPSOAnPOAKrPAgTOBZqGNVZuaqB3iPxfGsCy2O3aieR7

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

\restrict phbRI67cqzrOD46cj5UG2zSzhOpxQ6upOw3dJYgeUtT1TWIVTuH6ie41ozb8qvf

-- Dumped from database version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: auth; Type: SCHEMA; Schema: -; Owner: college_user
--

CREATE SCHEMA auth;


ALTER SCHEMA auth OWNER TO college_user;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- PostgreSQL database dump complete
--

\unrestrict phbRI67cqzrOD46cj5UG2zSzhOpxQ6upOw3dJYgeUtT1TWIVTuH6ie41ozb8qvf

--
-- Database "schedule_db" dump
--

--
-- PostgreSQL database dump
--

\restrict D2zx1qoLrGeBVsc139ki8T1L7Vjh5hVMvujUTRwSARGHJskvgAogcTSuGjVH2qE

-- Dumped from database version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: schedule_db; Type: DATABASE; Schema: -; Owner: college_user
--

CREATE DATABASE schedule_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'C.UTF-8';


ALTER DATABASE schedule_db OWNER TO college_user;

\unrestrict D2zx1qoLrGeBVsc139ki8T1L7Vjh5hVMvujUTRwSARGHJskvgAogcTSuGjVH2qE
\connect schedule_db
\restrict D2zx1qoLrGeBVsc139ki8T1L7Vjh5hVMvujUTRwSARGHJskvgAogcTSuGjVH2qE

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: schedule; Type: SCHEMA; Schema: -; Owner: college_user
--

CREATE SCHEMA schedule;


ALTER SCHEMA schedule OWNER TO college_user;

--
-- Name: participantstatus; Type: TYPE; Schema: public; Owner: college_user
--

CREATE TYPE public.participantstatus AS ENUM (
    'REGISTERED',
    'ATTENDED',
    'ABSENT'
);


ALTER TYPE public.participantstatus OWNER TO college_user;

--
-- Name: slotstatus; Type: TYPE; Schema: public; Owner: college_user
--

CREATE TYPE public.slotstatus AS ENUM (
    'SCHEDULED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.slotstatus OWNER TO college_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auditoriums; Type: TABLE; Schema: public; Owner: college_user
--

CREATE TABLE public.auditoriums (
    id integer NOT NULL,
    name character varying NOT NULL,
    capacity integer,
    description character varying
);


ALTER TABLE public.auditoriums OWNER TO college_user;

--
-- Name: auditoriums_id_seq; Type: SEQUENCE; Schema: public; Owner: college_user
--

CREATE SEQUENCE public.auditoriums_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auditoriums_id_seq OWNER TO college_user;

--
-- Name: auditoriums_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: college_user
--

ALTER SEQUENCE public.auditoriums_id_seq OWNED BY public.auditoriums.id;


--
-- Name: class_slots; Type: TABLE; Schema: public; Owner: college_user
--

CREATE TABLE public.class_slots (
    id integer NOT NULL,
    title character varying NOT NULL,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone NOT NULL,
    instructor character varying,
    max_participants integer,
    status public.slotstatus,
    course_id integer,
    auditorium_id integer
);


ALTER TABLE public.class_slots OWNER TO college_user;

--
-- Name: class_slots_id_seq; Type: SEQUENCE; Schema: public; Owner: college_user
--

CREATE SEQUENCE public.class_slots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.class_slots_id_seq OWNER TO college_user;

--
-- Name: class_slots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: college_user
--

ALTER SEQUENCE public.class_slots_id_seq OWNED BY public.class_slots.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: college_user
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying,
    instructor character varying
);


ALTER TABLE public.courses OWNER TO college_user;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: college_user
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.courses_id_seq OWNER TO college_user;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: college_user
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: groups; Type: TABLE; Schema: public; Owner: college_user
--

CREATE TABLE public.groups (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying,
    instructor character varying
);


ALTER TABLE public.groups OWNER TO college_user;

--
-- Name: groups_id_seq; Type: SEQUENCE; Schema: public; Owner: college_user
--

CREATE SEQUENCE public.groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.groups_id_seq OWNER TO college_user;

--
-- Name: groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: college_user
--

ALTER SEQUENCE public.groups_id_seq OWNED BY public.groups.id;


--
-- Name: participants; Type: TABLE; Schema: public; Owner: college_user
--

CREATE TABLE public.participants (
    id integer NOT NULL,
    class_slot_id integer,
    user_id integer,
    status public.participantstatus
);


ALTER TABLE public.participants OWNER TO college_user;

--
-- Name: participants_id_seq; Type: SEQUENCE; Schema: public; Owner: college_user
--

CREATE SEQUENCE public.participants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.participants_id_seq OWNER TO college_user;

--
-- Name: participants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: college_user
--

ALTER SEQUENCE public.participants_id_seq OWNED BY public.participants.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: college_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    full_name character varying NOT NULL,
    telegram_id character varying
);


ALTER TABLE public.users OWNER TO college_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: college_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO college_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: college_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: schedule_auditoriums; Type: TABLE; Schema: schedule; Owner: college_user
--

CREATE TABLE schedule.schedule_auditoriums (
    id integer NOT NULL,
    name text,
    is_active boolean
);


ALTER TABLE schedule.schedule_auditoriums OWNER TO college_user;

--
-- Name: schedule_auditoriums_id_seq; Type: SEQUENCE; Schema: schedule; Owner: college_user
--

ALTER TABLE schedule.schedule_auditoriums ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME schedule.schedule_auditoriums_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: schedule_groups; Type: TABLE; Schema: schedule; Owner: college_user
--

CREATE TABLE schedule.schedule_groups (
    id integer NOT NULL,
    name text,
    course integer
);


ALTER TABLE schedule.schedule_groups OWNER TO college_user;

--
-- Name: schedule_groups_id_seq; Type: SEQUENCE; Schema: schedule; Owner: college_user
--

ALTER TABLE schedule.schedule_groups ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME schedule.schedule_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: schedule_lessons; Type: TABLE; Schema: schedule; Owner: college_user
--

CREATE TABLE schedule.schedule_lessons (
    id integer NOT NULL,
    date date,
    time_start time without time zone,
    time_end time without time zone,
    lesson_number integer,
    group_id integer,
    subgroup text,
    subject_id integer,
    teacher_id integer,
    auditorium_id integer,
    activity_type text,
    comment text,
    created_at timestamp without time zone
);


ALTER TABLE schedule.schedule_lessons OWNER TO college_user;

--
-- Name: schedule_lessons_id_seq; Type: SEQUENCE; Schema: schedule; Owner: college_user
--

ALTER TABLE schedule.schedule_lessons ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME schedule.schedule_lessons_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: schedule_subjects; Type: TABLE; Schema: schedule; Owner: college_user
--

CREATE TABLE schedule.schedule_subjects (
    id integer NOT NULL,
    name text,
    teacher_id integer
);


ALTER TABLE schedule.schedule_subjects OWNER TO college_user;

--
-- Name: schedule_subjects_id_seq; Type: SEQUENCE; Schema: schedule; Owner: college_user
--

ALTER TABLE schedule.schedule_subjects ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME schedule.schedule_subjects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: schedule_teachers; Type: TABLE; Schema: schedule; Owner: college_user
--

CREATE TABLE schedule.schedule_teachers (
    id integer NOT NULL,
    name text
);


ALTER TABLE schedule.schedule_teachers OWNER TO college_user;

--
-- Name: schedule_teachers_id_seq; Type: SEQUENCE; Schema: schedule; Owner: college_user
--

ALTER TABLE schedule.schedule_teachers ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME schedule.schedule_teachers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auditoriums id; Type: DEFAULT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.auditoriums ALTER COLUMN id SET DEFAULT nextval('public.auditoriums_id_seq'::regclass);


--
-- Name: class_slots id; Type: DEFAULT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.class_slots ALTER COLUMN id SET DEFAULT nextval('public.class_slots_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: groups id; Type: DEFAULT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.groups ALTER COLUMN id SET DEFAULT nextval('public.groups_id_seq'::regclass);


--
-- Name: participants id; Type: DEFAULT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.participants ALTER COLUMN id SET DEFAULT nextval('public.participants_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: auditoriums; Type: TABLE DATA; Schema: public; Owner: college_user
--

COPY public.auditoriums (id, name, capacity, description) FROM stdin;
1	string	0	string
\.


--
-- Data for Name: class_slots; Type: TABLE DATA; Schema: public; Owner: college_user
--

COPY public.class_slots (id, title, start_time, end_time, instructor, max_participants, status, course_id, auditorium_id) FROM stdin;
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: college_user
--

COPY public.courses (id, name, description, instructor) FROM stdin;
1	string	string	string
\.


--
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: college_user
--

COPY public.groups (id, name, description, instructor) FROM stdin;
1	string	string	string
\.


--
-- Data for Name: participants; Type: TABLE DATA; Schema: public; Owner: college_user
--

COPY public.participants (id, class_slot_id, user_id, status) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: college_user
--

COPY public.users (id, email, password_hash, full_name, telegram_id) FROM stdin;
2	user@example.cocaca	$2b$12$L9zAdnQgI8NnUO4F.aY.Q.Yn4IlXe1FbeGBZdVxR..mZbpYQp.QYe	Иван Иванов	\N
1	user@example.com	$2b$12$QikGwi1bwOabJGDaVMqyaeDX96IDmQs2U3CN4tDszpPhQnGLIbjry	string	1
\.


--
-- Data for Name: schedule_auditoriums; Type: TABLE DATA; Schema: schedule; Owner: college_user
--

COPY schedule.schedule_auditoriums (id, name, is_active) FROM stdin;
\.


--
-- Data for Name: schedule_groups; Type: TABLE DATA; Schema: schedule; Owner: college_user
--

COPY schedule.schedule_groups (id, name, course) FROM stdin;
\.


--
-- Data for Name: schedule_lessons; Type: TABLE DATA; Schema: schedule; Owner: college_user
--

COPY schedule.schedule_lessons (id, date, time_start, time_end, lesson_number, group_id, subgroup, subject_id, teacher_id, auditorium_id, activity_type, comment, created_at) FROM stdin;
\.


--
-- Data for Name: schedule_subjects; Type: TABLE DATA; Schema: schedule; Owner: college_user
--

COPY schedule.schedule_subjects (id, name, teacher_id) FROM stdin;
\.


--
-- Data for Name: schedule_teachers; Type: TABLE DATA; Schema: schedule; Owner: college_user
--

COPY schedule.schedule_teachers (id, name) FROM stdin;
\.


--
-- Name: auditoriums_id_seq; Type: SEQUENCE SET; Schema: public; Owner: college_user
--

SELECT pg_catalog.setval('public.auditoriums_id_seq', 1, true);


--
-- Name: class_slots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: college_user
--

SELECT pg_catalog.setval('public.class_slots_id_seq', 1, false);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: college_user
--

SELECT pg_catalog.setval('public.courses_id_seq', 1, true);


--
-- Name: groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: college_user
--

SELECT pg_catalog.setval('public.groups_id_seq', 1, true);


--
-- Name: participants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: college_user
--

SELECT pg_catalog.setval('public.participants_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: college_user
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: schedule_auditoriums_id_seq; Type: SEQUENCE SET; Schema: schedule; Owner: college_user
--

SELECT pg_catalog.setval('schedule.schedule_auditoriums_id_seq', 1, false);


--
-- Name: schedule_groups_id_seq; Type: SEQUENCE SET; Schema: schedule; Owner: college_user
--

SELECT pg_catalog.setval('schedule.schedule_groups_id_seq', 1, false);


--
-- Name: schedule_lessons_id_seq; Type: SEQUENCE SET; Schema: schedule; Owner: college_user
--

SELECT pg_catalog.setval('schedule.schedule_lessons_id_seq', 1, false);


--
-- Name: schedule_subjects_id_seq; Type: SEQUENCE SET; Schema: schedule; Owner: college_user
--

SELECT pg_catalog.setval('schedule.schedule_subjects_id_seq', 1, false);


--
-- Name: schedule_teachers_id_seq; Type: SEQUENCE SET; Schema: schedule; Owner: college_user
--

SELECT pg_catalog.setval('schedule.schedule_teachers_id_seq', 1, false);


--
-- Name: auditoriums auditoriums_name_key; Type: CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.auditoriums
    ADD CONSTRAINT auditoriums_name_key UNIQUE (name);


--
-- Name: auditoriums auditoriums_pkey; Type: CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.auditoriums
    ADD CONSTRAINT auditoriums_pkey PRIMARY KEY (id);


--
-- Name: class_slots class_slots_pkey; Type: CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.class_slots
    ADD CONSTRAINT class_slots_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);


--
-- Name: participants participants_pkey; Type: CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.participants
    ADD CONSTRAINT participants_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: schedule_auditoriums schedule_auditoriums_pk; Type: CONSTRAINT; Schema: schedule; Owner: college_user
--

ALTER TABLE ONLY schedule.schedule_auditoriums
    ADD CONSTRAINT schedule_auditoriums_pk PRIMARY KEY (id);


--
-- Name: schedule_groups schedule_groups_pk; Type: CONSTRAINT; Schema: schedule; Owner: college_user
--

ALTER TABLE ONLY schedule.schedule_groups
    ADD CONSTRAINT schedule_groups_pk PRIMARY KEY (id);


--
-- Name: schedule_lessons schedule_lessons_pk; Type: CONSTRAINT; Schema: schedule; Owner: college_user
--

ALTER TABLE ONLY schedule.schedule_lessons
    ADD CONSTRAINT schedule_lessons_pk PRIMARY KEY (id);


--
-- Name: schedule_subjects schedule_subjects_pk; Type: CONSTRAINT; Schema: schedule; Owner: college_user
--

ALTER TABLE ONLY schedule.schedule_subjects
    ADD CONSTRAINT schedule_subjects_pk PRIMARY KEY (id);


--
-- Name: schedule_teachers schedule_teachers_pk; Type: CONSTRAINT; Schema: schedule; Owner: college_user
--

ALTER TABLE ONLY schedule.schedule_teachers
    ADD CONSTRAINT schedule_teachers_pk PRIMARY KEY (id);


--
-- Name: ix_auditoriums_id; Type: INDEX; Schema: public; Owner: college_user
--

CREATE INDEX ix_auditoriums_id ON public.auditoriums USING btree (id);


--
-- Name: ix_class_slots_id; Type: INDEX; Schema: public; Owner: college_user
--

CREATE INDEX ix_class_slots_id ON public.class_slots USING btree (id);


--
-- Name: ix_courses_id; Type: INDEX; Schema: public; Owner: college_user
--

CREATE INDEX ix_courses_id ON public.courses USING btree (id);


--
-- Name: ix_groups_id; Type: INDEX; Schema: public; Owner: college_user
--

CREATE INDEX ix_groups_id ON public.groups USING btree (id);


--
-- Name: ix_participants_id; Type: INDEX; Schema: public; Owner: college_user
--

CREATE INDEX ix_participants_id ON public.participants USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: college_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: college_user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: class_slots class_slots_auditorium_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.class_slots
    ADD CONSTRAINT class_slots_auditorium_id_fkey FOREIGN KEY (auditorium_id) REFERENCES public.auditoriums(id);


--
-- Name: class_slots class_slots_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.class_slots
    ADD CONSTRAINT class_slots_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: participants participants_class_slot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.participants
    ADD CONSTRAINT participants_class_slot_id_fkey FOREIGN KEY (class_slot_id) REFERENCES public.class_slots(id);


--
-- Name: participants participants_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: college_user
--

ALTER TABLE ONLY public.participants
    ADD CONSTRAINT participants_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict D2zx1qoLrGeBVsc139ki8T1L7Vjh5hVMvujUTRwSARGHJskvgAogcTSuGjVH2qE

--
-- Database "tech_card_db" dump
--

--
-- PostgreSQL database dump
--

\restrict 1xPICBYrlfoN8btW6MxPASby2aTYXc5AepE7qpZuHUQwqMzLNx8bbbynR4qi1RW

-- Dumped from database version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: tech_card_db; Type: DATABASE; Schema: -; Owner: college_user
--

CREATE DATABASE tech_card_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'C.UTF-8';


ALTER DATABASE tech_card_db OWNER TO college_user;

\unrestrict 1xPICBYrlfoN8btW6MxPASby2aTYXc5AepE7qpZuHUQwqMzLNx8bbbynR4qi1RW
\connect tech_card_db
\restrict 1xPICBYrlfoN8btW6MxPASby2aTYXc5AepE7qpZuHUQwqMzLNx8bbbynR4qi1RW

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: tech_card; Type: SCHEMA; Schema: -; Owner: college_user
--

CREATE SCHEMA tech_card;


ALTER SCHEMA tech_card OWNER TO college_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: group_name; Type: TABLE; Schema: tech_card; Owner: college_user
--

CREATE TABLE tech_card.group_name (
    primary_key integer NOT NULL,
    curator_id integer,
    curator_group text,
    group_name text
);


ALTER TABLE tech_card.group_name OWNER TO college_user;

--
-- Name: learning_outcomes; Type: TABLE; Schema: tech_card; Owner: college_user
--

CREATE TABLE tech_card.learning_outcomes (
    primary_key integer NOT NULL,
    lesson integer,
    skill text,
    know text
);


ALTER TABLE tech_card.learning_outcomes OWNER TO college_user;

--
-- Name: lesson; Type: TABLE; Schema: tech_card; Owner: college_user
--

CREATE TABLE tech_card.lesson (
    primary_key integer NOT NULL,
    name_lesson text NOT NULL,
    "Teacher" integer,
    "Group_name" integer,
    type_lesson integer
);


ALTER TABLE tech_card.lesson OWNER TO college_user;

--
-- Name: lesson_topic; Type: TABLE; Schema: tech_card; Owner: college_user
--

CREATE TABLE tech_card.lesson_topic (
    primary_key integer NOT NULL,
    lesson integer,
    topic text
);


ALTER TABLE tech_card.lesson_topic OWNER TO college_user;

--
-- Name: lesson_type; Type: TABLE; Schema: tech_card; Owner: college_user
--

CREATE TABLE tech_card.lesson_type (
    primary_key integer NOT NULL,
    lesson_type text NOT NULL
);


ALTER TABLE tech_card.lesson_type OWNER TO college_user;

--
-- Name: name_teacher; Type: TABLE; Schema: tech_card; Owner: college_user
--

CREATE TABLE tech_card.name_teacher (
    primary_key integer NOT NULL,
    full_name text NOT NULL
);


ALTER TABLE tech_card.name_teacher OWNER TO college_user;

--
-- Name: pk_and_ok; Type: TABLE; Schema: tech_card; Owner: college_user
--

CREATE TABLE tech_card.pk_and_ok (
    primary_key integer NOT NULL,
    lesson integer,
    prof_comp text,
    general_comp text
);


ALTER TABLE tech_card.pk_and_ok OWNER TO college_user;

--
-- Name: skills_and_knowledge; Type: TABLE; Schema: tech_card; Owner: college_user
--

CREATE TABLE tech_card.skills_and_knowledge (
    primary_key integer NOT NULL,
    lesson integer,
    skill text,
    knowledge text
);


ALTER TABLE tech_card.skills_and_knowledge OWNER TO college_user;

--
-- Data for Name: group_name; Type: TABLE DATA; Schema: tech_card; Owner: college_user
--

COPY tech_card.group_name (primary_key, curator_id, curator_group, group_name) FROM stdin;
\.


--
-- Data for Name: learning_outcomes; Type: TABLE DATA; Schema: tech_card; Owner: college_user
--

COPY tech_card.learning_outcomes (primary_key, lesson, skill, know) FROM stdin;
\.


--
-- Data for Name: lesson; Type: TABLE DATA; Schema: tech_card; Owner: college_user
--

COPY tech_card.lesson (primary_key, name_lesson, "Teacher", "Group_name", type_lesson) FROM stdin;
\.


--
-- Data for Name: lesson_topic; Type: TABLE DATA; Schema: tech_card; Owner: college_user
--

COPY tech_card.lesson_topic (primary_key, lesson, topic) FROM stdin;
\.


--
-- Data for Name: lesson_type; Type: TABLE DATA; Schema: tech_card; Owner: college_user
--

COPY tech_card.lesson_type (primary_key, lesson_type) FROM stdin;
\.


--
-- Data for Name: name_teacher; Type: TABLE DATA; Schema: tech_card; Owner: college_user
--

COPY tech_card.name_teacher (primary_key, full_name) FROM stdin;
\.


--
-- Data for Name: pk_and_ok; Type: TABLE DATA; Schema: tech_card; Owner: college_user
--

COPY tech_card.pk_and_ok (primary_key, lesson, prof_comp, general_comp) FROM stdin;
\.


--
-- Data for Name: skills_and_knowledge; Type: TABLE DATA; Schema: tech_card; Owner: college_user
--

COPY tech_card.skills_and_knowledge (primary_key, lesson, skill, knowledge) FROM stdin;
\.


--
-- Name: group_name group_name_pkey; Type: CONSTRAINT; Schema: tech_card; Owner: college_user
--

ALTER TABLE ONLY tech_card.group_name
    ADD CONSTRAINT group_name_pkey PRIMARY KEY (primary_key);


--
-- Name: learning_outcomes learning_outcomes_pkey; Type: CONSTRAINT; Schema: tech_card; Owner: college_user
--

ALTER TABLE ONLY tech_card.learning_outcomes
    ADD CONSTRAINT learning_outcomes_pkey PRIMARY KEY (primary_key);


--
-- Name: lesson lesson_pkey; Type: CONSTRAINT; Schema: tech_card; Owner: college_user
--

ALTER TABLE ONLY tech_card.lesson
    ADD CONSTRAINT lesson_pkey PRIMARY KEY (primary_key);


--
-- Name: lesson_topic lesson_topic_pkey; Type: CONSTRAINT; Schema: tech_card; Owner: college_user
--

ALTER TABLE ONLY tech_card.lesson_topic
    ADD CONSTRAINT lesson_topic_pkey PRIMARY KEY (primary_key);


--
-- Name: lesson_type lesson_type_pkey; Type: CONSTRAINT; Schema: tech_card; Owner: college_user
--

ALTER TABLE ONLY tech_card.lesson_type
    ADD CONSTRAINT lesson_type_pkey PRIMARY KEY (primary_key);


--
-- Name: name_teacher name_teacher_pkey; Type: CONSTRAINT; Schema: tech_card; Owner: college_user
--

ALTER TABLE ONLY tech_card.name_teacher
    ADD CONSTRAINT name_teacher_pkey PRIMARY KEY (primary_key);


--
-- Name: pk_and_ok pk_and_ok_pkey; Type: CONSTRAINT; Schema: tech_card; Owner: college_user
--

ALTER TABLE ONLY tech_card.pk_and_ok
    ADD CONSTRAINT pk_and_ok_pkey PRIMARY KEY (primary_key);


--
-- Name: skills_and_knowledge skills_and_Knowledge_pkey; Type: CONSTRAINT; Schema: tech_card; Owner: college_user
--

ALTER TABLE ONLY tech_card.skills_and_knowledge
    ADD CONSTRAINT "skills_and_Knowledge_pkey" PRIMARY KEY (primary_key);


--
-- PostgreSQL database dump complete
--

\unrestrict 1xPICBYrlfoN8btW6MxPASby2aTYXc5AepE7qpZuHUQwqMzLNx8bbbynR4qi1RW

--
-- PostgreSQL database cluster dump complete
--



-- Added by Antigravity
CREATE DATABASE techcard_db;
