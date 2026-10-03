"""Upgrade test in an ISOLATED database simulating pre-binding Pro Beta rows.

Never touches the production DB. Uses CI's dedicated PostgreSQL fixture only.
"""
from __future__ import annotations

import os
import unittest
from uuid import uuid4

from pro_beta.db_bootstrap import ensure_schema

try:
    import psycopg
    from psycopg import sql
    from psycopg.conninfo import make_conninfo
except ImportError:
    psycopg = None

LEGACY_MINIMAL_SCHEMA = """
create table users (
 user_id text primary key,
 external_auth_subject text not null unique,
 email text,
 created_at timestamptz not null default now()
);
create table workspaces (
 workspace_id text primary key,
 user_id text not null references users(user_id) on delete cascade,
 name text not null,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
create table conversations (
 conversation_id text primary key,
 workspace_id text not null references workspaces(workspace_id) on delete cascade,
 title text not null,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
create table hawm_snapshots (
 snapshot_id text primary key,
 conversation_id text not null references conversations(conversation_id) on delete cascade,
 state jsonb not null,
 last_verified_state text not null,
 created_at timestamptz not null default now()
);
create table cfc_runs (
 run_id text primary key,
 conversation_id text not null references conversations(conversation_id) on delete cascade,
 case_id text not null,
 controller_anchor text not null,
 controller_result jsonb not null,
 presentation jsonb not null,
 replay_matches_reference boolean,
 created_at timestamptz not null default now()
);
insert into users(user_id, external_auth_subject) values ('usr_legacy', 'legacy|owner');
insert into workspaces(workspace_id,user_id,name) values ('ws_legacy','usr_legacy','Old workspace');
insert into conversations(conversation_id,workspace_id,title) values
 ('conv_legacy','ws_legacy','Old conversation');
insert into hawm_snapshots(snapshot_id,conversation_id,state,last_verified_state)
 values ('hawm_legacy','conv_legacy','{"goal":"old state"}'::jsonb,'USER_WORKING_STATE');
insert into cfc_runs(run_id,conversation_id,case_id,controller_anchor,controller_result,presentation)
 values ('cfc_legacy','conv_legacy','HAWM_STRUCTURED_CUSTOM','0.2.90rc1',
 '{"control_closure":false}'::jsonb,'{"decision":"STOP"}'::jsonb);
"""


@unittest.skipIf(psycopg is None, "psycopg unavailable")
class LegacyBindingUpgradeTests(unittest.TestCase):
    def test_old_rows_survive_idempotent_nullable_migration_without_fake_link(self):
        base = os.environ.get("PRO_BETA_TEST_DATABASE_URL")
        if not base:
            self.skipTest("PRO_BETA_TEST_DATABASE_URL not configured")
        name = "cfc_binding_" + uuid4().hex[:16]
        isolated = make_conninfo(base, dbname=name)
        # CI's Postgres test user creates this disposable database; never
        # recreate, truncate or alter the shared DB supplied in the DSN.
        with psycopg.connect(base, autocommit=True) as admin:
            try:
                with admin.cursor() as cur:
                    cur.execute(
                        sql.SQL("create database {}").format(sql.Identifier(name))
                    )
                with psycopg.connect(isolated) as connection:
                    with connection.cursor() as cur:
                        cur.execute(LEGACY_MINIMAL_SCHEMA)
                    connection.commit()
                ensure_schema(isolated)
                ensure_schema(isolated)
                with psycopg.connect(isolated) as connection:
                    with connection.cursor() as cur:
                        cur.execute(
                            """
                            select hawm_snapshot_id, presentation->>'decision'
                            from cfc_runs where run_id='cfc_legacy'
                            """
                        )
                        self.assertEqual(cur.fetchone(), (None, "STOP"))
                        cur.execute(
                            """
                            select count(*) from pg_constraint
                            where conname='fk_cfc_run_owned_hawm_snapshot'
                              and conrelid='cfc_runs'::regclass
                            """
                        )
                        self.assertEqual(cur.fetchone()[0], 1)
                        cur.execute(
                            """
                            insert into cfc_runs
                            (run_id,conversation_id,case_id,controller_anchor,
                             controller_result,presentation,hawm_snapshot_id)
                            values ('cfc_new','conv_legacy','HAWM_STRUCTURED_CUSTOM',
                              '0.2.90rc1','{}'::jsonb,'{"decision":"STOP"}'::jsonb,
                              'hawm_legacy')
                            """
                        )
                    connection.commit()
                    with connection.cursor() as cur:
                        cur.execute(
                            "select hawm_snapshot_id from cfc_runs where run_id='cfc_new'"
                        )
                        self.assertEqual(cur.fetchone()[0], "hawm_legacy")
            finally:
                with admin.cursor() as cur:
                    cur.execute(
                        sql.SQL("drop database if exists {} with (force)").format(
                            sql.Identifier(name)
                        )
                    )


if __name__ == "__main__":
    unittest.main()
