import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import type { Loader } from 'astro/loaders';
import { REPO_BLOB_URL } from './config';

const repoRoot = path.resolve(process.cwd(), '..');
const docsDir = path.join(repoRoot, 'documentation');
const readmePath = path.join(repoRoot, 'README.md');

// The markdown is written for GitHub, so it has no frontmatter, uses an H1 as the
// title and links to sibling files. This loader adapts it for Starlight without
// keeping a second copy of the docs in the site.
export function repoDocsLoader(): Loader {
	return {
		name: 'repo-docs',
		async load({ store, parseData, renderMarkdown, generateDigest, watcher }) {
			const sync = async () => {
				const entries = await collectEntries();
				store.clear();
				for (const entry of entries) {
					const data = await parseData({ id: entry.id, data: { title: entry.title, ...entry.extra } });
					store.set({
						id: entry.id,
						data,
						body: entry.body,
						filePath: path.relative(process.cwd(), entry.file),
						digest: generateDigest(entry.body),
						rendered: await renderMarkdown(entry.body),
					});
				}
			};
			await sync();
			watcher?.add([docsDir, readmePath]);
			watcher?.on('change', (changed) => {
				if (changed.startsWith(docsDir) || changed === readmePath) sync();
			});
		},
	};
}

interface Entry {
	id: string;
	file: string;
	title: string;
	body: string;
	extra?: Record<string, unknown>;
}

async function collectEntries(): Promise<Entry[]> {
	const entries: Entry[] = [];
	for (const name of (await readdir(docsDir)).filter((f) => f.endsWith('.md')).sort()) {
		const file = path.join(docsDir, name);
		const { title, body } = splitTitle(await readFile(file, 'utf8'));
		entries.push({
			id: `docs/${name.replace(/\.md$/, '')}`,
			file,
			title,
			body: rewriteLinks(promoteSections(body), 'documentation'),
		});
	}

	// The ecosystem lists live in the README so they stay visible on GitHub.
	const readme = await readFile(readmePath, 'utf8');
	const start = readme.indexOf('\n## Libraries');
	if (start !== -1) {
		entries.push({
			id: 'ecosystem',
			file: readmePath,
			title: 'Libraries, apps & tools',
			body: rewriteLinks(readme.slice(start), ''),
			extra: { description: 'Community projects built on VVO data.' },
		});
	}
	return entries;
}

function splitTitle(markdown: string) {
	const match = markdown.match(/^#\s+(.+)\n/m);
	if (!match || match.index === undefined) return { title: 'Untitled', body: markdown };
	return {
		title: match[1].trim(),
		body: markdown.slice(0, match.index) + markdown.slice(match.index + match[0].length),
	};
}

// Some docs use further H1s as section headings. Starlight renders the title as the
// only H1 and builds the table of contents from H2/H3, so shift those docs down a level.
function promoteSections(body: string) {
	const lines = body.split('\n');
	let inFence = false;
	const hasH1 = lines.some((line) => {
		if (/^\s*(```|~~~)/.test(line)) inFence = !inFence;
		return !inFence && /^#\s/.test(line);
	});
	if (!hasH1) return body;
	inFence = false;
	return lines
		.map((line) => {
			if (/^\s*(```|~~~)/.test(line)) inFence = !inFence;
			return !inFence && /^#{1,5}\s/.test(line) ? `#${line}` : line;
		})
		.join('\n');
}

// Sibling docs and OpenAPI specs become site pages; other repo files link to GitHub.
function rewriteLinks(body: string, fromDir: string) {
	return body.replace(/\]\((?!https?:|mailto:|#)([^)\s]+)\)/g, (_, target: string) => {
		const [file, hash] = target.split('#');
		const resolved = path.posix.normalize(path.posix.join(fromDir, file));
		const doc = resolved.match(/^documentation\/([^/]+)\.md$/);
		const spec = resolved.match(/^openapi\/([^/]+)\.yaml$/);
		const suffix = hash ? `#${hash}` : '';
		if (doc) return `](${import.meta.env.BASE_URL}docs/${doc[1].toLowerCase()}/${suffix})`;
		if (spec) return `](${import.meta.env.BASE_URL}reference/${spec[1]}/)`;
		return `](${REPO_BLOB_URL}/${resolved}${suffix})`;
	});
}
