# VVO/DVB API Comparison Guide

This guide helps you choose the right API or data source for your Dresden public transport application.

## Quick Decision Matrix

| Use Case                 | Recommended API | Why                               |
| ------------------------ | --------------- | --------------------------------- |
| Simple departure display | Widget API      | Lightweight, easy to parse        |
| Mobile app               | WebAPI          | Rich features, JSON format        |
| Professional integration | TRIAS           | Standards-based, official support |
| Data analysis            | GTFS            | Complete dataset, standard format |
| Real-time tracking       | WebAPI or TRIAS | Live delays and service alerts    |
| Route planning           | WebAPI or TRIAS | Full journey planning features    |
| Stop/station search      | WebAPI or TRIAS | Comprehensive search options      |

## Feature Comparison

| Feature                    | Widget API   | WebAPI        | TRIAS        | GTFS                  |
| -------------------------- | ------------ | ------------- | ------------ | --------------------- |
| **Format**                 | JSON (array) | JSON          | XML          | CSV/Protobuf          |
| **Protocol**               | HTTP         | HTTP          | HTTP         | File download         |
| **Authentication**         | None         | None          | None/API key | None                  |
| **Real-time data**         | Minutes only | Yes, detailed | Yes          | Via GTFS-RT           |
| **Stop search**            | Basic        | Advanced      | Advanced     | N/A (bulk data)       |
| **Route planning**         | ❌           | ✔︎             | ✔︎            | ✔︎ (with tools)        |
| **Departure board**        | ✔︎            | ✔︎             | ✔︎            | ❌ (scheduled only)   |
| **Line information**       | ❌           | ✔︎             | ✔︎            | ✔︎                     |
| **Service alerts**         | ❌           | ✔︎             | ✔︎            | ✔︎ (GTFS-RT)           |
| **Vehicle positions**      | ❌           | ❌            | Limited      | ❌ (not in free feed) |
| **Occupancy data**         | ❌           | ✔︎             | ❌           | ❌                    |
| **Fare information**       | ❌           | Limited       | ✔︎            | ✔︎                     |
| **Accessibility info**     | ❌           | ✔︎             | ✔︎            | ✔︎                     |
| **Map data (pins, zones)** | ❌           | ✔︎             | ❌           | ❌                    |
| **Historical data**        | ❌           | ❌            | ❌           | ✔︎                     |

## Detailed API Characteristics

### Widget API

**Pros**

- Extremely simple format
- No parsing complexity
- Lightweight responses
- Works everywhere
- No authentication

**Cons**

- Limited features
- No real-time delays
- Basic data only
- No route planning
- Commercial use prohibited

**Best for**: Hobby projects, home displays, simple widgets

### WebAPI

**Pros**

- Rich feature set
- Real-time delays
- Modern JSON format
- Mobile-optimized
- Comprehensive data

**Cons**

- Undocumented (community reverse-engineered)
- May change without notice
- No CORS support
- No official support

**Best for**: Mobile apps, web applications, home automation

### TRIAS

**Pros**

- Official API
- Standards-based
- Comprehensive features
- Stable interface
- Professional support
- European standard

**Cons**

- XML complexity
- Verbose responses
- Steeper learning curve
- Larger payloads

**Best for**: Professional applications, long-term projects, commercial use

### GTFS

**Pros**

- Complete dataset
- Industry standard
- Many tools available
- No API limits
- Offline capable
- Historical data

**Cons**

- Not real-time (without GTFS-RT)
- Bulk download only
- Requires processing
- Storage needed

**Best for**: Analysis, offline apps, route optimization, research

## Technical Requirements

| Aspect                    | Widget API | WebAPI   | TRIAS          | GTFS      |
| ------------------------- | ---------- | -------- | -------------- | --------- |
| **Min. HTTP version**     | HTTP/1.0   | HTTP/1.1 | HTTP/1.1       | N/A       |
| **SSL/TLS**               | Optional   | Required | No (HTTP only) | Required  |
| **CORS support**          | Yes        | No       | No             | N/A       |
| **Compression**           | No         | gzip     | gzip           | ZIP files |
| **Typical response time** | <500ms     | <1s      | <2s            | N/A       |
| **Max response size**     | ~10KB      | ~100KB   | ~500KB         | ~50MB     |

## Rate Limiting and Stability

| API        | Rate Limits             | Stability | Error Rate |
| ---------- | ----------------------- | --------- | ---------- |
| Widget API | Fair use only           | Good      | Low        |
| WebAPI     | Unknown (be respectful) | Variable  | Medium     |
| TRIAS      | Depends on access level | Excellent | Very Low   |
| GTFS       | None (download)         | N/A       | N/A        |

**Recommended request intervals:**

- Widget API: Max 1 request/minute per stop
- WebAPI: Max 10 requests/minute total
- TRIAS: Varies by agreement
- GTFS: Daily download
