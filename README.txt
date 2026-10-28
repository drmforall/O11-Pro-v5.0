O11 Pro v5.0 - Linux x86-64

This release contains a compiled, stripped Linux executable with the logo,
login page, charcoal interface and icon assets embedded. It is not encrypted.
Source code, passwords, user configuration and media are excluded.

Requirements: Linux x86-64, Python 3 for optional guards, and FFmpeg for streaming.

INSTALLER (recommended; requires systemd):
  Ubuntu/Debian prerequisites: sudo apt install python3 ffmpeg
  sudo bash install.sh

The installer verifies package checksums, asks for an admin username and a
confirmed password of at least 12 characters, then installs and starts the
o11v5 service. Password entry is hidden and is not printed. Credentials are
saved in root-only /etc/o11v5.env. Existing installations are never overwritten.
It prompts for a port (default 8080) and refuses occupied ports. On a machine
already hosting O11, choose another port to install a separate instance.

Executable: /opt/o11v5/o11pro-v5
Data: /var/lib/o11v5
Service: sudo systemctl status o11v5
Login: http://localhost:YOUR_PORT/login
The installed service runs under a dedicated unprivileged account and listens
on loopback only. In WSL, systemd must be enabled. Optional cleanup utilities
remain separate and are not automatically scheduled by this installer.

Run:
  chmod +x o11pro-v5
  ./o11pro-v5 -p 8080 -b 127.0.0.1 -path /absolute/path/to/data

Use your existing secure authentication/startup configuration. Do not expose
the service publicly without configuring authentication. The executable writes
its embedded backend to the user's cache and executes it from disk (no UPX).
For systemd set XDG_CACHE_HOME to a writable cache directory.

Optional Python utilities are in tools/:
  python3 tools/memory_guard.py
    Samples the local o11pro systemd service. Observation mode by default.
    --restart enables restarts after 1536 MB RSS sustained for 300 seconds.
    This monitors excessive usage; it does not repair internal backend leaks.

  python3 tools/stream_cleanup.py --root /absolute/path/to/data/hls/live
    Preview cleanup of completed HLS stream subdirectories.
    Add --apply to enable deletion. Completion requires EXT-X-ENDLIST in all
    playlists, no open files and a 120-second grace period. VOD, replays and
    recordings are outside the default cleanup scope.

The Python tools are separate utilities; installing this ZIP does not install
the WSL machine's timers automatically. Configure scheduling for your host.

Verify files against SHA256SUMS.txt before installation. ZIP is an archive,
not password encryption or source-code protection.
