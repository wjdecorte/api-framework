from fastapi import Header


class CommonHeaders:
    def __init__(
        self,
        x_auth_key: str | None = Header(None),  # noqa: B008
        x_tenant_id: str | None = Header(None),  # noqa: B008
    ):
        self.auth_key = x_auth_key
        self.tenant_id = x_tenant_id
