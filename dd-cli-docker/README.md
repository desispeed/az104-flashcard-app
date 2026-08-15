# dd-cli in Docker (DoorDash CLI) — headless on a GCP VM

Containerized [`dd-cli`](https://github.com/doordash-oss/doordash-cli) **v0.2.2**,
built for **linux/amd64** to run headless on a server/VM.

- Base: `debian:bookworm-slim` (the binary is glibc-linked — not Alpine-safe).
- Release is **pinned + checksum-verified** in the Dockerfile against DoorDash's
  published `sha256` (`1be8039…d289c`).
- Runs as a **non-root** user; no ports exposed (outbound calls only).

> **Heads-up on where this was built:** I verified every build step against the
> real v0.2.2 release (download, checksum match, extract, `--version`/`--help`),
> but I could **not** run `docker build` from my sandbox — its network policy
> blocks Docker Hub — and I have **no access to your GCP VM**. So the two steps
> below (build, deploy) are things **you** run on the VM. Ping me and I'll walk
> through any errors.

---

## 1. Get an access token (on your DESKTOP, once)

A container has no browser or keychain, so `dd-cli login` can't run there.
Authenticate on your desktop and export the token:

```bash
# desktop (macOS/Linux): download dd-cli from the releases page, then:
dd-cli login          # browser sign-in to YOUR DoorDash account
dd-cli export-token   # prints an access token — copy it
```

`dd-cli` reads `DD_CLI_ACCESS_TOKEN` in headless environments; when set, it
takes precedence over the keychain. Tokens expire — re-run the two commands to
refresh, and update the token on the VM.

## 2. Build + run on the GCP VM

Copy this folder to the VM (or `git clone` the branch), then:

```bash
cd dd-cli-docker
cp .env.example .env
# paste your token into .env  (DD_CLI_ACCESS_TOKEN=...)

docker compose build

# one-off commands — dd-cli is a CLI, not a daemon:
docker compose run --rm dd-cli --json-output find-nearby-stores --help
docker compose run --rm dd-cli --json-output menu <store-id>
```

Or without compose:

```bash
docker build -t dd-cli:0.2.2 .
docker run --rm -e DD_CLI_ACCESS_TOKEN="$DD_CLI_ACCESS_TOKEN" \
  dd-cli:0.2.2 --json-output find-nearby-stores --help
```

Deploy straight from your Mac over SSH (no shell needed on the VM):

```bash
gcloud compute ssh VM_NAME --zone=ZONE --command \
  'cd dd-cli-docker && docker compose build && \
   DD_CLI_ACCESS_TOKEN=YOUR_TOKEN docker compose run --rm dd-cli --version'
```

## 3. Available commands

`address`, `build-grocery-list`, `cart`, `find-items`, `find-nearby-stores`,
`item-details`, `login`, `menu`, `order`, `export-token`, … (`--help` for all).

Add the global **`--json-output`** flag for machine-readable output — use that
if an agent/LLM will consume the results.

---

## Security notes
- **`DD_CLI_ACCESS_TOKEN` is a credential for your DoorDash account** (it can
  place real orders). Keep `.env` out of git (already gitignored) and off shared
  hosts. Prefer injecting it at run time over baking it into an image.
- The token is passed only at `docker run` time and never written into an image
  layer.
- Refresh the token when it expires (re-run `login` + `export-token`).

## Bump the version later
Edit the two build args in the `Dockerfile` (`DD_CLI_VERSION`, `DD_CLI_SHA256`)
using the new release's published `.sha256`, then rebuild.
