--
-- PostgreSQL database dump
--

-- Dumped from database version 12.1
-- Dumped by pg_dump version 12.1

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: tb_fund_name; Type: TABLE; Schema: public; Owner: yanxl
--

CREATE TABLE public.tb_fund_name (
    code character varying(6) NOT NULL,
    name character varying(50) NOT NULL,
    fund_manager character varying(20),
    last_update date
);


ALTER TABLE public.tb_fund_name OWNER TO yanxl;

--
-- Name: tb_fund_net_worth; Type: TABLE; Schema: public; Owner: yanxl
--

CREATE TABLE public.tb_fund_net_worth (
    id integer NOT NULL,
    net_worth_date date,
    code character varying(6) NOT NULL,
    net_worth real,
    cumulative_net_worth real
);


ALTER TABLE public.tb_fund_net_worth OWNER TO yanxl;

--
-- Name: tb_fund_net_worth_id_seq; Type: SEQUENCE; Schema: public; Owner: yanxl
--

CREATE SEQUENCE public.tb_fund_net_worth_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tb_fund_net_worth_id_seq OWNER TO yanxl;

--
-- Name: tb_fund_net_worth_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yanxl
--

ALTER SEQUENCE public.tb_fund_net_worth_id_seq OWNED BY public.tb_fund_net_worth.id;


--
-- Name: tb_fund_net_worth id; Type: DEFAULT; Schema: public; Owner: yanxl
--

ALTER TABLE ONLY public.tb_fund_net_worth ALTER COLUMN id SET DEFAULT nextval('public.tb_fund_net_worth_id_seq'::regclass);


--
-- Name: tb_fund_name tb_fund_name_pkey; Type: CONSTRAINT; Schema: public; Owner: yanxl
--

ALTER TABLE ONLY public.tb_fund_name
    ADD CONSTRAINT tb_fund_name_pkey PRIMARY KEY (code);


--
-- Name: tb_fund_net_worth tb_fund_net_worth_pkey; Type: CONSTRAINT; Schema: public; Owner: yanxl
--

ALTER TABLE ONLY public.tb_fund_net_worth
    ADD CONSTRAINT tb_fund_net_worth_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

