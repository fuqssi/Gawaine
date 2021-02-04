--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2
-- Dumped by pg_dump version 12.2

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
    fund_manager character varying(100),
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
-- Name: view_rate_of_return_by_15days; Type: VIEW; Schema: public; Owner: yanxl
--

CREATE VIEW public.view_rate_of_return_by_15days AS
 WITH summary AS (
         SELECT current.net_worth_date,
            info.name,
            current.code,
            current.cumulative_net_worth AS current,
            historical.cumulative_net_worth AS historical,
            round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2) AS percent
           FROM ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 1)) current,
            ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 60)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 15)) historical,
            ( SELECT tb_fund_name.code,
                    tb_fund_name.name
                   FROM public.tb_fund_name) info
          WHERE (((current.code)::text = (historical.code)::text) AND ((info.code)::text = (current.code)::text))
          ORDER BY (round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2)) DESC
        )
 SELECT row_number() OVER (ORDER BY s.percent DESC) AS rank,
    s.net_worth_date,
    s.name,
    s.code,
    s.current,
    s.historical,
    s.percent
   FROM summary s;


ALTER TABLE public.view_rate_of_return_by_15days OWNER TO yanxl;

--
-- Name: view_rate_of_return_by_180days; Type: VIEW; Schema: public; Owner: yanxl
--

CREATE VIEW public.view_rate_of_return_by_180days AS
 WITH summary AS (
         SELECT current.net_worth_date,
            info.name,
            current.code,
            current.cumulative_net_worth AS current,
            historical.cumulative_net_worth AS historical,
            round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2) AS percent
           FROM ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 1)) current,
            ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 400)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 180)) historical,
            ( SELECT tb_fund_name.code,
                    tb_fund_name.name
                   FROM public.tb_fund_name) info
          WHERE (((current.code)::text = (historical.code)::text) AND ((info.code)::text = (current.code)::text))
          ORDER BY (round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2)) DESC
        )
 SELECT row_number() OVER (ORDER BY s.percent DESC) AS rank,
    s.net_worth_date,
    s.name,
    s.code,
    s.current,
    s.historical,
    s.percent
   FROM summary s;


ALTER TABLE public.view_rate_of_return_by_180days OWNER TO yanxl;

--
-- Name: view_rate_of_return_by_1day; Type: VIEW; Schema: public; Owner: yanxl
--

CREATE VIEW public.view_rate_of_return_by_1day AS
 WITH summary AS (
         SELECT current.net_worth_date,
            info.name,
            current.code,
            current.cumulative_net_worth AS current,
            historical.cumulative_net_worth AS historical,
            round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2) AS percent
           FROM ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 1)) current,
            ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 2)) historical,
            ( SELECT tb_fund_name.code,
                    tb_fund_name.name
                   FROM public.tb_fund_name) info
          WHERE (((current.code)::text = (historical.code)::text) AND ((info.code)::text = (current.code)::text))
          ORDER BY (round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2)) DESC
        )
 SELECT row_number() OVER (ORDER BY s.percent DESC) AS rank,
    s.net_worth_date,
    s.name,
    s.code,
    s.current,
    s.historical,
    s.percent
   FROM summary s;


ALTER TABLE public.view_rate_of_return_by_1day OWNER TO yanxl;

--
-- Name: view_rate_of_return_by_30days; Type: VIEW; Schema: public; Owner: yanxl
--

CREATE VIEW public.view_rate_of_return_by_30days AS
 WITH summary AS (
         SELECT current.net_worth_date,
            info.name,
            current.code,
            current.cumulative_net_worth AS current,
            historical.cumulative_net_worth AS historical,
            round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2) AS percent
           FROM ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 1)) current,
            ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 60)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 30)) historical,
            ( SELECT tb_fund_name.code,
                    tb_fund_name.name
                   FROM public.tb_fund_name) info
          WHERE (((current.code)::text = (historical.code)::text) AND ((info.code)::text = (current.code)::text))
          ORDER BY (round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2)) DESC
        )
 SELECT row_number() OVER (ORDER BY s.percent DESC) AS rank,
    s.net_worth_date,
    s.name,
    s.code,
    s.current,
    s.historical,
    s.percent
   FROM summary s;


ALTER TABLE public.view_rate_of_return_by_30days OWNER TO yanxl;

--
-- Name: view_rate_of_return_by_365days; Type: VIEW; Schema: public; Owner: yanxl
--

CREATE VIEW public.view_rate_of_return_by_365days AS
 WITH summary AS (
         SELECT current.net_worth_date,
            info.name,
            current.code,
            current.cumulative_net_worth AS current,
            historical.cumulative_net_worth AS historical,
            round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2) AS percent
           FROM ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 1)) current,
            ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 400)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 365)) historical,
            ( SELECT tb_fund_name.code,
                    tb_fund_name.name
                   FROM public.tb_fund_name) info
          WHERE (((current.code)::text = (historical.code)::text) AND ((info.code)::text = (current.code)::text))
          ORDER BY (round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2)) DESC
        )
 SELECT row_number() OVER (ORDER BY s.percent DESC) AS rank,
    s.net_worth_date,
    s.name,
    s.code,
    s.current,
    s.historical,
    s.percent
   FROM summary s;


ALTER TABLE public.view_rate_of_return_by_365days OWNER TO yanxl;

