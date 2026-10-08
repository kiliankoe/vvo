export const REPO = 'kiliankoe/vvo';
export const REPO_URL = `https://github.com/${REPO}`;
export const REPO_BLOB_URL = `${REPO_URL}/blob/main`;
export const RAW_URL = `https://raw.githubusercontent.com/${REPO}`;
export const WEBAPI = 'https://webapi.vvo-online.de';
// Written by .github/workflows/health-check.yml to a separate branch so hourly
// results don't clutter the main history or trigger site rebuilds.
export const HEALTH_URL = `${RAW_URL}/status-data/health.json`;
export const GTFS_URL = `${REPO_URL}/releases/latest/download/vvo-gtfs.zip`;
