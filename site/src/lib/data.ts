import { readFile, stat } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

export const repoRoot = path.resolve(process.cwd(), '..');
export const repoPath = (...p: string[]) => path.join(repoRoot, ...p);

export interface Station {
	id: string;
	numeric_id: string;
	name: string;
	city: string;
	name_with_city: string;
	latitude: number;
	longitude: number;
	operators: string[];
	lines: Record<string, string[]>;
	total_lines: number;
}

export async function loadStations(): Promise<Station[]> {
	const json = JSON.parse(await readFile(repoPath('data/stations.json'), 'utf8'));
	return json.stations;
}

/** Minimal CSV parser for our own well-formed files (quoted fields, no embedded newlines). */
export async function loadCsv(file: string): Promise<Record<string, string>[]> {
	const [header, ...rows] = (await readFile(repoPath(file), 'utf8')).trim().split(/\r?\n/).map(splitCsvLine);
	return rows.map((row) => Object.fromEntries(header.map((h, i) => [h, row[i] ?? ''])));
}

function splitCsvLine(line: string): string[] {
	const out: string[] = [];
	let cur = '';
	let quoted = false;
	for (let i = 0; i < line.length; i++) {
		const c = line[i];
		if (quoted) {
			if (c === '"' && line[i + 1] === '"') (cur += '"'), i++;
			else if (c === '"') quoted = false;
			else cur += c;
		} else if (c === '"') quoted = true;
		else if (c === ',') out.push(cur), (cur = '');
		else cur += c;
	}
	out.push(cur);
	return out;
}

export async function fileInfo(file: string) {
	const { size } = await stat(repoPath(file));
	let updated: string | undefined;
	try {
		updated = execFileSync('git', ['log', '-1', '--format=%cI', '--', file], { cwd: repoRoot, encoding: 'utf8' }).trim() || undefined;
	} catch {
		// Not a git checkout, e.g. a source tarball.
	}
	return { size, updated };
}

export const formatBytes = (n: number) =>
	n < 1024 ? `${n} B` : n < 1024 ** 2 ? `${(n / 1024).toFixed(0)} KB` : `${(n / 1024 ** 2).toFixed(1)} MB`;
