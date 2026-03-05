--
-- PostgreSQL database dump
--

\restrict KNOXpip1gpShdfZbodYtNdTd063rtruk8gfMDNcfBOHFiOQaOOZzFfU0i83Nf5r

-- Dumped from database version 18.3 (Homebrew)
-- Dumped by pg_dump version 18.3 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: skills; Type: TABLE; Schema: public; Owner: skipppotter
--

CREATE TABLE public.skills (
    id text NOT NULL,
    source text DEFAULT 'anthropics/skills'::text NOT NULL,
    source_url text NOT NULL,
    source_path text,
    name text NOT NULL,
    description text,
    body text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    tags text[] DEFAULT '{}'::text[],
    version integer DEFAULT 1,
    status text DEFAULT 'active'::text,
    risk_level smallint DEFAULT 1,
    body_hash text NOT NULL,
    agent_allowlist text[] DEFAULT '{}'::text[],
    execution_count integer DEFAULT 0,
    last_used_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    embedding public.vector(384)
);


ALTER TABLE public.skills OWNER TO skipppotter;

--
-- Name: skills skills_name_key; Type: CONSTRAINT; Schema: public; Owner: skipppotter
--

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_name_key UNIQUE (name);


--
-- Name: skills skills_pkey; Type: CONSTRAINT; Schema: public; Owner: skipppotter
--

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_pkey PRIMARY KEY (id);


--
-- Name: idx_skills_agent_allowlist; Type: INDEX; Schema: public; Owner: skipppotter
--

CREATE INDEX idx_skills_agent_allowlist ON public.skills USING gin (agent_allowlist);


--
-- Name: idx_skills_body_hash; Type: INDEX; Schema: public; Owner: skipppotter
--

CREATE INDEX idx_skills_body_hash ON public.skills USING btree (body_hash);


--
-- Name: idx_skills_embedding; Type: INDEX; Schema: public; Owner: skipppotter
--

CREATE INDEX idx_skills_embedding ON public.skills USING ivfflat (embedding public.vector_cosine_ops) WHERE (embedding IS NOT NULL);


--
-- Name: idx_skills_name; Type: INDEX; Schema: public; Owner: skipppotter
--

CREATE INDEX idx_skills_name ON public.skills USING btree (name);


--
-- Name: idx_skills_status; Type: INDEX; Schema: public; Owner: skipppotter
--

CREATE INDEX idx_skills_status ON public.skills USING btree (status);


--
-- Name: idx_skills_tags; Type: INDEX; Schema: public; Owner: skipppotter
--

CREATE INDEX idx_skills_tags ON public.skills USING gin (tags);


--
-- Name: skills update_skills_updated_at; Type: TRIGGER; Schema: public; Owner: skipppotter
--

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON public.skills FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- PostgreSQL database dump complete
--

\unrestrict KNOXpip1gpShdfZbodYtNdTd063rtruk8gfMDNcfBOHFiOQaOOZzFfU0i83Nf5r

