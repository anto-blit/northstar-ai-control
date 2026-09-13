// Compile once for publication. Visitors need no CDN or Tailwind runtime.
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const cwd = fileURLToPath(new URL('.', import.meta.url));
const result = spawnSync(process.execPath, [
  'node_modules/@tailwindcss/cli/dist/index.mjs',
  '-i', 'homepage.css', '-o', 'homepage.compiled.css', '--minify',
], { cwd, stdio: 'inherit', windowsHide: true });
if (result.error) throw result.error;
if (result.status !== 0) process.exit(result.status ?? 1);
const inputs = ['homepage.html', 'homepage.css', 'homepage.compiled.css',
  'package.json', 'package-lock.json', 'build_styles.mjs'];
const hashes = Object.fromEntries(inputs.map(name => [name,
  createHash('sha256').update(readFileSync(new URL(name, import.meta.url))).digest('hex')]));
writeFileSync(new URL('homepage-style-build.json', import.meta.url),
  JSON.stringify({ note: 'Build provenance, not scientific evidence.', sha256: hashes }, null, 2) + '\n');
