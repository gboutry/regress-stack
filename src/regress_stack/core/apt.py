# Copyright 2025 - Canonical Ltd
# SPDX-License-Identifier: Apache-2.0

import typing

import apt

APT_CACHE: typing.Optional[apt.Cache] = None


def get_cache() -> apt.Cache:
    global APT_CACHE

    if APT_CACHE is None:
        APT_CACHE = apt.Cache()

    return APT_CACHE


def pkgs_installed(pkgs: typing.List[str]) -> bool:
    apt_cache = get_cache()

    try:
        return all([apt_cache[pkg].is_installed for pkg in pkgs])
    except KeyError:
        return False


def get_pkg_version(pkg: str) -> typing.Optional[str]:
    apt_cache = get_cache()

    try:
        pkg_version = apt_cache[pkg].installed
    except KeyError:
        return None
    if pkg_version is None:
        return None
    return pkg_version.version
