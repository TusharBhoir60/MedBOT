from contextvars import ContextVar

# ContextVar storing the unique correlation ID for the active async execution chain
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

def get_correlation_id() -> str:
    """Retrieve the current request correlation ID."""
    return correlation_id_ctx.get()

def set_correlation_id(correlation_id: str) -> None:
    """Set the request correlation ID in context."""
    correlation_id_ctx.set(correlation_id)
