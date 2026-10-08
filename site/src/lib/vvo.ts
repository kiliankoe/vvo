import { WEBAPI } from './config';

/** A response the WebAPI answered with a non-Ok status. Keeps the body, which can still be useful. */
export class WebApiError extends Error {
	constructor(
		readonly code: string,
		readonly body: { Name?: string; Place?: string; Status: { Code: string; Message?: string } },
	) {
		super(`${code}${body.Status.Message ? `: ${body.Status.Message}` : ''}`);
	}
}

export async function webapi<T>(path: string, body: Record<string, unknown>): Promise<T> {
	const res = await fetch(`${WEBAPI}/${path}`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json; charset=utf-8' },
		body: JSON.stringify({ ...body, format: 'json' }),
	});
	if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
	const json = await res.json();
	if (json.Status?.Code && json.Status.Code !== 'Ok') throw new WebApiError(json.Status.Code, json);
	return json as T;
}

/** Normalizes text for search: case, diacritics and ß don't matter, so "strasse" finds "Straße". */
export const fold = (s: string) =>
	s.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replace(/ß/g, 'ss').replace(/[^a-z0-9:]+/g, ' ').trim();

/** Parses the WebAPI's `/Date(1512400560000+0100)/` format. */
export function parseDate(value?: string): Date | undefined {
	const ms = value?.match(/-?\d+/)?.[0];
	return ms ? new Date(Number(ms)) : undefined;
}

const timeFmt = new Intl.DateTimeFormat('de-DE', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Berlin' });
const dateFmt = new Intl.DateTimeFormat('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'Europe/Berlin' });
export const formatTime = (d: Date) => timeFmt.format(d);
export const formatDate = (d: Date) => dateFmt.format(d);

const ALLOWED = new Set(['P', 'UL', 'OL', 'LI', 'B', 'STRONG', 'I', 'EM', 'U', 'BR', 'H2', 'H3', 'H4', 'A', 'TABLE', 'TBODY', 'TR', 'TD', 'TH']);

/**
 * Route change descriptions are HTML from a third party. Rebuild them from an allowlist
 * instead of trusting the markup, so nothing executable or styled reaches the page.
 */
export function sanitizeHtml(html: string): DocumentFragment {
	const source = new DOMParser().parseFromString(html, 'text/html').body;
	const out = document.createDocumentFragment();
	const copy = (from: Node, to: Node) => {
		for (const child of Array.from(from.childNodes)) {
			if (child.nodeType === Node.TEXT_NODE) {
				to.appendChild(document.createTextNode(child.textContent ?? ''));
			} else if (child instanceof Element) {
				if (!ALLOWED.has(child.tagName)) {
					copy(child, to);
					continue;
				}
				const el = document.createElement(child.tagName === 'H2' || child.tagName === 'H3' ? 'h4' : child.tagName);
				const href = child.getAttribute('href');
				if (child.tagName === 'A' && href && /^https?:\/\//.test(href)) {
					el.setAttribute('href', href);
					el.setAttribute('rel', 'noopener noreferrer');
				}
				copy(child, el);
				to.appendChild(el);
			}
		}
	};
	copy(source, out);
	return out;
}

export function el<K extends keyof HTMLElementTagNameMap>(
	tag: K,
	props: Record<string, string> = {},
	...children: (Node | string | null | undefined | false)[]
): HTMLElementTagNameMap[K] {
	const node = document.createElement(tag);
	for (const [k, v] of Object.entries(props)) node.setAttribute(k, v);
	for (const c of children) if (c) node.append(c);
	return node;
}
