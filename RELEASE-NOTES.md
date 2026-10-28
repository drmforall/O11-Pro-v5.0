# O11 Pro 5.0 · Linux x86-64

O11 Pro v5.0 is a new Linux release, packaged 28 October 2026.

## Included

- Compiled, stripped Linux executable with embedded interface assets and logo.
- Login page with password visibility control, scalable SVG icons, and charcoal panels.
- Website and Telegram footer links with 2026–2027 copyright text.
- Interactive systemd installer with hidden password entry and checksum verification.
- Offline HTML guide, Markdown and text documentation, and six application screenshots.
- Optional Python memory-observation and completed-HLS cleanup utilities.

## Requirements

Linux x86-64, systemd, Python 3, and FFmpeg. WSL must have systemd enabled.
The installer uses a dedicated service account, binds to loopback, and refuses
to replace an existing installation. Remote access requires additional setup.

## Verification status

Desktop navigation, Monitoring tabs, and opening/canceling Provider, User,
Server, and Job dialogs were checked in the browser. Login succeeded during
screenshot capture. No browser errors occurred in the checked flows.
Installer shell syntax and archive checksums were verified. The installer has
not been exercised on a clean machine. No source provider is configured in the
test workspace, so playback, persistent creation workflows, and cleanup after
a real stream finishes are not certified by this release.

## Maintenance-tool scope

The installer does not schedule the Python tools automatically. The memory
guard defaults to service `o11pro`, matching the development host; adapt its
service references to `o11v5` for the installed release. It observes memory;
it does not repair an established internal backend leak. Restart mode is opt-in.

The cleanup tool's default directory is specific to the development host.
For an installed release, explicitly supply:

```bash
sudo python3 tools/stream_cleanup.py --root /var/lib/o11v5/hls/live
```

Preview first; add `--apply` to delete eligible completed HLS groups. All
playlists must include `#EXT-X-ENDLIST`; open or recently used files are retained
for a 120-second grace period. This does not clean arbitrary temporary files,
unmarked abandoned streams, recordings, VOD, or replay data.

## Distribution

The executable is compiled and stripped, not encrypted. It extracts its embedded
backend to the runtime cache and executes it from disk. Credentials, application
data, logs, and source-build directories are excluded from this archive. Python
utilities and the shell installer are intentionally supplied as readable scripts.
