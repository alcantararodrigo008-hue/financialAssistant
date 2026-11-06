"""Privacy regressions use synthetic data and never inspect secret values in output."""

import io
import json
import os
import re
import socket
import subprocess
import sys
from contextvars import ContextVar
from datetime import date
from ipaddress import ip_address
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from financial_assistant.models import Transaction
from financial_assistant.repository import SQLiteRepository
from financial_assistant.visualizations import (
    daily_trends_spec,
    expense_distribution_spec,
)

ROOT = Path(__file__).resolve().parents[1]


def test_streamlit_loads_private_launch_defaults():
    keys = ["server.address", "browser.gatherUsageStats", "server.enableCORS",
            "server.enableXsrfProtection", "server.enableStaticServing"]
    # Verify actual Streamlit resolution in a fresh process, not just TOML text.
    env = {k: v for k, v in os.environ.items() if not k.startswith("STREAMLIT_")}
    result = subprocess.run([sys.executable, "-c", ("import json; from streamlit import config; "
                             f"print(json.dumps([config.get_option(k) for k in {keys!r}]))")],
                            cwd=ROOT, env=env, capture_output=True, text=True, check=True)
    assert json.loads(result.stdout) == ["127.0.0.1", False, True, True, False]


def test_private_paths_are_ignored_without_creating_them():
    paths = ["data/private.csv", "data/nested/private.json", "custom.db", "custom.db-wal",
             "nested/private.sqlite", "nested/private.sqlite-shm", "nested/private.sqlite3-journal",
             ".env", ".env.local", "nested/.env", ".streamlit/secrets.toml"]
    result = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"], cwd=ROOT,
                            input=b"\0".join(p.encode() for p in paths) + b"\0", capture_output=True, check=True)
    assert {p.decode() for p in result.stdout.split(b"\0") if p} == set(paths)


def test_public_config_and_placeholder_remain_trackable():
    result = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"], cwd=ROOT,
                            input=b".streamlit/config.toml\0data/.gitkeep\0README.md\0",
                            capture_output=True, check=False)
    assert result.returncode == 1 and result.stdout == b""


def test_index_excludes_databases_and_known_secret_signatures():
    # Read the index rather than unrelated local edits. Report paths, never contents.
    listed = subprocess.run(["git", "ls-files", "--stage", "-z"], cwd=ROOT,
                            capture_output=True, check=True).stdout.split(b"\0")
    entries = [(record.split(b"\t", 1)[1], record.split()[1]) for record in listed if record]
    result = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT,
                            input=b"\n".join(oid for _, oid in entries) + b"\n",
                            capture_output=True, check=True)
    stream = io.BytesIO(result.stdout)
    signatures = [rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
                  rb"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}\b",
                  rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
                  rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b"]
    suspicious = []
    for path, oid in entries:
        header = stream.readline().split()
        assert header[:2] == [oid, b"blob"]
        content = stream.read(int(header[2]))
        assert stream.read(1) == b"\n"
        name = path.decode("utf-8")
        basename = name.rsplit("/", 1)[-1].lower()
        if (re.search(r"\.(?:db|sqlite|sqlite3)(?:-.*)?$", name, re.IGNORECASE)
                or basename == ".env" or basename.startswith(".env.") or basename == "secrets.toml"
                or content.startswith(b"SQLite format 3\0")
                or any(re.search(pattern, content) for pattern in signatures)):
            suspicious.append(name)
    assert not suspicious, f"Potential private artifacts in index (paths only): {suspicious}"


def test_local_financial_flow_needs_no_network_or_account(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    attempts = []

    def deny(*args, **kwargs):
        attempts.append(True)
        raise AssertionError("Unexpected network connection in local financial flow.")

    # Newer Streamlit creates asyncio loops per AppTest run. Windows implements
    # their internal socketpair using a loopback TCP handshake. Permit only that
    # stdlib setup in its own context, never application/external connections.
    pair_setup = ContextVar("pair_setup", default=False)
    real_pair, real_connect = socket.socketpair, socket.socket.connect

    def local_pair(*args, **kwargs):
        token = pair_setup.set(True)
        try:
            return real_pair(*args, **kwargs)
        finally:
            pair_setup.reset(token)

    def guarded_connect(sock, address):
        if pair_setup.get() and ip_address(address[0]).is_loopback:
            return real_connect(sock, address)
        return deny()

    monkeypatch.setattr(socket, "socketpair", local_pair)
    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    # Exercise the exception, then prove it does not leak to application calls.
    left, right = socket.socketpair()
    with left, right:
        left.sendall(b"synthetic")
        assert right.recv(9) == b"synthetic"
    with socket.socket() as probe:
        for address in ("127.0.0.1", "203.0.113.1"):
            with pytest.raises(AssertionError, match="Unexpected network connection"):
                probe.connect((address, 9))
    assert len(attempts) == 2
    attempts.clear()
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15).run()
    repo = SQLiteRepository()
    day = date(2024, 2, 29)
    app.date_input(key="dashboard_month").set_value(day).run()
    name = "Synthetic ![private](https://example.invalid/private) <script>window.probe=1</script>"
    for label, value in [("Goal name", name), ("Target amount (EUR)", "100"), ("Current savings (EUR)", "0")]:
        next(item for item in app.text_input if item.label == label).set_value(value)
    next(item for item in app.button if item.label == "Save goal").click().run()
    for kind, amount in [("income", "25.01"), ("expense", "5.00")]:
        next(item for item in app.selectbox if item.label == "Type").set_value(kind)
        next(item for item in app.text_input if item.label == "Amount (EUR)").set_value(amount)
        next(item for item in app.date_input if item.label == "Date").set_value(day)
        next(item for item in app.text_input if item.label == "Description (optional)").set_value("Synthetic '); DROP TABLE transactions; --")
        next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception
    assert [item.value for item in app.metric][:3] == ["25.01 EUR", "5.00 EUR", "20.01 EUR"]
    assert any(item.value == name for item in app.text)
    assert not any(name in item.value for item in app.markdown)
    before = repo.list_transactions(), repo.list_goals()
    next(item for item in app.text_input if item.label == "Amount (EUR)").set_value("NaN")
    next(item for item in app.button if item.label == "Save transaction").click().run()
    assert not app.exception and app.error
    reopened = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15).run()
    reopened.date_input(key="dashboard_month").set_value(day).run()
    assert not reopened.exception
    assert [item.value for item in reopened.metric][:3] == ["25.01 EUR", "5.00 EUR", "20.01 EUR"]
    assert (repo.list_transactions(), repo.list_goals()) == before
    assert not attempts


def test_charts_embed_only_needed_fields_without_remote_data_urls():
    description = "Synthetic private marker https://example.invalid/private"
    records = [Transaction("expense", "5", date(2024, 2, 29), "Food", description)]
    for spec in (expense_distribution_spec(records), daily_trends_spec(records)):
        assert "values" in spec["data"] and "url" not in spec["data"]
        assert description not in json.dumps(spec)
