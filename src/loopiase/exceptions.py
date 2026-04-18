class LoopiaError(Exception):
    """Raised when the Loopia API returns a non-OK status."""

    def __init__(self, status: str) -> None:
        self.status = status
        super().__init__(status)
