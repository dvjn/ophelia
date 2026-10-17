# Copyright 2026 The Ophelia Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Stops files whose content didn't change from looking stale to the build.

Tools like quilt rewrite files even when their content ends up the same, which
gives them a new mtime and makes the build recompile everything that depends
on them. Before each build, every file whose mtime changed since the last
build but whose content didn't gets its old mtime back, and the current state
is recorded for next time.
"""

import hashlib
import os
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

_SKIP = {'out', '.pc'}


def _scan(src):
    """mtime and size of every regular file in src, outside out/ and .pc/"""
    found = {}
    stack = [src]
    while stack:
        with os.scandir(stack.pop()) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    if not (entry.name in _SKIP and os.path.dirname(entry.path) == src):
                        stack.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    stat = entry.stat(follow_symlinks=False)
                    found[os.path.relpath(entry.path, src)] = (stat.st_mtime_ns, stat.st_size)
    return found


def _digests(src, rels):
    digests = []
    for rel in rels:
        with open(os.path.join(src, rel), 'rb') as file:
            digests.append(hashlib.file_digest(file, 'sha256').digest())
    return digests


def _hash(src, rels):
    chunks = [rels[i:i + 2000] for i in range(0, len(rels), 2000)]
    with ProcessPoolExecutor() as pool:
        results = pool.map(_digests, [src] * len(chunks), chunks)
    return dict(zip(rels, (digest for chunk in results for digest in chunk)))


def run(src, state_file):
    """Restores mtimes in the source tree at src, then records its state in state_file"""
    src = str(src)
    old = {}
    if state_file.exists():
        with state_file.open('rb') as file:
            old = pickle.load(file)

    current = _scan(src)
    changed = [rel for rel, stat in current.items() if old.get(rel, (None, None))[:2] != stat]
    digests = _hash(src, changed)

    state = {}
    restored = 0
    for rel, (mtime, size) in current.items():
        if rel not in digests:
            state[rel] = old[rel]
            continue
        prev = old.get(rel)
        if prev and prev[1:] == (size, digests[rel]):
            os.utime(os.path.join(src, rel), ns=(prev[0], prev[0]))
            mtime = prev[0]
            restored += 1
        state[rel] = (mtime, size, digests[rel])

    tmp = state_file.with_suffix('.tmp')
    with tmp.open('wb') as file:
        pickle.dump(state, file, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(tmp, state_file)
    if old:
        print(f'{len(changed)} files touched since the last build, '
              f'{restored} of them unchanged and given their old mtime back')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(f'usage: {sys.argv[0]} <source dir> <state file>')
    run(sys.argv[1], Path(sys.argv[2]))
