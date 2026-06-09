import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

// How long to wait on a single `docker ps` before giving up on a host.
const DOCKER_TIMEOUT_MS = Number(process.env.DOCKER_TIMEOUT_MS || 15000);

/**
 * Query containers on a single host.
 *
 * @param {{ name: string, dockerHost?: string }} host
 *   dockerHost is a Docker connection string, e.g. "ssh://user@1.2.3.4".
 *   Leave it empty/undefined to talk to the local Docker daemon.
 * @returns {Promise<Array>} normalized container objects
 */
export async function getContainers(host) {
  const env = { ...process.env };
  if (host.dockerHost) {
    env.DOCKER_HOST = host.dockerHost;
  }

  // `{{json .}}` emits one JSON object per container, one per line.
  const args = ['ps', '-a', '--no-trunc', '--format', '{{json .}}'];

  const { stdout } = await execFileAsync('docker', args, {
    env,
    timeout: DOCKER_TIMEOUT_MS,
    maxBuffer: 8 * 1024 * 1024,
  });

  return stdout
    .trim()
    .split('\n')
    .filter(Boolean)
    .map((line) => {
      const c = JSON.parse(line);
      return {
        id: c.ID,
        name: c.Names,
        image: c.Image,
        state: c.State, // "running", "exited", "paused", "created", ...
        status: c.Status, // human string, e.g. "Up 3 hours"
        ports: c.Ports || '',
        createdAt: c.CreatedAt,
      };
    });
}
