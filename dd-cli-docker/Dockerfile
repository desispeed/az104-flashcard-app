# dd-cli (DoorDash CLI) in a container, for headless/server use on a GCP VM.
# The binary is a glibc-linked linux/amd64 ELF, so the base is debian-slim
# (NOT alpine/musl) and we install ca-certificates for HTTPS to DoorDash.

# ---- fetch: download, verify checksum, extract the pinned release ----
FROM debian:bookworm-slim AS fetch
ARG DD_CLI_VERSION=0.2.2
# sha256 of dd-cli-v${DD_CLI_VERSION}-linux-amd64.tar.gz (DoorDash-published value).
ARG DD_CLI_SHA256=1be803988e41a3f4f093df80e0ea5065940dda8343c565284e26b1d5a8fd289c
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /tmp/dd
RUN set -eux; \
    dir="dd-cli-v${DD_CLI_VERSION}-linux-amd64"; \
    file="${dir}.tar.gz"; \
    curl -fsSL -o "${file}" \
      "https://github.com/doordash-oss/doordash-cli/releases/download/v${DD_CLI_VERSION}/${file}"; \
    echo "${DD_CLI_SHA256}  ${file}" | sha256sum -c -; \
    tar xzf "${file}"; \
    install -m 0755 "${dir}/${dir}" /usr/local/bin/dd-cli; \
    /usr/local/bin/dd-cli --version

# ---- runtime: minimal image with just the CLI + CA certs ----
FROM debian:bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -r -m -u 10001 ddcli
COPY --from=fetch /usr/local/bin/dd-cli /usr/local/bin/dd-cli
USER ddcli
WORKDIR /home/ddcli
# Auth in a headless container comes from DD_CLI_ACCESS_TOKEN at *run* time
# (obtain it on a desktop with `dd-cli login` / `dd-cli export-token`).
# Never bake the token into the image.
ENTRYPOINT ["dd-cli"]
CMD ["--help"]
