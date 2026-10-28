#!/usr/bin/env python3
"""Observe O11 RSS; optionally restart after sustained high usage. No dependencies."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit-mb', type=int, default=1536)
    parser.add_argument('--sustain-seconds', type=int, default=300)
    parser.add_argument('--restart', action='store_true', help='Opt in: may interrupt streams')
    args = parser.parse_args()
    if args.limit_mb < 128 or args.sustain_seconds < 60:
        parser.error('limit must be >=128 MB and sustain time >=60 seconds')
    root = Path('/var/lib/o11-memory-guard')
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (root / 'lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        result = subprocess.run(['systemctl', 'show', 'o11pro', '-p', 'MainPID', '--value'],
                                capture_output=True, text=True, check=True)
        pid = int(result.stdout.strip())
        if pid <= 0:
            print('O11 inactive; no action')
            return
        # Include wrapper and backend, but not unrelated FFmpeg worker processes.
        children = set()
        for task in Path(f'/proc/{pid}/task').iterdir():
            try:
                children.update((task / 'children').read_text().split())
            except FileNotFoundError:
                continue
        pids = [str(pid)]
        for child in sorted(children):
            try:
                if 'backend-' in os.readlink(f'/proc/{child}/exe'):
                    pids.append(child)
            except FileNotFoundError:
                continue
        rss_kb = 0
        identities = []
        for p in pids:
            try:
                status = Path(f'/proc/{p}/status').read_text()
                rss_kb += next(int(line.split()[1]) for line in status.splitlines()
                               if line.startswith('VmRSS:'))
                identities.append(p + ':' + Path(f'/proc/{p}/stat').read_text().rsplit(')', 1)[1].split()[19])
            except (FileNotFoundError, ProcessLookupError):
                print('Process changed during sampling; retry next run')
                return
        identity = ','.join(identities)
        state_file = root / 'state.json'
        try:
            state = json.loads(state_file.read_text())
        except (FileNotFoundError, ValueError):
            state = {}
        now = time.monotonic()
        high = rss_kb > args.limit_mb * 1024
        since = state.get('since') if state.get('identity') == identity else None
        since = (since or now) if high else None
        # Keep only one state record: no unbounded diagnostic files.
        state = {'identity': identity, 'rss_mb': round(rss_kb / 1024, 1),
                 'since': since, 'sample_monotonic': now}
        temporary = root / 'state.tmp'
        temporary.write_text(json.dumps(state))
        temporary.replace(state_file)
        sustained = high and now - since >= args.sustain_seconds
        print(json.dumps({**state, 'sustained_high_memory': sustained,
                          'automatic_restart_enabled': args.restart}))
        if sustained and args.restart:
            # Does not remove mappings, drop caches, or delete application files.
            subprocess.run(['systemctl', 'restart', 'o11pro'], check=True, timeout=45)
            print('O11 restarted after sustained RSS limit breach')


if __name__ == '__main__':
    main()
