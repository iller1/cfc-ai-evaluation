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

-- Historical runs remain NULL/unbound. Never backfill by matching timestamps.
alter table cfc_runs add column if not exists hawm_snapshot_id text;

-- Composite key prevents a run in conversation X from referencing a snapshot
-- in conversation Y, including direct database writes (PostgreSQL >= 15).
create unique index if not exists uq_hawm_snapshot_conversation
  on hawm_snapshots(snapshot_id, conversation_id);

-- Identity anchors are created only for snapshots saved after this contract
-- exists. Historical snapshots are intentionally not backfilled.
create table if not exists hawm_snapshot_identities (
  snapshot_id text primary key,
  conversation_id text not null,
  case_id text not null,
  arm_id text not null,
  state_id text not null,
  lineage_id text not null,
  previous_state_id text,
  registered_snapshot_fingerprint text not null
    check (registered_snapshot_fingerprint ~ '^[0-9a-f]{64}$'),
  adapter_version text not null,
  created_at timestamptz not null default now(),
  constraint fk_hawm_identity_snapshot
    foreign key (snapshot_id, conversation_id)
    references hawm_snapshots(snapshot_id, conversation_id)
    on delete cascade,
  constraint fk_hawm_identity_predecessor
    foreign key (previous_state_id, conversation_id)
    references hawm_snapshots(snapshot_id, conversation_id)
);

create unique index if not exists uq_hawm_identity_snapshot_conversation
  on hawm_snapshot_identities(snapshot_id, conversation_id);

create unique index if not exists uq_cfc_run_conversation
  on cfc_runs(run_id, conversation_id);

create unique index if not exists uq_cfc_run_conversation_snapshot
  on cfc_runs(run_id, conversation_id, hawm_snapshot_id);

-- Evidence/Provenance Layer B registrations are explicit and state-bound.
-- Historical snapshots are intentionally not backfilled.
create table if not exists evidence_set_registrations (
  registration_id text primary key,
  snapshot_id text not null unique,
  conversation_id text not null,
  state_id text not null,
  evidence_set jsonb not null
    check (jsonb_typeof(evidence_set) = 'array'),
  missing_evidence jsonb not null
    check (jsonb_typeof(missing_evidence) = 'array'),
  adapter_version text not null,
  created_at timestamptz not null default now(),
  check (state_id = snapshot_id),
  constraint fk_evidence_registration_identity
    foreign key (snapshot_id, conversation_id)
    references hawm_snapshot_identities(snapshot_id, conversation_id)
    on delete cascade
);

create unique index if not exists uq_evidence_registration_snapshot_conversation
  on evidence_set_registrations(snapshot_id, conversation_id);

create table if not exists evidence_provenance_receipts (
  receipt_id text primary key,
  snapshot_id text not null,
  conversation_id text not null,
  state_id text not null,
  evidence_id text not null,
  source_id text not null,
  status text not null
    check (status in ('ESTABLISHED','PARTIAL','UNKNOWN','INVALID')),
  adapter_version text not null,
  created_at timestamptz not null default now(),
  check (state_id = snapshot_id),
  constraint fk_evidence_provenance_registration
    foreign key (snapshot_id, conversation_id)
    references evidence_set_registrations(snapshot_id, conversation_id)
    on delete cascade,
  unique (snapshot_id, evidence_id)
);

create table if not exists evidence_dependency_receipts (
  receipt_id text primary key,
  snapshot_id text not null unique,
  conversation_id text not null,
  state_id text not null,
  evidence_ids jsonb not null
    check (jsonb_typeof(evidence_ids) = 'array'),
  failure_domains jsonb not null
    check (jsonb_typeof(failure_domains) = 'object'),
  status text not null
    check (status in ('RESOLVED','PARTIAL','UNKNOWN','CONFLICTING')),
  adapter_version text not null,
  created_at timestamptz not null default now(),
  check (state_id = snapshot_id),
  constraint fk_evidence_dependency_registration
    foreign key (snapshot_id, conversation_id)
    references evidence_set_registrations(snapshot_id, conversation_id)
    on delete cascade
);

