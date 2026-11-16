import { readdir, readFile } from 'node:fs/promises';
import { repoPath } from './data';

/** OpenAPI specs from the repo's openapi/ directory, keyed by file name without extension. */
export async function loadSpecs() {
	const files = (await readdir(repoPath('openapi'))).filter((f) => f.endsWith('.yaml')).sort();
	return Promise.all(
		files.map(async (file) => {
			const source = await readFile(repoPath('openapi', file), 'utf8');
			const title = source.match(/^\s{2}title:\s*["']?(.+?)["']?\s*$/m)?.[1] ?? file;
			// Set by specs whose API a browser can't call (plain http, missing CORS), so "try it" can't work.
			const browserBlocked = /^x-browser-blocked:\s*true\s*$/m.test(source);
			return { name: file.replace(/\.yaml$/, ''), file, title, source, browserBlocked };
		}),
	);
}
