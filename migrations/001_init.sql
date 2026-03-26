create table if not exists repo_policies (
    id bigserial primary key,
    repo_full_name text not null unique,
    allowed_org text not null,
    default_base_branch text not null default 'main',
    writes_enabled boolean not null default false,
    prs_enabled boolean not null default false,
    created_at timestamptz not null default now()
);

create table if not exists tool_audit_log (
    id bigserial primary key,
    tool_name text not null,
    repo_full_name text,
    actor text,
    request_payload jsonb not null default '{}'::jsonb,
    response_payload jsonb,
    status text not null,
    error_message text,
    created_at timestamptz not null default now()
);

create table if not exists idempotency_keys (
    id bigserial primary key,
    key text not null unique,
    tool_name text not null,
    created_at timestamptz not null default now()
);