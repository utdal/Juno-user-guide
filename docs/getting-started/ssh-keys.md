# SSH Key Authentication

## Overview

SSH key authentication replaces your password with a cryptographic key pair — a **private key** on your machine and a **public key** on Juno. This page explains why SSH keys are recommended, how they work under the hood, and how to set them up on every major platform.

```
            Your Machine                              Juno HPC Cluster
  ┌─────────────────────────────┐           ┌──────────────────────────────────┐
  │  ~/.ssh/id_ed25519          │           │  ~/.ssh/authorized_keys          │
  │  (private key — stays here) │           │  (your public key lives here)    │
  │                             │    SSH    │                                  │
  │  $ ssh netID@juno…          │──────────►│  ✓ Challenge verified — welcome! │
  │    "prove you have the key" │◄──────────│  "sign this challenge"           │
  └─────────────────────────────┘           └──────────────────────────────────┘
```

---

## Why SSH Keys?

Typing a password every time you log in is inconvenient — but more importantly, passwords carry real security risks on shared research infrastructure like Juno.

**Practical benefits:**

- **No password prompts** — log in with a single command, every time
- **Works with scripts and automation** — jobs, `rsync` transfers, and VS Code remote connections all work seamlessly
- **Multiple devices** — add a key from your laptop and your workstation independently
- **Easy to revoke** — remove a single key from `authorized_keys` without changing your password for everyone

!!! tip
    SSH keys are the recommended authentication method for Juno. Most automation workflows (VS Code Remote, file sync scripts, Jupyter tunnels) require them.

---

## How SSH Keys Are More Secure

SSH key authentication is fundamentally different from — and stronger than — passwords. Here's why.

### The Problem with Passwords

| Risk | How It Happens |
|------|----------------|
| **Brute force** | Automated tools try millions of passwords per second |
| **Phishing** | You're tricked into entering your password on a fake site |
| **Credential stuffing** | A breached password from another site is tried on Juno |
| **Network interception** | A passive observer records a password in transit |
| **Shoulder surfing** | Someone watches you type |

### How SSH Keys Eliminate These Risks

SSH keys use **asymmetric cryptography** (Ed25519 by default on Juno). A key pair has two parts:

- **Private key** (`~/.ssh/id_ed25519`) — never leaves your machine. Treat it like a physical house key.
- **Public key** (`~/.ssh/id_ed25519.pub`) — safe to share. Juno stores it in `~/.ssh/authorized_keys`.

```
  Authentication flow (no secret is ever transmitted):

  1. You connect:      $ ssh netID@juno.utdallas.edu
  2. Juno challenges:  "Sign this random 256-bit nonce with your private key"
  3. Your client:      Signs it locally using ~/.ssh/id_ed25519
  4. Juno verifies:    Checks the signature against your public key
  5. Result:           Access granted — no password, no secret sent over the wire
```

**Why this is stronger:**

- **Nothing to steal in transit** — the private key never leaves your machine; only a cryptographic signature is sent
- **Immune to brute force** — Ed25519 keys are 256-bit; cracking one would take longer than the age of the universe
- **Immune to phishing** — your client only signs challenges from the exact host key it already trusts; a fake server gets nothing usable
- **Immune to credential stuffing** — keys are unique per user and never reused across services
- **Passphrase protection (optional)** — encrypts the private key on disk so that even if your laptop is stolen, the key cannot be used without the passphrase

!!! note
    Ed25519 is the key type used on Juno. It is more compact and faster than the older RSA-4096 while providing equivalent or better security.

---

## Before You Begin

You'll need:

- A terminal on your local machine (Terminal on Mac/Linux, PowerShell or Windows Terminal on Windows)
- Your Juno credentials (NetID and password) — used **once** during setup, then replaced by the key

---

## Step 1 — Generate a Key Pair

**Linux / Mac**

Open your terminal and run:

```bash
ssh-keygen -t ed25519 -C "netID@utdallas.edu"
```

Replace `netID` with your actual UT Dallas NetID.

You'll see:

```
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/you/.ssh/id_ed25519):
```

Press **Enter** to accept the default path.

```
Enter passphrase (empty for no passphrase):
```

**A passphrase is strongly recommended.** It encrypts your private key so it cannot be used if your machine is ever compromised. You'll only type it once per session (see [Using ssh-agent](#using-ssh-agent--skip-the-passphrase-prompt)).

After completion, two files are created:

| File | Contents | Share? |
|------|----------|--------|
| `~/.ssh/id_ed25519` | **Private key** — keep secret | **Never** |
| `~/.ssh/id_ed25519.pub` | Public key — goes to Juno | Yes |

**Windows (PowerShell)**

Open **PowerShell** and run:

```powershell
ssh-keygen -t ed25519 -C "netID@utdallas.edu"
```

Accept the default path (`C:\Users\you\.ssh\id_ed25519`) by pressing **Enter**.

