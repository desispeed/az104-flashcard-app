# Container Status — iOS app + SSH agent

Monitor Docker containers on your **MacBook** and your **GCP VM** from an iPhone.

```
 iPhone (SwiftUI app)  ──HTTPS + Bearer token──▶  Agent (Node)  ──SSH──▶  MacBook docker
                                                                 └──SSH──▶  GCP VM docker
```

- **`ios/`** — native SwiftUI app (the on-phone client). Build it in Xcode on your Mac.
- **`server/`** — small Node agent that queries each host with Docker **SSH contexts**
  (`DOCKER_HOST=ssh://user@host docker ps`) and serves token-authed JSON.

> **Why an agent and not direct phone→host SSH?** Docker "SSH contexts" are a
> server-side concept, and your phone usually can't reach a NAT'd MacBook. The
> agent centralizes SSH access and exposes a single endpoint to the phone, so
> your SSH keys never leave the server.

---

## 1. Run the agent

Run it **on a machine that can SSH to both hosts**. Easiest: run it **on the
MacBook** — the Mac is then "local" (empty `dockerHost`) and the VM is reached
over SSH via its public IP. (If you'd rather host it on the VM, the VM can't
usually reach a NAT'd Mac — put both on a mesh VPN like Tailscale first.)

```bash
cd server
cp .env.example .env
# edit .env:  set API_TOKEN (openssl rand -hex 32) and HOSTS_JSON
```

Make sure the user running the agent can already do this **without a password
prompt** for each remote host (key-based auth + a known_hosts entry):

```bash
ssh you@VM_EXTERNAL_IP docker ps        # must succeed non-interactively
```

Then start it:

```bash
# Option A — Docker (recommended; mounts your ~/.ssh read-only)
docker compose up -d --build

# Option B — Node directly
npm install && npm start
```

Verify:

```bash
curl -H "Authorization: Bearer $API_TOKEN" http://localhost:8080/api/containers
```

### Exposing it to your phone, safely
The token is the only thing guarding this endpoint, so **do not** put plain
`http://` on the public internet. Pick one:
- **Tailscale (recommended):** install on the agent host and your phone; use the
  agent's tailnet IP/MagicDNS name as the backend URL. No ports exposed.
- **Reverse proxy with TLS** (Caddy/nginx + Let's Encrypt) in front of `:8080`.
- **LAN only:** use it on the same Wi-Fi as the agent (`http://mac.local:8080`).

---

## 2. Build the iOS app

You need a Mac with **Xcode** (this repo can't compile iOS code).

```bash
cd ios
brew install xcodegen        # one-time
xcodegen generate            # creates ContainerStatus.xcodeproj
open ContainerStatus.xcodeproj
```

No XcodeGen? Create a new Xcode **iOS App** (SwiftUI, iOS 17+) named
`ContainerStatus` and drag every file from `ios/ContainerStatus/` into it.

Then: set your signing team, run on the simulator or your iPhone, tap the gear,
and enter the **backend URL** + **API token**. The list auto-refreshes every 15s
and supports pull-to-refresh.

- 🟢 running · 🔴 exited/dead · 🟡 other (created/paused/restarting)
- An unreachable host shows the agent's SSH error inline.

---

## Security notes
- The agent refuses to start without `API_TOKEN`; the token is compared in
  constant time and stored on the phone in the **Keychain**.
- The agent only ever runs `docker ps -a` (read-only). It does not start, stop,
  or exec anything.
- Keep `.env` out of git (already gitignored).
