from __future__ import annotations

import json
from typing import Any

from pro_beta.contracts import (
    AuditReportRecord,
    CFCRun,
    Conversation,
    HAWMSnapshot,
    Message,
    UserAccount,
    Workspace,
)
from pro_beta.persistence import NotFoundError, OwnershipError


class PostgresPersistence:
    """PostgreSQL adapter for the Pro Beta persistence contract.

    The adapter receives an already-open DB-API compatible connection. It does
    not own credentials, create connections, or persist provider API keys.
    """

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def _one(self, sql: str, params: tuple[Any, ...]):
        with self.connection.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

    def _all(self, sql: str, params: tuple[Any, ...]):
        with self.connection.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def _execute(self, sql: str, params: tuple[Any, ...]) -> None:
        with self.connection.cursor() as cur:
            cur.execute(sql, params)
        self.connection.commit()

    def create_user(self, account: UserAccount) -> UserAccount:
        self._execute(
            """
            insert into users (user_id, external_auth_subject, email, created_at)
            values (%s, %s, %s, %s)
            """,
            (
                account.user_id,
                account.external_auth_subject,
                account.email,
                account.created_at,
            ),
        )
        return account

    def get_user(self, user_id: str) -> UserAccount:
        row = self._one(
            """
            select user_id, external_auth_subject, email, created_at::text
            from users where user_id = %s
            """,
            (user_id,),
        )
        if row is None:
            raise NotFoundError("USER_NOT_FOUND")
        return UserAccount(
            user_id=row[0],
            external_auth_subject=row[1],
            email=row[2],
            created_at=row[3],
        )

    def get_user_by_external_auth_subject(
        self, external_auth_subject: str
    ) -> UserAccount:
        row = self._one(
            """
            select user_id, external_auth_subject, email, created_at::text
            from users where external_auth_subject = %s
            """,
            (external_auth_subject,),
        )
        if row is None:
            raise NotFoundError("AUTH_SUBJECT_NOT_FOUND")
        return UserAccount(
            user_id=row[0],
            external_auth_subject=row[1],
            email=row[2],
            created_at=row[3],
        )

    def _workspace_owner(self, workspace_id: str) -> str:
        row = self._one(
            "select user_id from workspaces where workspace_id = %s",
            (workspace_id,),
        )
        if row is None:
            raise NotFoundError("WORKSPACE_NOT_FOUND")
        return row[0]

    def _assert_workspace_owned(self, user_id: str, workspace_id: str) -> None:
        if self._workspace_owner(workspace_id) != user_id:
            raise OwnershipError("WORKSPACE_NOT_OWNED")

    def _conversation_owner(self, conversation_id: str) -> str:
        row = self._one(
            """
            select w.user_id
            from conversations c
            join workspaces w on w.workspace_id = c.workspace_id
            where c.conversation_id = %s
            """,
            (conversation_id,),
        )
        if row is None:
            raise NotFoundError("CONVERSATION_NOT_FOUND")
        return row[0]

    def _assert_conversation_owned(self, user_id: str, conversation_id: str) -> None:
        if self._conversation_owner(conversation_id) != user_id:
            raise OwnershipError("CONVERSATION_NOT_OWNED")

    def create_workspace(self, user_id: str, workspace: Workspace) -> Workspace:
        self.get_user(user_id)
        if workspace.user_id != user_id:
            raise OwnershipError("WORKSPACE_OWNER_MISMATCH")
        self._execute(
            """
            insert into workspaces
                (workspace_id, user_id, name, created_at, updated_at)
            values (%s, %s, %s, %s, %s)
            """,
            (
                workspace.workspace_id,
                workspace.user_id,
                workspace.name,
                workspace.created_at,
                workspace.updated_at,
            ),
        )
        return workspace

    def get_workspace(self, user_id: str, workspace_id: str) -> Workspace:
        self._assert_workspace_owned(user_id, workspace_id)
        row = self._one(
            """
            select workspace_id, user_id, name, created_at::text, updated_at::text
            from workspaces where workspace_id = %s
            """,
            (workspace_id,),
        )
        return Workspace(
            workspace_id=row[0],
            user_id=row[1],
            name=row[2],
            created_at=row[3],
            updated_at=row[4],
        )

    def list_workspaces(self, user_id: str) -> list[Workspace]:
        self.get_user(user_id)
        rows = self._all(
            """
            select workspace_id, user_id, name, created_at::text, updated_at::text
            from workspaces
            where user_id = %s
            order by created_at, workspace_id
            """,
            (user_id,),
        )
        return [
            Workspace(
                workspace_id=r[0],
                user_id=r[1],
                name=r[2],
                created_at=r[3],
                updated_at=r[4],
            )
            for r in rows
        ]

    def create_conversation(
        self, user_id: str, conversation: Conversation
    ) -> Conversation:
        self._assert_workspace_owned(user_id, conversation.workspace_id)
        self._execute(
            """
            insert into conversations
                (conversation_id, workspace_id, title, created_at, updated_at)
            values (%s, %s, %s, %s, %s)
            """,
            (
                conversation.conversation_id,
                conversation.workspace_id,
                conversation.title,
                conversation.created_at,
                conversation.updated_at,
            ),
        )
        return conversation

    def list_conversations(
        self, user_id: str, workspace_id: str
    ) -> list[Conversation]:
        self._assert_workspace_owned(user_id, workspace_id)
        rows = self._all(
            """
            select conversation_id, workspace_id, title,
                   created_at::text, updated_at::text
            from conversations
            where workspace_id = %s
            order by created_at, conversation_id
            """,
            (workspace_id,),
        )
        return [
            Conversation(
                conversation_id=r[0],
                workspace_id=r[1],
                title=r[2],
                created_at=r[3],
                updated_at=r[4],
            )
            for r in rows
        ]

    def get_conversation(
        self, user_id: str, conversation_id: str
    ) -> Conversation:
        self._assert_conversation_owned(user_id, conversation_id)
        row = self._one(
            """
            select conversation_id, workspace_id, title,
                   created_at::text, updated_at::text
            from conversations
            where conversation_id = %s
            """,
            (conversation_id,),
        )
        return Conversation(
            conversation_id=row[0],
            workspace_id=row[1],
            title=row[2],
            created_at=row[3],
            updated_at=row[4],
        )

    def append_message(self, user_id: str, message: Message) -> Message:
        self._assert_conversation_owned(user_id, message.conversation_id)
        self._execute(
            """
            insert into messages
                (message_id, conversation_id, role, content,
                 authority, cfc_status, mode, provider, model, created_at)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                message.message_id,
                message.conversation_id,
                message.role,
                message.content,
                message.authority,
                message.cfc_status,
                message.mode,
                message.provider,
                message.model,
                message.created_at,
            ),
        )
        return message

    def list_messages(self, user_id: str, conversation_id: str) -> list[Message]:
        self._assert_conversation_owned(user_id, conversation_id)
        rows = self._all(
            """
            select message_id, conversation_id, role, content,
                   authority, cfc_status, mode, provider, model, created_at::text
            from messages
            where conversation_id = %s
            order by created_at, message_id
            """,
            (conversation_id,),
        )
        return [
            Message(
                message_id=r[0],
                conversation_id=r[1],
                role=r[2],
                content=r[3],
                authority=r[4],
                cfc_status=r[5],
                mode=r[6],
                provider=r[7],
                model=r[8],
                created_at=r[9],
            )
            for r in rows
        ]

    def add_hawm_snapshot(
        self, user_id: str, snapshot: HAWMSnapshot
    ) -> HAWMSnapshot:
        self._assert_conversation_owned(user_id, snapshot.conversation_id)
        self._execute(
            """
            insert into hawm_snapshots
                (snapshot_id, conversation_id, state,
                 last_verified_state, created_at)
            values (%s, %s, %s::jsonb, %s, %s)
            """,
            (
                snapshot.snapshot_id,
                snapshot.conversation_id,
                json.dumps(snapshot.state, ensure_ascii=False),
                snapshot.last_verified_state,
                snapshot.created_at,
            ),
        )
        return snapshot

    def list_hawm_snapshots(
        self, user_id: str, conversation_id: str
    ) -> list[HAWMSnapshot]:
        self._assert_conversation_owned(user_id, conversation_id)
        rows = self._all(
            """
            select snapshot_id, conversation_id, state,
                   last_verified_state, created_at::text
            from hawm_snapshots
            where conversation_id = %s
            order by created_at, snapshot_id
            """,
            (conversation_id,),
        )
        return [
            HAWMSnapshot(
                snapshot_id=r[0],
                conversation_id=r[1],
                state=r[2],
                last_verified_state=r[3],
                created_at=r[4],
            )
            for r in rows
        ]

    def list_cfc_runs(
        self, user_id: str, conversation_id: str
    ) -> list[CFCRun]:
        self._assert_conversation_owned(user_id, conversation_id)
        rows = self._all(
            """
            select run_id, conversation_id, case_id, controller_anchor,
                   controller_result, presentation,
                   replay_matches_reference, created_at::text
            from cfc_runs
            where conversation_id = %s
            order by created_at, run_id
            """,
            (conversation_id,),
        )
        return [
            CFCRun(
                run_id=r[0],
                conversation_id=r[1],
                case_id=r[2],
                controller_anchor=r[3],
                controller_result=r[4],
                presentation=r[5],
                replay_matches_reference=r[6],
                created_at=r[7],
            )
            for r in rows
        ]

    def add_cfc_run(self, user_id: str, run: CFCRun) -> CFCRun:
        self._assert_conversation_owned(user_id, run.conversation_id)
        self._execute(
            """
            insert into cfc_runs
                (run_id, conversation_id, case_id, controller_anchor,
                 controller_result, presentation, replay_matches_reference,
                 created_at)
            values (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s)
            """,
            (
                run.run_id,
                run.conversation_id,
                run.case_id,
                run.controller_anchor,
                json.dumps(run.controller_result, ensure_ascii=False),
                json.dumps(run.presentation, ensure_ascii=False),
                run.replay_matches_reference,
                run.created_at,
            ),
        )
        return run


    def add_audit_report(
        self, user_id: str, report: AuditReportRecord
    ) -> AuditReportRecord:
        self._assert_conversation_owned(user_id, report.conversation_id)
        if report.cfc_run_id is not None:
            row = self._one(
                "select conversation_id from cfc_runs where run_id = %s",
                (report.cfc_run_id,),
            )
            if row is None:
                raise NotFoundError("CFC_RUN_NOT_FOUND")
            if row[0] != report.conversation_id:
                raise OwnershipError("CFC_RUN_CONVERSATION_MISMATCH")
        self._execute(
            """
            insert into audit_reports
                (report_id, conversation_id, cfc_run_id, status,
                 artifact_path, created_at)
            values (%s, %s, %s, %s, %s, %s)
            """,
            (
                report.report_id,
                report.conversation_id,
                report.cfc_run_id,
                report.status,
                report.artifact_path,
                report.created_at,
            ),
        )
        return report
