# Copyright 2025 - Canonical Ltd
# SPDX-License-Identifier: GPL-3.0-only

from regress_stack.modules import heat


def test_ensure_heat_api_wsgi_creates_symlink(tmp_path, monkeypatch):
    heat_api = tmp_path / "heat-api"
    heat_wsgi_api = tmp_path / "heat-wsgi-api"
    heat_wsgi_api.write_text("")
    warnings = []

    monkeypatch.setattr(heat, "HEAT_API_BINARY", heat_api)
    monkeypatch.setattr(heat, "HEAT_API_WSGI", heat_wsgi_api)
    monkeypatch.setattr(
        heat.core_utils,
        "warn_workaround",
        lambda subject, detail: warnings.append((subject, detail)),
    )

    heat._ensure_heat_api_wsgi()

    assert heat_api.is_symlink()
    assert heat_api.resolve() == heat_wsgi_api.resolve()
    assert len(warnings) == 1


def test_ensure_heat_api_wsgi_is_noop_when_present(tmp_path, monkeypatch):
    heat_api = tmp_path / "heat-api"
    heat_api.write_text("existing binary")
    heat_wsgi_api = tmp_path / "heat-wsgi-api"
    heat_wsgi_api.write_text("")
    warnings = []

    monkeypatch.setattr(heat, "HEAT_API_BINARY", heat_api)
    monkeypatch.setattr(heat, "HEAT_API_WSGI", heat_wsgi_api)
    monkeypatch.setattr(
        heat.core_utils,
        "warn_workaround",
        lambda subject, detail: warnings.append((subject, detail)),
    )

    heat._ensure_heat_api_wsgi()

    assert not heat_api.is_symlink()
    assert heat_api.read_text() == "existing binary"
    assert len(warnings) == 0


def test_ensure_heat_api_wsgi_noop_when_wsgi_missing(tmp_path, monkeypatch):
    heat_api = tmp_path / "heat-api"
    heat_wsgi_api = tmp_path / "heat-wsgi-api"
    warnings = []

    monkeypatch.setattr(heat, "HEAT_API_BINARY", heat_api)
    monkeypatch.setattr(heat, "HEAT_API_WSGI", heat_wsgi_api)
    monkeypatch.setattr(
        heat.core_utils,
        "warn_workaround",
        lambda subject, detail: warnings.append((subject, detail)),
    )

    heat._ensure_heat_api_wsgi()

    assert not heat_api.exists()
    assert len(warnings) == 0
