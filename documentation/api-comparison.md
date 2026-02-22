# VVO/DVB API Comparison Guide

This guide helps you choose the right API or data source for your Dresden public transport application.

## Quick Decision Matrix

| Use Case                 | Recommended API | Why                                  |
| ------------------------ | --------------- | ------------------------------------ |
| Simple departure display | Widget API      | Lightweight, easy to parse           |
| Mobile app               | WebAPI          | Rich features, JSON format           |
| Professional integration | TRIAS           | Standards-based, official support    |
| Data analysis            | GTFS            | Complete dataset, standard format    |
| Real-time bulk feed      | SIRI ET         | All delays/cancellations in one feed |
| Real-time tracking       | WebAPI or TRIAS | Live delays and service alerts       |
| Route planning           | WebAPI or TRIAS | Full journey planning features       |
| Stop/station search      | WebAPI or TRIAS | Comprehensive search options         |

## Feature Comparison

| Feature                    | Widget API   | WebAPI        | TRIAS        | GTFS                  | SIRI ET           |
| -------------------------- | ------------ | ------------- | ------------ | --------------------- | ----------------- |
| **Format**                 | JSON (array) | JSON          | XML          | CSV/Protobuf          | XML               |
| **Protocol**               | HTTP         | HTTP          | HTTP         | File download         | File download     |
| **Authentication**         | None         | None          | None/API key | None                  | None (mirror)     |
| **Real-time data**         | Minutes only | Yes, detailed | Yes          | Via GTFS-RT           | Yes, full network |
| **Stop search**            | Basic        | Advanced      | Advanced     | N/A (bulk data)       | ❌                |
| **Route planning**         | ❌           | ✔︎             | ✔︎            | ✔︎ (with tools)        | ❌                |
| **Departure board**        | ✔︎            | ✔︎             | ✔︎            | ❌ (scheduled only)   | ✔︎ (all stops)     |
| **Line information**       | ❌           | ✔︎             | ✔︎            | ✔︎                     | ✔︎                 |
| **Service alerts**         | ❌           | ✔︎             | ✔︎            | ✔︎ (GTFS-RT)           | ❌                |
| **Vehicle positions**      | ❌           | ❌            | Limited      | ❌ (not in free feed) | ❌                |
| **Occupancy data**         | ❌           | ✔︎             | ❌           | ❌                    | ✔︎                 |
| **Platform information**   | ❌           | ✔︎             | ✔︎            | ❌                    | ✔︎ (rail)          |
| **Cancellation info**      | ❌           | ✔︎             | ✔︎            | ❌                    | ✔︎                 |
| **Fare information**       | ❌           | Limited       | ✔︎            | ✔︎                     | ❌                |
| **Accessibility info**     | ❌           | ✔︎             | ✔︎            | ✔︎                     | ❌                |
| **Map data (pins, zones)** | ❌           | ✔︎             | ❌           | ❌                    | ❌                |
| **Historical data**        | ❌           | ❌            | ❌           | ✔︎                     | ✔︎ (archived)      |

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

### SIRI ET

**Pros**

- Full network real-time data in a single feed
- Delay predictions, cancellations, occupancy
- European standard (CEN/TS 15531)
- Covers 16 operators across the VVO region
- Historical archives available
- CC BY-SA licensed

**Cons**

- Large XML files (~12–15 MB per snapshot)
- No stop search or journey planning
- No service alerts (text messages)
- Requires XML parsing

**Best for**: Network-wide real-time monitoring, delay analysis, data science, building departure boards

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
