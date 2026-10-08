import { fold } from './vvo';

export type StopRow = [id: string, numericId: string, name: string, city: string, lat: number, lon: number, lines: Record<string, string[]>];

let index: Promise<StopRow[]> | undefined;
export function loadStops(): Promise<StopRow[]> {
	index ??= fetch(`${import.meta.env.BASE_URL}stops.json`).then((r) => r.json());
	return index;
}


/** Ranks exact ID matches first, then names starting with the query, then all other matches. */
export function searchStops(stops: StopRow[], query: string, limit = 50): StopRow[] {
	const q = fold(query);
	if (!q) return [];
	const terms = q.split(' ');
	const scored: [number, StopRow][] = [];
	for (const row of stops) {
		const [id, numericId, name, city] = row;
		if (query.trim() === id || query.trim() === numericId) {
			scored.push([0, row]);
			continue;
		}
		const fName = fold(name);
		const hay = `${fName} ${fold(city)}`;
		if (!terms.every((t) => hay.includes(t))) continue;
		// Prefer Dresden for ambiguous names since most visitors look for city stops.
		const rank = (fName.startsWith(q) ? 1 : 2) + (city === 'Dresden' ? 0 : 0.5);
		scored.push([rank, row]);
	}
	return scored
		.sort((a, b) => a[0] - b[0] || a[1][2].localeCompare(b[1][2], 'de'))
		.slice(0, limit)
		.map(([, row]) => row);
}
