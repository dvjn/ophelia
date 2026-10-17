#!/usr/bin/env bash
# Copyright 2026 The Ophelia Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.

# Makes a development build like helium-linux's `he setup` and `he build`: a
# component build of Helium with Ophelia's patches on top, applied with quilt
# so later runs only reapply the patches from the first changed one onwards.

set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# the box shares the host's PATH, so make sure its own tools come first
export PATH="/usr/bin:$PATH"

. "$root/helium-linux/scripts/shared.sh"
. "$root/helium-linux/helium-chromium/devutils/set_quilt_vars.sh"
setup_environment

# keep the build tree out of the submodule
_build_dir="$root/build/linux"
_dl_cache="$_build_dir/download_cache"
_src_dir="$_build_dir/src"
_out_dir="$_src_dir/out/Default"
_subs_cache="$_build_dir/subs.tar.gz"
_namesubs_cache="$_build_dir/namesubs.tar"
mkdir -p "$_dl_cache"

export QUILT_PATCHES="$_build_dir/patches"

ophelia_quilt() {
    # quilt prefers the patches path it recorded over QUILT_PATCHES, so keep it
    # current in case the build dir moved
    if [ -d "$_src_dir/.pc" ]; then
        echo "$QUILT_PATCHES" >"$_src_dir/.pc/.quilt_patches"
    fi
    (cd "$_src_dir" && quilt --quiltrc - "$@")
}

ophelia_prepare() {
    local stamp="$_src_dir/.ophelia-prepared.stamp"
    if [ -f "$stamp" ]; then
        return
    fi
    fetch_sources false false
    python3 "$_main_repo/utils/prune_binaries.py" --keep-build-dependencies "$_src_dir" "$_main_repo/pruning.list"
    helium_resources
    helium_version
    SCCACHE_ENABLED=y write_gn_args
    sed -i s/is_official_build/is_component_build/ "$_out_dir/args.gn"
    touch "$stamp"
}

ophelia_patches() {
    local merged="$_build_dir/patches.new"
    rm -rf "$merged"
    python3 "$_main_repo/utils/patches.py" merge "$merged" \
        "$_main_repo/patches" "$_root_dir/patches" "$root/patches"

    local applied=() new=()
    if [ -f "$_src_dir/.pc/applied-patches" ]; then
        mapfile -t applied <"$_src_dir/.pc/applied-patches"
    fi
    mapfile -t new < <(grep -v '^$' "$merged/series")

    local keep=0
    while [ "$keep" -lt "${#applied[@]}" ] && [ "$keep" -lt "${#new[@]}" ] &&
        [ "${applied[keep]}" = "${new[keep]}" ] &&
        cmp -s "$QUILT_PATCHES/${applied[keep]}" "$merged/${new[keep]}"; do
        keep=$((keep + 1))
    done
    if [ "$keep" -eq "${#applied[@]}" ] && [ "$keep" -eq "${#new[@]}" ]; then
        rm -rf "$merged"
        echo 'patches are up to date'
        return
    fi

    if [ "$keep" -lt "${#applied[@]}" ]; then
        if [ "$keep" -gt 0 ]; then
            ophelia_quilt pop "${applied[keep - 1]}"
        else
            ophelia_quilt pop -a
        fi
    fi
    rm -rf "$QUILT_PATCHES"
    mv "$merged" "$QUILT_PATCHES"
    if [ "$keep" -lt "${#new[@]}" ]; then
        ophelia_quilt push -a
    fi
}

ophelia_prepare
ophelia_patches
python3 "$root/scripts/mtimes.py" "$_src_dir" "$_build_dir/mtimes.pickle"
gn_gen
build -k 0
