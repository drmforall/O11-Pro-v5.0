#!/usr/bin/env python3
"""Clean completed live HLS cache. Does not infer completion from file age alone."""
import argparse
import json
import os
from pathlib import Path
import stat
import time

SUFFIXES = {'.m3u8', '.ts', '.m4s', '.mp4', '.aac', '.vtt', '.tmp'}


def open_files():
    opened = set()
    # Fail closed if process descriptors cannot be inspected.
    for process in Path('/proc').iterdir():
        if not process.name.isdigit():
            continue
        try:
            for fd in (process / 'fd').iterdir():
                try:
                    info = fd.stat()
                    opened.add((info.st_dev, info.st_ino))
                except FileNotFoundError:
                    continue
        except FileNotFoundError:
            continue
    return opened


def cleanup(root, grace, apply):
    root = root.resolve(strict=True)
    playlists = list(root.rglob('*.m3u8'))
    candidates = {p.parent for p in playlists if not p.is_symlink()
                  and '#EXT-X-ENDLIST' in p.read_text(errors='replace')}
    removed = 0
    opened = open_files()
    for directory in candidates:
        # Never clear a shared root or recursively sweep unrelated subdirectories.
        if directory == root or directory.is_symlink():
            continue
        entries = list(directory.iterdir())
        if not entries or any(p.is_symlink() or not p.is_file() or p.suffix.lower() not in SUFFIXES
                              for p in entries):
            continue
        manifests = [p for p in entries if p.suffix == '.m3u8']
        # Master playlists or any still-live variant prevent deletion of the group.
        if not manifests or any('#EXT-X-ENDLIST' not in p.read_text(errors='replace') for p in manifests):
            continue
        snapshots = {p: p.stat() for p in entries}
        now = time.time()
        if any(now - max(s.st_mtime, s.st_atime) < grace or (s.st_dev, s.st_ino) in opened
               for s in snapshots.values()):
            continue
        for path, before in snapshots.items():
            # Revalidate immediately before unlink; no symlink traversal.
            current = path.lstat()
            if not stat.S_ISREG(current.st_mode) or (current.st_dev, current.st_ino, current.st_mtime_ns,
                    current.st_size) != (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_size):
                break
        else:
            print(json.dumps({'completed_cache': str(directory), 'files': len(entries), 'delete': apply}))
            if apply:
                for path in entries:
                    path.unlink()
                    removed += 1
                directory.rmdir()
    return removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('/mnt/e/work/o11v4/o11-data/hls/live'))
    parser.add_argument('--grace-seconds', type=int, default=120)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if args.grace_seconds < 30:
        parser.error('Grace must be at least 30 seconds to protect final segment playback')
    try:
        print(json.dumps({'removed': cleanup(args.root, args.grace_seconds, args.apply)}))
    except (PermissionError, FileNotFoundError) as error:
        print(json.dumps({'skipped': str(error)}))


if __name__ == '__main__':
    main()
