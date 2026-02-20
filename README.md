# 🚏VVO

This is a comprehensive list of API endpoints, libraries, apps, tools and resources for accessing public transportation data in the [Verkehrsverbund Oberelbe](https://www.vvo-online.de/de) (VVO) network, which includes the [Dresdner Verkehrsbetriebe](https://www.dvb.de/de-de/) (DVB).

This repository serves as the primary community resource for Dresden transit API documentation, containing reverse-engineered specifications, links to client libraries, and a comprehensive ecosystem overview.

This document is inspired by [derhuerst/vbb-modules](https://github.com/derhuerst/vbb-modules).

Got any more info, details, links? Please don't hesitate to open an issue and/or PR!

![DVB transit map](./data/liniennetzplan.jpg)

## Documentation Overview

- **[API Comparison Guide](documentation/api-comparison.md)** - Feature matrix and selection guide for choosing the right API
- **[Widget API](documentation/widgets.md)** - Simple GET-based API for departure monitors
- **[WebAPI](documentation/webapi.md)** - JSON REST API used by mobile apps
- **[TRIAS API](documentation/trias.md)** - Official XML-based API following European standards
- **[GTFS Data](documentation/gtfs.md)** - Standard transit data format with static and real-time feeds
- **[Dresden OpenData](documentation/opendata.md)** - Geographic transit datasets via OGC API Features (lines, stops, accessibility)

## Legal Information

**EU Open Data Requirements**: Under EU Regulation 2017/1926, transit data must be made available in machine-readable formats. VVO complies through various APIs and data formats.

**Usage Terms**:

- **Widget API**: Non-commercial use only, fair use policy applies
- **WebAPI**: No official terms, use respectfully
- **TRIAS**: Official API, commercial use allowed with agreement

For commercial applications or high-volume usage, contact VVO at opendata@vvo-online.de.

## Static Data

- [`stations.json`](https://raw.githubusercontent.com/kiliankoe/vvo/master/data/stations.json) - Complete station data with metadata and transit lines
- [`stations.geojson`](https://raw.githubusercontent.com/kiliankoe/vvo/master/data/stations.geojson) - All stations as GeoJSON for mapping applications
- [`stations.csv`](https://raw.githubusercontent.com/kiliankoe/vvo/master/data/stations.csv) - Tabular list of all stations with coordinates and operators
- [`stations_summary.md`](https://raw.githubusercontent.com/kiliankoe/vvo/master/data/stations_summary.md) - Statistics and summary of the VVO network
- [`abbreviations_dresden.csv`](https://raw.githubusercontent.com/kiliankoe/vvo/master/data/abbreviations_dresden.csv) - Station abbreviations in Dresden
- [`abbreviations_regional.csv`](https://raw.githubusercontent.com/kiliankoe/vvo/master/data/abbreviations_regional.csv) - Station abbreviations in surrounding areas
- [`liniennetzplan.jpg`](https://raw.githubusercontent.com/kiliankoe/vvo/master/data/liniennetzplan.jpg) - Current DVB standard network map (JPEG)
- [`liniennetzplan.pdf`](https://raw.githubusercontent.com/kiliankoe/vvo/master/data/liniennetzplan.pdf) - Current DVB standard network map (PDF)
- [`VVO_STOPS.JSON`](https://www.vvo-online.de/open_data/VVO_STOPS.JSON) - Official daily updated station data (external)

## APIs

### Open Access APIs

- **[TRIAS API](documentation/trias.md)** - `http://efa.vvo-online.de:8080/std3/trias`
  - **Official** XML-based API following VDV 431-2 standard
  - Comprehensive features: journey planning, real-time departures, stop search
  - No authentication required (use RequestorRef: "OpenService")
  - [VDV Standard v1.1](https://www.vdv.de/431-2sds-v1.1.pdfx?forced=true) or [v1.2](https://www.vdv.de/431-2-sdsv1.2.pdfx?forced=false)

- **[Widget API](documentation/widgets.md)** - `http://widgets.vvo-online.de`
  - Simple GET-based API for departure monitors
  - Lightweight JSON responses
  - ⚠️ Non-commercial use only
  - [Documentation](documentation/widgets.md) (reverse-engineered)

- **[WebAPI](documentation/webapi.md)** - `https://webapi.vvo-online.de`
  - JSON REST API used by mobile apps
  - Real-time data with delays, platform info, and occupancy levels
  - Map pins, tariff zone polygons, trip PDF export
  - Comprehensive but unofficial
  - [Documentation](documentation/webapi.md) (reverse-engineered)

- **[EFA Classic](http://efa.vvo-online.de:8080)** - `http://efa.vvo-online.de:8080`
  - Legacy XML trip planning interface
  - Being superseded by TRIAS
  - No public documentation

### Restricted Access APIs

- **[DVB WebDFI](http://dfi.dvb.de/)** - `http://dfi.dvb.de/`
  - Digital departure display interface
  - Requires registration with DVB
  - For business customers only
  - See [#3](https://github.com/kiliankoe/vvo/issues/3) for details

- **[DVB Maps API](https://www.dvb.de/apps/map/)**
  - POI search and reverse geocoding
  - Internal API, not publicly accessible
  - No documentation available

### Data Downloads

- **[GTFS Feeds](documentation/gtfs.md)**
  - Static: Daily updated schedule data
  - Real-time: Trip updates and service alerts (via GTFS-RT)
  - Standard format compatible with many tools

- **[Dresden OpenData Portal](documentation/opendata.md)** - `https://kommisdd.dresden.de/net4/public/ogcapi/`
  - Geographic data: Line routes, stop locations, infrastructure
  - Accessibility information: Platform heights, tactile paving
  - OGC API Features standard (GeoJSON/JSON)
  - Open Data License, commercial use allowed

## Libraries

Client libraries for various languages, sorted in no particular order. Although some of the names are specific to the DVB, most if not all of them are compatible with everything in the VVO network.

- **Node.js**: [`dvbjs`](https://github.com/kiliankoe/dvbjs) - WebAPI client with TypeScript support
- **Python**: [`dvbpy`](https://github.com/kiliankoe/dvbpy) - Pythonic WebAPI wrapper
- **Haskell**: [`dresdner-verkehrsbetriebe`](https://github.com/offenesdresden/dresdner-verkehrsbetriebe) - Widget API client
- **Swift**: [`DVB`](https://github.com/kiliankoe/DVB) - iOS/macOS client for WebAPI
- **Java**: [`jVVO`](https://github.com/PhilippMatthes/jVVO) - WebAPI client for JVM
- **Ruby**: [`dvbrb`](https://github.com/kiliankoe/dvbrb) - Supports both APIs
- **Go**: [`dvbgo`](https://github.com/kiliankoe/dvbgo) - WebAPI client
- **Rust**: [`dvb-rs`](https://github.com/hoodie/dvb-rs) - WebAPI client

### Other

- [TripKit/VvoProvider](https://github.com/alexander-albers/tripkit/blob/main/Sources/TripKit/Provider/Implementations/VvoProvider.swift) - Part of TripKit, a Swift port of [schildbach/public-transport-enabler](https://github.com/schildbach/public-transport-enabler) for the iOS app [ÖPNV Navigator](http://navigatorapp.net)

## Apps

Mobile apps known and used in Dresden.

- [`DVB mobil`](https://www.dvb.de/de-de/fahrplan/dvb-mobil/) - Official, cross-platform
- [`ÖPNV Navigator`](https://itunes.apple.com/de/app/öpnv-navigator/id1239908782?mt=8) - iOS, not specific to the VVO network
- [`Öffi`](https://f-droid.org/packages/de.schildbach.oeffi/) - Android
- [`Haltestellenmonitor-v3`](https://github.com/HanashiDev/Haltestellenmonitor-v3) - iOS

### Assistive apps & accessibility

- [`DVBerry`](https://github.com/Julius-Babies/JH_DVBerry) - a Kotlin app that reads out departures for nearby VVO stops for blind and visually impaired users

### Deprecated

- [`Manni`](https://github.com/manni-app/manni-ios) - iOS (no longer on App Store, repository archived)
- [`DVB-Verspaetungen`](https://github.com/alexander-fischer/DVB-Verspaetungen) - Android app informing you about the current delay situation (repository archived)
- `FahrInfo Dresden` - cross-platform (removed from public stores)
- `Faplino` - Android (removed from Play Store in July 2022)

## Tools, UIs & Experiments

- [`Home Assistant Integration`](https://github.com/VDenisyuk/home-assistant-transport) - Show current departure data for selected stop on Home Assistant Dashboard
- [`Magic Mirror`](https://web.archive.org/web/20180422030559/http://blog.thomas-bachmann.com/2016/02/magic-mirror-2-0-mit-gestensteuerung.html) - Shows current departure data (using [`dvbpy`](https://github.com/kiliankoe/dvbpy))
- [`alfred_dvb`](https://github.com/kiliankoe/alfred_dvb) - [Alfred](https://www.alfredapp.com) workflow for departure data (using [`dvbgo`](https://github.com/kiliankoe/dvbgo))
- [`Amazon Echo`](https://twitter.com/ubahnverleih/status/830079491523358721) - Tweet [@ubahnverleih](https://twitter.com/ubahnverleih) for more info
- [`catch-my-bus`](https://github.com/hoodie/catch-my-bus) - ruby script notifying you about your next bus
- [`catch-my-bus-python`](https://github.com/meepoSenpai/catch-my-bus-python) - GTK3 StatusIcon showing current departure data
- [`DVBot`](https://www.messenger.com/t/dvbot) - DVB Facebook Messenger Bot
- [`ddplan`](https://github.com/4gray/ddplan) - Electron based station monitor that lives in the menubar
- [`Abfahrtsmonitor`](https://github.com/HeEAaD/Abfahrtsmonitor) - Departure board for your Apple Watch
- [`hubot-dvb`](https://github.com/kiliankoe/hubot-dvb) - [Hubot](https://hubot.github.com) script (using [`dvbjs`](https://github.com/kiliankoe/dvbjs))
- [`dresden-departure-monitor`](https://github.com/don-philipe/dresden-departure-monitor) - Bashscript for getting current departure times
- [`AbfahrtsTV`](https://github.com/kiliankoe/AbfahrtsTV) - Current departure times on your AppleTV, 'cause why not
- [`DVBManniBot`](https://github.com/freakyblue/DVBManniBot) - Telegram bot for checking current departures
- [`Verkehrsbot`](https://github.com/dirkonet/verkehrsbot) - another Telegram bot for checking current departures (using [`dvbpy`](https://github.com/kiliankoe/dvbpy))
- [`Dresden Bot`](https://github.com/rtwalz/dresden) - Feature rich Telegram bot with routing, maps, departures and a lot more
- [`dvb-on-esp32`](https://github.com/andiikaa/dvb-on-esp32) - Current depature times on lcd via ESP32 (Arduino)
- [`dvb-browser`](https://github.com/pabra/dvb-browser) - Vue.js (mobile) browser app showing real time departures really fast
- [`oepnvdresdenbot`](https://t.me/oepnvdresdenbot) - Telegram bot featuring natural language queries for departures and routes
- [`ARKit Abfahrtsmonitor`](https://chaos.social/@kilian/115061882525155413) - iOS ARKit demo showing departure information
- [`Departure Shortcut`](https://github.com/kiliankoe/shortcuts#dvb-abfahrten) - Shortcut for iOS' Shortcuts app showing departures
- [`dvb-mqtt`](https://github.com/seb-daehne/dvb-mqtt) - Periodically publish departure data to an mqtt broker
- [`dvblive`](https://github.com/Tiffel/dvblive) - Visualization of tram delays for the entire city ([#odcdresden19](http://dresden.de/odcdresden19) project, no longer actively maintained)
- [`VV...Wo?`](https://github.com/kiliankoe/vvwo) - iOS app using natural language queries ([#odcdresden19](http://dresden.de/odcdresden19) project)
- [`DVBFast`](https://github.com/lucasvog/dvbfast) - WebApp that displays the departure infos of the nearest stations using GPS ([live Version](https://dvbfast.github.io/))
- [`MMM-DVB`](https://github.com/skastenholz/MMM-DVB) - MagicMirror² module
- [`vvo-departures-cli`](https://aur.archlinux.org/packages/vvo-departures-cli) - CLI for querying departures information, also see [#32](https://github.com/kiliankoe/vvo/issues/32)
- [`wartefrei`](https://github.com/Nichtmetall/wartefrei) - web-based realtime dashboard for departures and routes
- [`dvb-mcp`](https://github.com/hoodie/dvb-mcp) - mcp-server
