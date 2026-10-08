import type { APIRoute } from 'astro';
import { loadStations } from '../lib/data';

// Compact index for client-side search. Arrays instead of objects keep it small.
export const GET: APIRoute = async () => {
	const stations = await loadStations();
	const rows = stations.map((s) => [s.id, s.numeric_id, s.name, s.city, s.latitude, s.longitude, s.lines]);
	return new Response(JSON.stringify(rows), { headers: { 'Content-Type': 'application/json' } });
};