Enter and confirm a passphrase when prompted (recommended).

Your keys are saved to:

| File | Location |
|------|----------|
| Private key | `C:\Users\<you>\.ssh\id_ed25519` |
| Public key | `C:\Users\<you>\.ssh\id_ed25519.pub` |

**Windows (PuTTYgen)**

If you use PuTTY for SSH access:

1. Download and open **PuTTYgen** (included with the [PuTTY installer](https://www.putty.org/))
2. Under **Parameters**, select **EdDSA** and leave the curve at **Ed25519**
3. Click **Generate** and move your mouse over the blank area to create randomness
4. Enter a **Key passphrase** and confirm it
5. Click **Save private key** → save as `id_ed25519.ppk` somewhere safe
6. Copy the text from the **Public key for pasting into OpenSSH authorized_keys file** box — you'll need it in Step 2

!!! note
    PuTTY uses its own `.ppk` key format. If you also use PowerShell or WSL, generate a separate OpenSSH key using the PowerShell instructions above.

---

## Step 2 — Copy Your Public Key to Juno

**Linux / Mac**

The `ssh-copy-id` command handles everything automatically:

```bash
ssh-copy-id netID@juno.utdallas.edu
```

You'll be prompted for your **Juno password once**. After that, key-based login is active.

What this does: appends your `~/.ssh/id_ed25519.pub` to `~/.ssh/authorized_keys` on Juno with correct permissions.

**Windows (PowerShell)**

PowerShell does not include `ssh-copy-id`. Use this one-liner instead:

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh netID@juno.utdallas.edu "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Enter your Juno password when prompted. This is the last time you'll need it.

**Manual method (any platform)**

If the automated commands above don't work, copy the key by hand:

1. Display your public key locally:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   Copy the entire output — it starts with `ssh-ed25519` and ends with your comment.

2. Log in to Juno with your password:
   ```bash
   ssh netID@juno.utdallas.edu
   ```

3. On Juno, add your public key:
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   nano ~/.ssh/authorized_keys      # paste your public key on a new line
   chmod 600 ~/.ssh/authorized_keys
   ```

4. Log out and test the key (see Step 3).

**Windows (PuTTY)**

After generating a key in PuTTYgen (Step 1):

1. Log in to Juno with your password using PuTTY
2. Paste the public key text into `~/.ssh/authorized_keys`:
   ```bash
   mkdir -p ~/.ssh && chmod 700 ~/.ssh
   nano ~/.ssh/authorized_keys
   # Paste the public key text, save and exit
   chmod 600 ~/.ssh/authorized_keys
   ```
3. In PuTTY, go to **Connection → SSH → Auth → Credentials** and browse to your `.ppk` private key file
4. Save the PuTTY session so the key is loaded automatically

---

## Step 3 — Test Your Key

Log out (if you're still connected) and reconnect:

```bash
ssh netID@juno.utdallas.edu
```

You should log in **without being asked for your Juno password**. If you set a passphrase, you'll be asked for that instead.

A successful login looks like:

```
Enter passphrase for key '/home/you/.ssh/id_ed25519':
Last login: Mon May 12 09:15:42 2025 from 10.x.x.x
[netID@juno-l-01 ~]$
```

!!! tip
    If you're still being asked for your Juno password (not a passphrase), see [Troubleshooting](#troubleshooting).

---

## Step 4 — Set Up an SSH Config File (Optional but Recommended)

An SSH config file lets you type `ssh juno` instead of the full command, and sets useful defaults automatically.

Create or open `~/.ssh/config` on your **local machine**:

```bash
nano ~/.ssh/config
```

Add the following block:

```
Host juno
    HostName juno.utdallas.edu
    User netID
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Replace `netID` with your actual UT Dallas NetID.

Save and exit. Now you can connect with just:

```bash
ssh juno
```

**What these options do:**

| Option | Effect |
|--------|--------|
| `HostName` | Full cluster hostname |
| `User` | Your NetID so you never need to type it |
| `IdentityFile` | Exact key to use for this host |
| `ServerAliveInterval 60` | Sends a keepalive every 60 seconds — prevents timeout disconnects |
| `ServerAliveCountMax 3` | Drops the connection after 3 missed keepalives |

---

## Using ssh-agent — Skip the Passphrase Prompt

If you set a passphrase on your key, `ssh-agent` caches it in memory so you only type it once per login session.

**Linux / Mac**

```bash
# Start the agent (usually already running on modern systems)
eval "$(ssh-agent -s)"

# Add your key — you'll type your passphrase once
ssh-add ~/.ssh/id_ed25519

# All subsequent SSH connections this session are passphrase-free
ssh juno
```

On **Mac**, the system Keychain can store the passphrase permanently:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

Then add to `~/.ssh/config`:

```
Host *
    UseKeychain yes
    AddKeysToAgent yes
```

**Windows (PowerShell)**

Enable and start the SSH Agent service (run PowerShell as Administrator once):

```powershell
Set-Service ssh-agent -StartupType Automatic
Start-Service ssh-agent
```

Then add your key:

```powershell
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

---

## Managing Your Keys on Juno

### View Authorized Keys

On Juno, all trusted public keys live in one file:

```bash
cat ~/.ssh/authorized_keys
```

Each line is one authorized key. You can have keys from multiple machines in this file.

### Add Another Machine

Repeat Step 1 on the new machine to generate a new key pair, then run Step 2 to copy its public key to Juno. Each machine should have its own unique key.

### Revoke a Key

If a machine is lost or stolen, remove its key from Juno immediately:

```bash
# On Juno — open the file and delete the line for the compromised key
nano ~/.ssh/authorized_keys
```

Removing the public key makes the corresponding private key useless — no password change required.

### Rotate Keys

It's good practice to generate fresh keys periodically or when changing machines:

1. Generate a new key pair on your machine
2. Add the new public key to `~/.ssh/authorized_keys` on Juno
3. Verify the new key works
4. Delete the old key from `~/.ssh/authorized_keys`

---

## Troubleshooting

### Still being asked for my Juno password

The key was likely not copied correctly, or file permissions are wrong. On **Juno**, run:

```bash
# Correct permissions — SSH is strict about this
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
ls -la ~/.ssh/
```

SSH will silently ignore `authorized_keys` if the file or directory permissions are too open.

### Permission denied (publickey)

Check which key your client is offering:

```bash
ssh -v netID@juno.utdallas.edu 2>&1 | grep "Offering\|Trying"
```

If it's not offering `id_ed25519`, specify it explicitly:

```bash
ssh -i ~/.ssh/id_ed25519 netID@juno.utdallas.edu
```

Or add `IdentityFile ~/.ssh/id_ed25519` to your `~/.ssh/config` (see [SSH Config File](#step-4--set-up-an-ssh-config-file-optional-but-recommended)).

### Bad permissions on private key

```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```

Fix the permissions on your **local machine**:

```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

### Forgot my passphrase

There is no way to recover a forgotten passphrase — the encryption is one-way. Generate a new key pair (Step 1) and copy the new public key to Juno (Step 2). Then remove the old key from `~/.ssh/authorized_keys` on Juno.

### Key works from one machine but not another

Each machine needs its own key pair. Copying a private key from machine to machine is a security risk and often causes permission problems. Instead, generate a fresh key on each machine and add each public key as a separate line in `~/.ssh/authorized_keys` on Juno.

### Connection still drops after adding keepalive

Add `TCPKeepAlive yes` to your `~/.ssh/config`:

```
Host juno
    HostName juno.utdallas.edu
    User netID
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
```

---

## Quick Reference

### Key Generation

| Platform | Command |
|----------|---------|
| Linux / Mac / PowerShell | `ssh-keygen -t ed25519 -C "netID@utdallas.edu"` |
| View public key | `cat ~/.ssh/id_ed25519.pub` |
| View authorized keys on Juno | `cat ~/.ssh/authorized_keys` |

### Copying Key to Juno

| Platform | Command |
|----------|---------|
| Linux / Mac | `ssh-copy-id netID@juno.utdallas.edu` |
| Windows PowerShell | `type $env:USERPROFILE\.ssh\id_ed25519.pub \| ssh netID@juno.utdallas.edu "cat >> .ssh/authorized_keys"` |

### Permissions (must be exact)

| Path | Permission | Command |
|------|------------|---------|
| `~/.ssh/` | `drwx------` | `chmod 700 ~/.ssh` |
| `~/.ssh/id_ed25519` | `-rw-------` | `chmod 600 ~/.ssh/id_ed25519` |
| `~/.ssh/id_ed25519.pub` | `-rw-r--r--` | `chmod 644 ~/.ssh/id_ed25519.pub` |
| `~/.ssh/authorized_keys` | `-rw-------` | `chmod 600 ~/.ssh/authorized_keys` |

### Connecting

| Purpose | Command |
|---------|---------|
| Login | `ssh netID@juno.utdallas.edu` |
| Login with config alias | `ssh juno` |
| Login with specific key | `ssh -i ~/.ssh/id_ed25519 netID@juno.utdallas.edu` |
| Debug connection issues | `ssh -v netID@juno.utdallas.edu` |

---

## Next Steps

After setting up SSH key authentication:

1. [Set up an SSH Config alias for faster logins →](#step-4--set-up-an-ssh-config-file-optional-but-recommended)
2. [Connect VS Code directly to Juno →](../gui-and-tools/vscode.md)
3. [Transfer files with rsync or scp →](storage.md)
4. [Submit your first job →](../running-programs/slurm.md)

## Need Help?

- **Email**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **HPC Services**: [hpc.utdallas.edu/services](https://hpc.utdallas.edu/services)