--
-- Name: view_rate_of_return_by_3days; Type: VIEW; Schema: public; Owner: yanxl
--

CREATE VIEW public.view_rate_of_return_by_3days AS
 WITH summary AS (
         SELECT current.net_worth_date,
            info.name,
            current.code,
            current.cumulative_net_worth AS current,
            historical.cumulative_net_worth AS historical,
            round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2) AS percent
           FROM ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 1)) current,
            ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 3)) historical,
            ( SELECT tb_fund_name.code,
                    tb_fund_name.name
                   FROM public.tb_fund_name) info
          WHERE (((current.code)::text = (historical.code)::text) AND ((info.code)::text = (current.code)::text))
          ORDER BY (round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2)) DESC
        )
 SELECT row_number() OVER (ORDER BY s.percent DESC) AS rank,
    s.net_worth_date,
    s.name,
    s.code,
    s.current,
    s.historical,
    s.percent
   FROM summary s;


ALTER TABLE public.view_rate_of_return_by_3days OWNER TO yanxl;

--
-- Name: view_rate_of_return_by_7days; Type: VIEW; Schema: public; Owner: yanxl
--

CREATE VIEW public.view_rate_of_return_by_7days AS
 WITH summary AS (
         SELECT current.net_worth_date,
            info.name,
            current.code,
            current.cumulative_net_worth AS current,
            historical.cumulative_net_worth AS historical,
            round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2) AS percent
           FROM ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 1)) current,
            ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 7)) historical,
            ( SELECT tb_fund_name.code,
                    tb_fund_name.name
                   FROM public.tb_fund_name) info
          WHERE (((current.code)::text = (historical.code)::text) AND ((info.code)::text = (current.code)::text))
          ORDER BY (round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2)) DESC
        )
 SELECT row_number() OVER (ORDER BY s.percent DESC) AS rank,
    s.net_worth_date,
    s.name,
    s.code,
    s.current,
    s.historical,
    s.percent
   FROM summary s;


ALTER TABLE public.view_rate_of_return_by_7days OWNER TO yanxl;

--
-- Name: view_rate_of_return_by_90days; Type: VIEW; Schema: public; Owner: yanxl
--

CREATE VIEW public.view_rate_of_return_by_90days AS
 WITH summary AS (
         SELECT current.net_worth_date,
            info.name,
            current.code,
            current.cumulative_net_worth AS current,
            historical.cumulative_net_worth AS historical,
            round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2) AS percent
           FROM ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 15)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 1)) current,
            ( SELECT t.id,
                    t.net_worth_date,
                    t.code,
                    t.net_worth,
                    t.cumulative_net_worth,
                    t.rk
                   FROM ( SELECT tb_fund_net_worth.id,
                            tb_fund_net_worth.net_worth_date,
                            tb_fund_net_worth.code,
                            tb_fund_net_worth.net_worth,
                            tb_fund_net_worth.cumulative_net_worth,
                            row_number() OVER (PARTITION BY tb_fund_net_worth.code ORDER BY tb_fund_net_worth.net_worth_date DESC) AS rk
                           FROM public.tb_fund_net_worth
                          WHERE ((tb_fund_net_worth.net_worth_date >= (CURRENT_DATE - 180)) AND (tb_fund_net_worth.net_worth_date <= CURRENT_DATE))) t
                  WHERE (t.rk = 90)) historical,
            ( SELECT tb_fund_name.code,
                    tb_fund_name.name
                   FROM public.tb_fund_name) info
          WHERE (((current.code)::text = (historical.code)::text) AND ((info.code)::text = (current.code)::text))
          ORDER BY (round(((((current.cumulative_net_worth - historical.cumulative_net_worth) / historical.cumulative_net_worth) * (100)::double precision))::numeric, 2)) DESC
        )
 SELECT row_number() OVER (ORDER BY s.percent DESC) AS rank,
    s.net_worth_date,
    s.name,
    s.code,
    s.current,
    s.historical,
    s.percent
   FROM summary s;


ALTER TABLE public.view_rate_of_return_by_90days OWNER TO yanxl;

--
-- Name: tb_fund_net_worth id; Type: DEFAULT; Schema: public; Owner: yanxl
--

ALTER TABLE ONLY public.tb_fund_net_worth ALTER COLUMN id SET DEFAULT nextval('public.tb_fund_net_worth_id_seq'::regclass);


--
-- Name: tb_fund_net_worth cons_uniq_date_code; Type: CONSTRAINT; Schema: public; Owner: yanxl
--

ALTER TABLE ONLY public.tb_fund_net_worth
    ADD CONSTRAINT cons_uniq_date_code UNIQUE (net_worth_date, code);


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
-- Name: indx_tb_fund_name_code; Type: INDEX; Schema: public; Owner: yanxl
--

CREATE INDEX indx_tb_fund_name_code ON public.tb_fund_name USING btree (code);


--
-- Name: indx_tb_fund_name_lastdate; Type: INDEX; Schema: public; Owner: yanxl
--

CREATE INDEX indx_tb_fund_name_lastdate ON public.tb_fund_name USING btree (last_update);


--
-- Name: indx_tb_fund_net_worth_date_code; Type: INDEX; Schema: public; Owner: yanxl
--

CREATE INDEX indx_tb_fund_net_worth_date_code ON public.tb_fund_net_worth USING btree (net_worth_date, code);


--
-- PostgreSQL database dump complete
--

