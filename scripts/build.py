#!/usr/bin/env python3
# Copyright 2026 The Ophelia Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Builds Ophelia for one platform.

Runs the steps Ophelia owns (its patch layers and rebranding) here, and hands
everything else to platforms/<os>/build.py, which drives the upstream Helium
platform repo.
"""

import argparse
import importlib.util
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLATFORMS = {'Linux': 'linux'}


def load_platform(name):
    """Imports platforms/<name>/build.py"""
    path = ROOT / 'platforms' / name / 'build.py'
    spec = importlib.util.spec_from_file_location(f'platform_{name}', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def patch_dirs(name):
    """Ophelia's patch layers, applied after Helium's"""
    return [ROOT / 'patches', ROOT / 'platforms' / name / 'patches']


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform',
                        choices=sorted(PLATFORMS.values()),
                        default=PLATFORMS.get(platform.system()))
    args = parser.parse_args()
    if not (ROOT / 'platforms' / args.platform / 'build.py').exists():
        sys.exit(f'{args.platform} is not supported yet')

    target = load_platform(args.platform)
    build_dir = ROOT / 'build' / args.platform

    # TODO: target.prepare(build_dir): fetch sources, apply Helium's patches
    # TODO: target.apply_patches(build_dir, patch_dirs(args.platform))
    # TODO: rebrand.run(source tree)
    # TODO: target.build(build_dir), then target.package(build_dir)


if __name__ == '__main__':
    main()
