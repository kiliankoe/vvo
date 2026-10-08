import type { APIRoute, GetStaticPaths } from 'astro';
import { loadSpecs } from '../../lib/specs';

// Publishes the specs next to the reference pages, so tools can import them by URL.
export const getStaticPaths = (async () =>
	(await loadSpecs()).map((spec) => ({ params: { file: spec.file }, props: { source: spec.source } }))) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) =>
	new Response(props.source as string, { headers: { 'Content-Type': 'application/yaml; charset=utf-8' } });
