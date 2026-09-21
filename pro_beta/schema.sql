-- CFC + HAWM Pro Beta v0.1
-- PostgreSQL-oriented persistence contract.
-- This file is not deployed by Web Alpha.

create table if not exists users (
  user_id text primary key,
  external_auth_subject text not null unique,
  email text,
  created_at timestamptz not null default now()
);

create table if not exists workspaces (
  workspace_id text primary key,
  user_id text not null references users(user_id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists conversations (
  conversation_id text primary key,
  workspace_id text not null references workspaces(workspace_id) on delete cascade,
  title text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists messages (
  message_id text primary key,
  conversation_id text not null references conversations(conversation_id) on delete cascade,
  role text not null check (role in ('user','assistant','system')),
  content text not null,
  authority text not null,
  cfc_status text not null,
  mode text not null,
  created_at timestamptz not null default now()
);

alter table messages add column if not exists provider text;
alter table messages add column if not exists model text;

create table if not exists hawm_snapshots (
  snapshot_id text primary key,
  conversation_id text not null references conversations(conversation_id) on delete cascade,
  state jsonb not null,
  last_verified_state text not null,
  created_at timestamptz not null default now()
);

create table if not exists cfc_runs (
  run_id text primary key,
  conversation_id text not null references conversations(conversation_id) on delete cascade,
  case_id text not null,
  controller_anchor text not null,
  controller_result jsonb not null,
  presentation jsonb not null,
  replay_matches_reference boolean,
  created_at timestamptz not null default now()
);

create table if not exists audit_reports (
  report_id text primary key,
  conversation_id text not null references conversations(conversation_id) on delete cascade,
  cfc_run_id text references cfc_runs(run_id) on delete set null,
  status text not null,
  artifact_path text,
  created_at timestamptz not null default now()
);

create table if not exists usage_events (
  event_id text primary key,
  user_id text not null references users(user_id) on delete cascade,
  event_type text not null,
  units integer not null default 1 check (units >= 0),
  created_at timestamptz not null default now()
);

create index if not exists idx_workspaces_user on workspaces(user_id);
create index if not exists idx_conversations_workspace on conversations(workspace_id);
create index if not exists idx_messages_conversation_created on messages(conversation_id, created_at);
create index if not exists idx_hawm_conversation_created on hawm_snapshots(conversation_id, created_at);
create index if not exists idx_cfc_runs_conversation_created on cfc_runs(conversation_id, created_at);
create index if not exists idx_usage_user_created on usage_events(user_id, created_at);

-- Intentionally absent: passwords, password hashes, provider API keys, access tokens.
