# O11 Pro v5.0

![O11 Pro](docs/logo.png)

New release · Linux x86-64 · Version 5.0

**Open [README.html](README.html) for the installation guide and full screenshot gallery.**

Open [HELP.html](HELP.html) for the Help Center covering workspace functions, playback checks, maintenance, and troubleshooting. The same help is available at `/help` in the application.

## Install

```bash
sudo apt install python3 ffmpeg unzip
unzip O11-Pro-v5.0-Linux-x64.zip -d o11v5
cd o11v5
sudo bash install.sh
```

Requires systemd. The installer prompts for an admin username, hidden password (12+ characters), confirmation, and an available port. Open `http://localhost:8080/login` using your selected port. No default password is supplied. Existing installations are not overwritten.

## Operate

```bash
sudo systemctl status o11v5
sudo journalctl -u o11v5 -n 50 --no-pager
```

Data: `/var/lib/o11v5` · Credentials: `/etc/o11v5.env` (root-only) · Binary: `/opt/o11v5/o11pro-v5`.

The installed server listens on loopback. Configure an HTTPS reverse proxy for remote access. Python maintenance tools are optional and not automatically scheduled. Read the HTML guide for scope and service-name requirements. The binary is compiled and stripped, not encrypted.

## Screenshots

Actual captures from a fresh local workspace.

| Login | Providers |
|---|---|
| ![Login](screenshots/01-login.jpg) | ![Providers](screenshots/02-providers.jpg) |

| Monitoring | Users |
|---|---|
| ![Monitoring](screenshots/03-monitoring.jpg) | ![Users](screenshots/04-users.jpg) |

| Servers | Jobs |
|---|---|
| ![Servers](screenshots/05-servers.jpg) | ![Jobs](screenshots/06-jobs.jpg) |

[Website](https://www.o11.shop) · [Telegram](https://t.me/Playreadydrm?direct)

© 2026–2027 O11 Pro
