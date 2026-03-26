from typing import Any

from github_dev_mcp.db import get_db


class AuditService:
    def log(
        self,
        tool_name: str,
        repo_full_name: str | None,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any] | None,
        status: str,
        error_message: str | None = None,
        actor: str | None = "local-user",
    ) -> None:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into tool_audit_log
                    (tool_name, repo_full_name, actor, request_payload, response_payload, status, error_message)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        tool_name,
                        repo_full_name,
                        actor,
                        request_payload,
                        response_payload,
                        status,
                        error_message,
                    ),
                )
            conn.commit()