-- Execution Gate host integration. Intent records identify one exact
-- action/run/state/version tuple but do not establish execution authority.
create table if not exists execution_intents (
  intent_id text primary key,
  conversation_id text not null,
  action_id text not null,
  controller_run_id text not null,
  state_id text not null,
  state_version text not null
    check (state_version ~ '^[0-9a-f]{64}$'),
  idempotency_key text not null,
  receipt_id text not null unique,
  action_payload_fingerprint text not null
    check (action_payload_fingerprint ~ '^[0-9a-f]{64}$'),
  human_review_required boolean not null,
  transaction_required boolean not null,
  adapter_version text not null,
  created_at timestamptz not null default now(),
  constraint fk_execution_intent_run_state
    foreign key (controller_run_id, conversation_id, state_id)
    references cfc_runs(run_id, conversation_id, hawm_snapshot_id)
    on delete cascade,
  constraint fk_execution_intent_state
    foreign key (state_id, conversation_id)
    references hawm_snapshot_identities(snapshot_id, conversation_id)
    on delete cascade,
  unique (conversation_id, idempotency_key)
);

create unique index if not exists uq_execution_intent_conversation
  on execution_intents(intent_id, conversation_id);

create unique index if not exists uq_execution_intent_exact_binding
  on execution_intents(
    intent_id, conversation_id, action_id, controller_run_id,
    state_id, state_version, idempotency_key, receipt_id
  );

-- Append-only final records for attempts that actually reached an executor.
-- Preflight-only BLOCKED / NOT_ATTEMPTED states are intentionally not stored
-- here as execution receipts.
create table if not exists execution_receipts (
  receipt_id text primary key,
  intent_id text not null unique,
  conversation_id text not null,
  action_id text not null,
  controller_run_id text not null,
  state_id text not null,
  state_version text not null
    check (state_version ~ '^[0-9a-f]{64}$'),
  idempotency_key text not null,
  execution_status text not null
    check (execution_status in (
      'ATTEMPTED_NOT_EXECUTED',
      'EXECUTED',
      'OUTCOME_UNKNOWN',
      'FAILED'
    )),
  attempted boolean not null check (attempted = true),
  executed boolean,
  effect_handle text,
  adapter_version text not null,
  created_at timestamptz not null default now(),
  constraint fk_execution_receipt_exact_intent
    foreign key (
      intent_id, conversation_id, action_id, controller_run_id,
      state_id, state_version, idempotency_key, receipt_id
    )
    references execution_intents(
      intent_id, conversation_id, action_id, controller_run_id,
      state_id, state_version, idempotency_key, receipt_id
    )
    on delete cascade,
  check (
    (execution_status = 'EXECUTED'
      and executed = true
      and effect_handle is not null
      and length(effect_handle) > 0)
    or
    (execution_status in ('ATTEMPTED_NOT_EXECUTED','FAILED')
      and executed = false
      and effect_handle is null)
    or
    (execution_status = 'OUTCOME_UNKNOWN'
      and executed is null)
  )
);

create index if not exists idx_execution_intents_conversation_created
  on execution_intents(conversation_id, created_at);
create index if not exists idx_execution_receipts_conversation_created
  on execution_receipts(conversation_id, created_at);

do $binding$
begin
  if not exists (
    select 1 from pg_catalog.pg_constraint
    where conname = 'fk_cfc_run_owned_hawm_snapshot'
      and conrelid = 'cfc_runs'::regclass
  ) then
    alter table cfc_runs add constraint fk_cfc_run_owned_hawm_snapshot
      foreign key (hawm_snapshot_id, conversation_id)
      references hawm_snapshots(snapshot_id, conversation_id)
      on delete set null (hawm_snapshot_id);
  end if;
end
$binding$;

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
create index if not exists idx_evidence_provenance_snapshot
  on evidence_provenance_receipts(snapshot_id, created_at);
create index if not exists idx_evidence_dependency_snapshot
  on evidence_dependency_receipts(snapshot_id, created_at);
create index if not exists idx_benchmark_runs_conversation_created on benchmark_runs(conversation_id, created_at);
create index if not exists idx_benchmark_runs_case_created on benchmark_runs(case_id, created_at);
create index if not exists idx_benchmark_labels_run on benchmark_manual_labels(benchmark_run_id);
create index if not exists idx_benchmark_labels_label on benchmark_manual_labels(label);
create index if not exists idx_founding_beta_measurements_workspace_created on founding_beta_measurements(workspace_id, created_at);
create index if not exists idx_founding_beta_measurements_created on founding_beta_measurements(created_at);
create index if not exists idx_founding_beta_retention_reports_created on founding_beta_retention_reports(created_at);
create index if not exists idx_usage_user_created on usage_events(user_id, created_at);

-- Intentionally absent: passwords, password hashes, provider API keys, access tokens.
