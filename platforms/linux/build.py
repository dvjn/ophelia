# Copyright 2026 The Ophelia Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Linux steps for scripts/build.py, driving upstream/ (helium-linux).

Makes a development build like helium-linux's `he setup` and `he build`: a
component build whose patches are applied with quilt, so they can be updated
in place later.
"""

import filecmp
import os
import shutil
import subprocess
from pathlib import Path

UPSTREAM = Path(__file__).resolve().parent / 'upstream'
MAIN_REPO = UPSTREAM / 'helium-chromium'


def _helium(build_dir, script):
    """Runs script with helium-linux's shared.sh loaded and its paths pointed at build_dir"""
    subprocess.run([
        'bash', '-c', f'''
set -euo pipefail
. "$1/scripts/shared.sh"
setup_environment
_build_dir="$2"
_dl_cache="$_build_dir/download_cache"
_src_dir="$_build_dir/src"
_out_dir="$_src_dir/out/Default"
_subs_cache="$_build_dir/subs.tar.gz"
_namesubs_cache="$_build_dir/namesubs.tar"
mkdir -p "$_dl_cache"
{script}''', 'helium',
        str(UPSTREAM),
        str(build_dir)
    ],
                   check=True)


def _quilt(build_dir, *args):
    """Runs quilt in the source tree with Helium's quilt settings"""
    env = dict(os.environ,
               QUILT_PATCHES=str(build_dir / 'patches'),
               QUILT_PATCH_OPTS='--unified --reject-format=unified',
               QUILT_DIFF_ARGS='-p ab --no-timestamps --no-index',
               QUILT_REFRESH_ARGS='-p ab --no-timestamps --no-index --strip-trailing-whitespace',
               QUILT_DIFF_OPTS='--show-c-function',
               LC_ALL='C')
    # quilt prefers the patches path it recorded over QUILT_PATCHES, so keep it
    # current in case the build dir moved
    pc = source_dir(build_dir) / '.pc'
    if pc.exists():
        (pc / '.quilt_patches').write_text(f'{build_dir / "patches"}\n')
    subprocess.run(['quilt', '--quiltrc', '-', *args],
                   cwd=source_dir(build_dir),
                   env=env,
                   check=True)


def _series(patches):
    return [line for line in (patches / 'series').read_text().splitlines() if line]


def source_dir(build_dir):
    """The Chromium source tree inside build_dir"""
    return build_dir / 'src'


def prepare(build_dir):
    """Fetches the Chromium sources and sets up the tree for building"""
    stamp = source_dir(build_dir) / '.ophelia-prepared.stamp'
    if stamp.exists():
        return
    _helium(
        build_dir, '''
fetch_sources false false
python3 "$_main_repo/utils/prune_binaries.py" --keep-build-dependencies "$_src_dir" "$_main_repo/pruning.list"
helium_resources
helium_version
SCCACHE_ENABLED=y write_gn_args
sed -i s/is_official_build/is_component_build/ "$_out_dir/args.gn"
''')
    stamp.touch()


def apply_patches(build_dir, patch_dirs):
    """Applies Helium's core and Linux patches, then patch_dirs.

    Later runs only reapply the patches from the first changed one onwards.
    """
    src = source_dir(build_dir)
    patches = build_dir / 'patches'
    merged = build_dir / 'patches.new'
    shutil.rmtree(merged, ignore_errors=True)
    subprocess.run([
        'python3', MAIN_REPO / 'utils/patches.py', 'merge', merged, MAIN_REPO / 'patches',
        UPSTREAM / 'patches', *patch_dirs
    ],
                   check=True)

    applied_file = src / '.pc' / 'applied-patches'
    applied = applied_file.read_text().splitlines() if applied_file.exists() else []
    new = _series(merged)
    keep = 0
    for old_name, new_name in zip(applied, new):
        if old_name != new_name or not filecmp.cmp(
                patches / old_name, merged / new_name, shallow=False):
            break
        keep += 1
    if keep == len(applied) == len(new):
        shutil.rmtree(merged)
        print('patches are up to date')
        return

    if keep < len(applied):
        _quilt(build_dir, 'pop', *([applied[keep - 1]] if keep else ['-a']))
    shutil.rmtree(patches, ignore_errors=True)
    merged.rename(patches)
    if keep < len(new):
        _quilt(build_dir, 'push', '-a')


def build(build_dir):
    """Generates the build files and builds"""
    _helium(build_dir, 'gn_gen\nbuild -k 0')


def package(build_dir):
    """Packages the build with Ophelia's package/ files"""
    # TODO: AppImage and deb from package/
