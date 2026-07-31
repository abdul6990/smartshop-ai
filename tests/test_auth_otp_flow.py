"""Auth OTP flow tests for schema-compatible fallback behavior."""

import importlib


def test_request_otp_uses_memory_fallback_when_db_schema_missing(monkeypatch):
    auth = importlib.import_module("utils.auth")

    class _BrokenTable:
        def select(self, *_args, **_kwargs):
            return self

        def eq(self, *_args, **_kwargs):
            return self

        def limit(self, *_args, **_kwargs):
            return self

        def upsert(self, *_args, **_kwargs):
            raise Exception("PGRST204")

        def update(self, *_args, **_kwargs):
            raise Exception("PGRST204")

        def insert(self, *_args, **_kwargs):
            raise Exception("PGRST204")

        def execute(self):
            raise Exception("PGRST204")

    class _BrokenDB:
        def table(self, _name):
            return _BrokenTable()

    monkeypatch.setattr(auth, "get_supabase", lambda: _BrokenDB())
    monkeypatch.setattr(auth, "send_otp_email", lambda _email, _otp: (True, "ok"))

    result = auth.request_otp("test@example.com")

    assert result["success"] is True


def test_verify_otp_reads_from_memory_store(monkeypatch):
    auth = importlib.import_module("utils.auth")

    class _BrokenTable:
        def select(self, *_args, **_kwargs):
            return self

        def eq(self, *_args, **_kwargs):
            return self

        def limit(self, *_args, **_kwargs):
            return self

        def upsert(self, *_args, **_kwargs):
            raise Exception("PGRST204")

        def update(self, *_args, **_kwargs):
            raise Exception("PGRST204")

        def insert(self, *_args, **_kwargs):
            raise Exception("PGRST204")

        def execute(self):
            raise Exception("PGRST204")

    class _BrokenDB:
        def table(self, _name):
            return _BrokenTable()

    monkeypatch.setattr(auth, "get_supabase", lambda: _BrokenDB())
    monkeypatch.setattr(auth, "send_otp_email", lambda _email, _otp: (True, "ok"))

    email = "verify@example.com"
    auth.request_otp(email)

    otp_record = auth._load_otp_from_memory(email)
    assert otp_record is not None

    valid = auth.verify_otp(email, otp_record["otp"])
    assert valid["success"] is True

    invalid = auth.verify_otp(email, "000000")
    assert invalid["success"] is False
