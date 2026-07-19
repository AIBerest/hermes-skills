# Security forensics

Use this reference when the operator wants attribution for who changed or deleted important files, especially config, dependency, or deploy paths.

## Forensics baseline

### 1. Targeted `auditd` watches

Enable focused file-change watches on the project or runtime paths that actually matter:

```bash
sudo apt-get update -y
sudo apt-get install -y auditd audispd-plugins
sudo systemctl enable --now auditd

sudo tee /etc/audit/rules.d/server-doctor-forensics.rules >/dev/null <<'EOF'
-w <project-root> -p wa -k project_changes
-w <project-root>/package.json -p wa -k project_pkg
-w <project-root>/package-lock.json -p wa -k project_pkg
-w <project-root>/docker-compose.yml -p wa -k project_runtime
-a always,exit -F arch=b64 -S execve -F auid=<service-user-uid> -k operator_exec
-a always,exit -F arch=b32 -S execve -F auid=<service-user-uid> -k operator_exec
EOF

sudo augenrules --load
```

Keep the rule set narrow. A small, relevant watch list is far more useful than a noisy everything-watch.

### 2. `sudo` input/output logging

If the environment allows it, capture privileged shell history with sudo I/O logs:

```bash
sudo tee /etc/sudoers.d/99-sudo-io-logging >/dev/null <<'EOF'
Defaults log_output
Defaults log_input
Defaults iolog_dir="/var/log/sudo-io"
Defaults logfile="/var/log/sudo.log"
Defaults timestamp_type=global
EOF
sudo chmod 440 /etc/sudoers.d/99-sudo-io-logging
sudo visudo -cf /etc/sudoers.d/99-sudo-io-logging
sudo mkdir -p /var/log/sudo-io
sudo touch /var/log/sudo.log
```

## Verification

```bash
systemctl is-active auditd
sudo auditctl -l | grep -E 'project_changes|project_pkg|project_runtime|operator_exec'
sudo visudo -cf /etc/sudoers.d/99-sudo-io-logging
```

## Incident queries

```bash
sudo ausearch -k project_changes -i
sudo ausearch -k project_pkg -i
sudo ausearch -k project_runtime -i
sudo ausearch -k operator_exec -i
sudo less /var/log/sudo.log
sudo ls -la /var/log/sudo-io
```

## Notes

- without this baseline, retroactive attribution is often impossible
- keep rules focused so the audit stream stays readable
- record the exact watched paths and the target UID in the operator handoff, otherwise the setup becomes guesswork later

## SSH and Firewall Hardening Runbook

Use this when the operator asks to lock down SSH or close unnecessary public exposure on a VPS.

Before changing anything:

- verify current SSH access works with key-only auth from the operator path
- record the current SSH source address as seen by the server, not just the workstation's idea of its public IP
- collect the known operator/VPS allowlist from the private topology or operator-provided map
- list current listeners with `ss -tulpn` and classify which public ports must remain intentionally reachable
- create backups of `/etc/ssh/sshd_config`, `/etc/ssh/sshd_config.d/`, firewall status, and iptables/nft state
- schedule a short rollback timer before enabling a deny-by-default firewall

Safe SSH baseline for private automation hosts:

```text
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
PermitRootLogin prohibit-password
PermitEmptyPasswords no
MaxAuthTries 3
LoginGraceTime 30
X11Forwarding no
```

Firewall baseline:

- default deny incoming
- default allow outgoing
- allow SSH only from the recorded operator/server allowlist
- explicitly allow only the public service ports that are intentionally exposed
- keep Docker/VPN published ports in mind; do not enable a routed deny policy without checking those services still work

Post-change verification must happen before cancelling rollback:

```bash
ssh -o BatchMode=yes -o PreferredAuthentications=publickey -o PasswordAuthentication=no <host> 'hostname; whoami'
ssh -o BatchMode=yes -o PreferredAuthentications=password -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=0 <host> true
sshd -T | egrep '^(permitrootlogin|passwordauthentication|kbdinteractiveauthentication|pubkeyauthentication|x11forwarding|maxauthtries|logingracetime)'
ufw status verbose
ss -tulpn
```

Also verify any other allowed management host can still reach SSH, and any intentionally public web/VPN ports still answer. Only then stop the rollback timer. Record the final policy in private topology, not in public docs.
