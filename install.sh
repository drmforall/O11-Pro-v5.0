#!/usr/bin/env bash
set -euo pipefail
umask 077

if [[ ${EUID} -ne 0 ]]; then
  echo 'Run with sudo bash install.sh' >&2; exit 1
fi
if [[ $(uname -m) != x86_64 || $(uname -s) != Linux ]]; then
  echo 'This release requires Linux x86-64.' >&2; exit 1
fi
command -v systemctl >/dev/null || { echo 'systemd is required.' >&2; exit 1; }
systemctl show-environment >/dev/null 2>&1 || { echo 'Start systemd first (including in WSL).' >&2; exit 1; }
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd "$script_dir"
[[ -f o11pro-v5 && -f SHA256SUMS.txt ]] || { echo 'Extract the entire release ZIP first.' >&2; exit 1; }
sha256sum --check SHA256SUMS.txt
if [[ -e /etc/o11v5.env || -e /etc/systemd/system/o11v5.service || -e /opt/o11v5/o11pro-v5 ]]; then
  echo 'An O11 v5 installation already exists. Refusing to overwrite its credentials or executable.' >&2; exit 1
fi
for dependency in python3 ffmpeg; do
  command -v "$dependency" >/dev/null || { echo "Install $dependency using your Linux package manager, then rerun." >&2; exit 1; }
done
read -r -p 'Admin username [admin]: ' admin_user < /dev/tty
admin_user=${admin_user:-admin}
[[ $admin_user =~ ^[A-Za-z0-9_.-]{1,64}$ ]] || { echo 'Use letters, digits, underscore, dot or dash for the username.' >&2; exit 1; }
read -r -s -p 'Create admin password (minimum 12 characters): ' admin_password < /dev/tty; echo
read -r -s -p 'Confirm admin password: ' confirmation < /dev/tty; echo
[[ ${#admin_password} -ge 12 && $admin_password == "$confirmation" ]] || { echo 'Passwords must match and be at least 12 characters.' >&2; exit 1; }
read -r -p 'HTTP port [8080]: ' port < /dev/tty
port=${port:-8080}
[[ $port =~ ^[0-9]{1,5}$ ]] && ((10#$port >= 1024 && 10#$port <= 65535)) || { echo 'Choose a port from 1024 to 65535.' >&2; exit 1; }
python3 - "$port" <<'PY'
import socket, sys
with socket.socket() as listener:
    try:
        listener.bind(('127.0.0.1', int(sys.argv[1])))
    except OSError:
        sys.exit('Port already occupied; stop the existing server or choose another port.')
PY
if ! id o11v5 >/dev/null 2>&1; then
  useradd --system --home-dir /var/lib/o11v5 --shell /usr/sbin/nologin o11v5
fi
install -d -m 755 /opt/o11v5
install -m 755 o11pro-v5 /opt/o11v5/o11pro-v5
install -d -o o11v5 -g o11v5 -m 700 /var/lib/o11v5 /var/cache/o11v5
# Encode environment values without exposing credentials in commands or logs.
escape_env() { local value=$1; value=${value//\\/\\\\}; value=${value//\"/\\\"}; printf '%s' "$value"; }
{
  printf 'O11_ADMIN_USER="%s"\n' "$(escape_env "$admin_user")"
  printf 'O11_ADMIN_PASSWORD="%s"\n' "$(escape_env "$admin_password")"
} > /etc/o11v5.env
chmod 600 /etc/o11v5.env
unset admin_password confirmation
cat > /etc/systemd/system/o11v5.service <<EOF
[Unit]
Description=O11 Pro v5 streaming server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=o11v5
Group=o11v5
WorkingDirectory=/var/lib/o11v5
EnvironmentFile=/etc/o11v5.env
Environment=XDG_CACHE_HOME=/var/cache/o11v5
ExecStart=/opt/o11v5/o11pro-v5 -p $port -b 127.0.0.1 -path /var/lib/o11v5 -user \${O11_ADMIN_USER} -password \${O11_ADMIN_PASSWORD} -stdout
Restart=on-failure
RestartSec=3
KillMode=control-group
TimeoutStopSec=30
UMask=0077

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now o11v5.service
ready=false
for attempt in {1..30}; do
  if python3 - "$port" <<'PY'
import sys, urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:' + sys.argv[1] + '/login', timeout=1) as response:
        sys.exit(0 if response.status == 200 else 1)
except Exception:
    sys.exit(1)
PY
  then ready=true; break; fi
  sleep 1
done
if [[ $ready != true ]]; then
  echo 'Installed, but startup failed. Inspect: sudo journalctl -u o11v5' >&2; exit 1
fi
printf '\nInstalled successfully.\nLogin: http://localhost:%s/login\nUsername: %s\nPassword: the password you entered\n' "$port" "$admin_user"
echo 'Service: o11v5 | Data: /var/lib/o11v5 | Credentials: /etc/o11v5.env (root only)'
echo 'The listener is local-only. Use an authenticated HTTPS reverse proxy for remote access.'
