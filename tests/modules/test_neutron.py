# Copyright 2025 - Canonical Ltd
# SPDX-License-Identifier: GPL-3.0-only

import sys
import types

import pytest

from regress_stack.modules import neutron


@pytest.fixture()
def fake_neutron_lib(monkeypatch):
    """Provide a fake neutron_lib.constants without ACCESS_READONLY."""
    fake_constants = types.ModuleType("neutron_lib.constants")
    fake_constants.ACCESS_SHARED = "access_as_shared"
    fake_constants.ACCESS_EXTERNAL = "access_as_external"
    fake_lib = types.ModuleType("neutron_lib")
    fake_lib.constants = fake_constants
    monkeypatch.setitem(sys.modules, "neutron_lib", fake_lib)
    monkeypatch.setitem(sys.modules, "neutron_lib.constants", fake_constants)
    return fake_constants


def test_fix_neutron_lib_compat_patches_file(tmp_path, monkeypatch, fake_neutron_lib):
    db_file = tmp_path / "external_net_db.py"
    db_file.write_text(
        "EXTERNAL_NETWORK_RBAC_ACTIONS = {constants.ACCESS_SHARED,\n"
        "                                 constants.ACCESS_READONLY,\n"
        "                                 constants.ACCESS_EXTERNAL}\n"
    )
    warnings = []

    monkeypatch.setattr(neutron, "EXTERNAL_NET_DB", str(db_file))
    monkeypatch.setattr(
        neutron.core_utils,
        "warn_workaround",
        lambda subject, detail: warnings.append((subject, detail)),
    )

    neutron._fix_neutron_lib_compat()

    content = db_file.read_text()
    assert "ACCESS_READONLY" not in content
    assert "ACCESS_SHARED" in content
    assert "ACCESS_EXTERNAL" in content
    assert len(warnings) == 1


def test_fix_neutron_lib_compat_noop_when_constant_exists(
    tmp_path, monkeypatch, fake_neutron_lib
):
    fake_neutron_lib.ACCESS_READONLY = "access_as_readonly"

    db_file = tmp_path / "external_net_db.py"
    db_file.write_text(
        "EXTERNAL_NETWORK_RBAC_ACTIONS = {constants.ACCESS_SHARED,\n"
        "                                 constants.ACCESS_READONLY,\n"
        "                                 constants.ACCESS_EXTERNAL}\n"
    )

    monkeypatch.setattr(neutron, "EXTERNAL_NET_DB", str(db_file))

    neutron._fix_neutron_lib_compat()

    content = db_file.read_text()
    assert "ACCESS_READONLY" in content  # not patched


def test_fix_neutron_lib_compat_noop_when_file_missing(
    tmp_path, monkeypatch, fake_neutron_lib
):
    missing = tmp_path / "does_not_exist.py"
    monkeypatch.setattr(neutron, "EXTERNAL_NET_DB", str(missing))

    # Should not raise
    neutron._fix_neutron_lib_compat()
