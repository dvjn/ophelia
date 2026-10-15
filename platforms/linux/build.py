# Copyright 2026 The Ophelia Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Linux steps for scripts/build.py, driving upstream/ (helium-linux)"""

from pathlib import Path

UPSTREAM = Path(__file__).resolve().parent / 'upstream'


def prepare(build_dir):
    """Fetches the sources and applies Helium's core and Linux patches"""
    # TODO: helium-linux shared.sh: fetch_sources, apply_patches, with its
    # build paths pointed at build_dir


def apply_patches(build_dir, patch_dirs):
    """Applies Ophelia's patch layers on top"""
    # TODO: helium-chromium/utils/patches.py apply <src> *patch_dirs


def build(build_dir):
    """Runs the remaining helium-linux build steps"""
    # TODO: domsub, name substitution, translations, version, resources,
    # gn args, toolchain, gn gen, build


def package(build_dir):
    """Packages the build with Ophelia's package/ files"""
    # TODO: AppImage and deb from package/
