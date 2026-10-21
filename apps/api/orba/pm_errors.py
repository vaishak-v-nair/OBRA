"""Public PM failure envelopes never include raw provider errors or credentials."""


class PMError(Exception):
    def __init__(
        self,
        status,
        code,
        message,
        *,
        run_id=None,
        diagnostic_id=None,
        details=None,
        retry_after=None,
    ):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message
        self.run_id, self.diagnostic_id = run_id, diagnostic_id
        self.details, self.retry_after = details or [], retry_after

    def body(self):
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "run_id": str(self.run_id) if self.run_id else None,
                "diagnostic_id": str(self.diagnostic_id) if self.diagnostic_id else None,
                "details": self.details,
                "docs": "#pm-setup",
            }
        }


def validation_details(exc):
    if hasattr(exc, "errors"):
        return [
            {
                "field": ".".join(map(str, error["loc"])),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors(include_input=False, include_context=False)[:20]
        ]
    return [{"field": "document", "message": str(exc), "type": "value_error"}]
