# VVO/DVB API Comparison Guide

This guide helps you choose the right API or data source for your Dresden public transport application.

## Quick Decision Matrix

| Use Case                 | Recommended API             | Why                                   |
| ------------------------ | --------------------------- | ------------------------------------- |
| Simple departure display | Widget API                  | Lightweight, easy to parse            |
| Mobile app               | WebAPI                      | Rich features, JSON format            |
| Professional integration | TRIAS                       | Standards-based, official support     |
| Data analysis            | GTFS                        | Complete dataset, standard format     |
| Real-time bulk feed      | SIRI ET                     | All delays/cancellations in one feed  |
| Real-time tracking       | WebAPI or TRIAS             | Live delays and service alerts        |
| Live vehicle positions   | [TLMS](tlms.md)             | Community WebSocket with GPS streams  |
| Route planning           | WebAPI or TRIAS             | Full journey planning features        |
| Cross-border routing     | [Transitous](transitous.md) | Europe-wide data, real-time routing   |
| Stop/station search      | WebAPI or TRIAS             | Comprehensive search options          |

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
- No authentication

**Cons**

- Limited features
- No real-time delays
- Basic data only
- No route planning
- Commercial use prohibited
- HTTP only, so browsers block it on HTTPS pages

**Best for**: Hobby projects, home displays, simple widgets

### WebAPI

**Pros**

- Rich feature set
- Real-time delays
- Modern JSON format
- Mobile-optimized
- Comprehensive data
- CORS enabled, usable from browsers

**Cons**

- Undocumented (community reverse-engineered)
- May change without notice
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
- No CORS preflight support, so not usable from browsers

**Best for**: Professional applications, long-term projects, commercial use

### OJP

**Pros**

- European standard, successor of TRIAS
- Stop search and journey planning with real-time data on VVO's server
- A DELFI-backed endpoint returns departures for most of Germany

**Cons**

- VVO's server returns no departures
- Undocumented by VVO, and the DELFI-backed endpoint is undocumented too
- No real-time data for the VVO area on the DELFI-backed endpoint
- No CORS preflight support, so not usable from browsers

**Best for**: Applications that cover more than one German region; use [TRIAS](trias.md) for VVO data

### Transitous

**Pros**

- JSON over plain GET requests
- CORS enabled, usable from browsers
- Trams, buses, S-Bahn, regional and long-distance trains in one API
- Journey planning across Germany and into neighboring countries, with real-time data applied to routing
- Bike sharing, address search and street routing

**Cons**

- Open-source, non-commercial projects only
- Community-run on a best-effort basis
- No service alerts or route change notices for VVO stops
- Delays and scheduled times sometimes differ from the WebAPI's
- Most Dresden stations can only be queried by platform ID or coordinates

**Best for**: Open-source projects that need destinations outside the VVO or real-time-aware routing; use the [WebAPI](webapi.md) for DVB departures

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
