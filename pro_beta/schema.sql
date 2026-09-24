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

create table if not exists benchmark_runs (
  benchmark_run_id text primary key,
  conversation_id text not null references conversations(conversation_id) on delete cascade,
  benchmark_version text not null,
  case_id text not null,
  benchmark_type text not null,
  context_boundary text not null,
  expected_control_state text not null,
  invariant text not null,
  mode text not null,
  status text not null,
  results jsonb not null,
  failed_providers jsonb not null,
  authority text not null,
  cfc_status text not null,
  automatic_semantic_scoring boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists benchmark_manual_labels (
  label_id text primary key,
  benchmark_run_id text not null references benchmark_runs(benchmark_run_id) on delete cascade,
  provider text not null,
  model text not null,
  label text not null check (label in ('CONSISTENT','AMBIGUOUS','PREMATURE_CLOSURE')),
  note text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (benchmark_run_id, provider)
);

create table if not exists founding_beta_measurements (
  measurement_id text primary key,
  workspace_id text not null references workspaces(workspace_id) on delete cascade,
  system_version text not null,
  workflow_type text not null,
  case_id text not null,
  cfc_result text not null check (cfc_result in ('ALLOW','STOP','UNRESOLVED')),
  reason_code text not null,
  hawm_state text not null,
  human_assessment text not null check (human_assessment in ('AGREE','DISAGREE','UNSURE')),
  final_action text not null,
  problem_type text not null check (
    problem_type in ('NONE','BUG','USABILITY','FALSE_STOP','FALSE_ALLOW','UPSTREAM_STATE_ISSUE')
  ),
  comment text,
  created_at timestamptz not null default now()
);

create table if not exists founding_beta_retention_reports (
  report_id text primary key,
  retention_days integer not null check (retention_days > 0),
  cutoff_at timestamptz not null,
  source_record_count integer not null check (source_record_count > 0),
  summary jsonb not null,
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
create index if not exists idx_benchmark_runs_conversation_created on benchmark_runs(conversation_id, created_at);
create index if not exists idx_benchmark_runs_case_created on benchmark_runs(case_id, created_at);
create index if not exists idx_benchmark_labels_run on benchmark_manual_labels(benchmark_run_id);
create index if not exists idx_benchmark_labels_label on benchmark_manual_labels(label);
create index if not exists idx_founding_beta_measurements_workspace_created on founding_beta_measurements(workspace_id, created_at);
create index if not exists idx_founding_beta_measurements_created on founding_beta_measurements(created_at);
create index if not exists idx_founding_beta_retention_reports_created on founding_beta_retention_reports(created_at);
create index if not exists idx_usage_user_created on usage_events(user_id, created_at);

-- Intentionally absent: passwords, password hashes, provider API keys, access tokens.
