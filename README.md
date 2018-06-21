# 🚏VVO

This is a list of API endpoints, libraries, apps, tools and anything else that's available to access data in the [Verkehrsverbund Oberelbe](https://www.vvo-online.de/de) network. This includes the [Dresdner Verkehrsbetriebe](https://www.dvb.de/de-de/).

This document is inspired by [derhuerst/vbb-modules](https://github.com/derhuerst/vbb-modules).

Got any more info, details, links? Please don't hesitate to open an issue and/or PR 🙃



## Static Data

- [`stations.csv`](https://raw.githubusercontent.com/kiliankoe/vvo/master/stations.csv) - A list of all stations including coordinates.
- [`kuerzel_dresden.csv`](https://raw.githubusercontent.com/kiliankoe/vvo/master/kuerzel/kuerzel_dresden.csv) - A list of station abbreviations in Dresden
- [`kuerzel_umland.csv`](https://raw.githubusercontent.com/kiliankoe/vvo/master/kuerzel/kuerzel_umland.csv) - A list of station abbreviations around Dresden




## APIs

- [`Widgets`](http://widgets.vvo-online.de)
  - For the [VVO widgets](https://www.vvo-online.de/de/service/widgets/index.cshtml)
  - No known official documentation
  - See [documentation/widgets](https://github.com/kiliankoe/vvo/blob/master/documentation/widgets.md) for reverse-engineered docs
- [`WebAPI`](https://webapi.vvo-online.de)
  - New API used by the mobile page (and therefore the official app)
  - No known official documentation
  - See [documentation/webapi](https://github.com/kiliankoe/vvo/blob/master/documentation/webapi.md) for reverse-engineered docs
- [`EFA`](http://efa.vvo-online.de:8080)
  - "Classic" interface for trip requests
  - No known (public) documentation (yet?)
- [`Trias`](http://trias.vvo-online.de:9000/middleware/data/trias)
  - Brand new and still in the process of being implemented afaik
  - "Documentation" [here](https://www.vdv.de/431-2sds-v1.1.pdfx?forced=true)
- [`DVB WebDFI`](http://dfi.dvb.de/)
  - Closed access
  - For web-based [departure monitors](https://www.dvb.de/de-de/service/geschaeftskunden/abfahrtsmonitor/)
  - See [#3](https://github.com/kiliankoe/vvo/issues/3) for some more information
  - No known (public) documentation (yet?)
- [`DVB Maps App`](https://www.dvb.de/apps/map/)
  - POI search and reverse geocoding
  - No known (public) documentation (yet?)



## Libraries

Client libraries for various languages, sorted in no particular order. Although the names are specific to the DVB, most if not all of them are compatible with everything in the VVO network.

- Node.js: [`dvbjs`](https://github.com/kiliankoe/dvbjs)
- Python: [`dvbpy`](https://github.com/kiliankoe/dvbpy)
- Haskell: [`dresdner-verkehrsbetriebe`](https://github.com/offenesdresden/dresdner-verkehrsbetriebe)
- Swift: [`DVB`](https://github.com/kiliankoe/DVB)
- Java: [`jVVO`](https://github.com/PhilippMatthes/jVVO)
- Ruby: [`dvbrb`](https://github.com/kiliankoe/dvbrb)
- Go: [`dvbgo`](https://github.com/kiliankoe/dvbgo)
- Rust: [`dvb-rs`](https://github.com/hoodie/dvb-rs)


To make it more obvious which lib support which features, here's a nifty table.

|                       | JavaScript | Python  | Haskell | Swift | Java | Ruby |  Go  | Rust |
| --------------------- | :--------: | :-----: | :-----: | :---: | :--: | :--: | :--: | :--: |
| Find stops via name   |     ✅      |    ✅    |         |   ✅   |   ✅  |  ✅   |      |  ✅   |
| Find stops via coords |     ✅      |    ✅    |         |   ✅   |   ✅  |      |      |      |
| Departure Monitor     |     ✅      |    ✅    |    ✅    |   ✅   |   ✅  |  ✅   |  ✅   |  ✅   |
| Routing               |     ✅      |    ✅    |    ✅    |   ✅   |   ✅  |      |      |      |
| Reverse Geocoding     |     ✅      |    ✅    |         |   ✅   |     |      |      |      |
| POI Search            |     ✅      |    ✅    |         |       |      |      |      |      |
| Route Changes         |            |         |         |   ✅   |   ✅  |      |      |      |
| Supported Lines       |            |         |         |   ✅   |   ✅  |      |      |      |
| Route Map Location    |            |         |         |        |      |      |      |      |
| Used API              |  A, E, D   | W, E, D |  W, E   |   A   |   A   |  W   |  W   |  W   |

W: Widgets, E: EFA, A: WebAPI, D: DVBApps



## Apps

Mobile apps known and used in Dresden.

- [`DVB mobil`](https://www.dvb.de/de-de/fahrplan/dvb-mobil/) - Official, cross-platform
- [`Faplino`](https://play.google.com/store/apps/details?id=de.faplino) - Android
- [`FahrInfo Dresden`](https://itunes.apple.com/de/app/fahrinfo-dresden/id314790387?mt=8) - cross-platform
- [`Öffi`](https://play.google.com/store/apps/details?id=de.schildbach.oeffi) - Android
- [`DVB-Verspaetungen`](https://github.com/alexander-fischer/DVB-Verspaetungen) - Android app informing you about the current delay situation
- [`Manni`](https://itunes.apple.com/us/app/manni/id1347527695?l=de&ls=1&mt=8) - iOS app to find the current location of your upcoming departure



## Tools, UIs & Experiments

- [`Magic Mirror`](http://blog.thomas-bachmann.com/2016/02/magic-mirror-2-0-mit-gestensteuerung.html) - Shows current departure data (using [`dvbpy`](https://github.com/kiliankoe/dvbpy))
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
- [`dvb-on-esp32`](https://github.com/andiikaa/dvb-on-esp32) - Current depature times on lcd via ESP32 (Arduino)
- [`dvb-browser`](https://github.com/pabra/dvb-browser) - Vue.js (mobile) browser app showing real time departures really fast
- [`oepnvdresdenbot`](https://t.me/oepnvdresdenbot) - Telegram bot featuring natural language queries for departures and routes
- [`ARKit Abfahrtsmonitor`](https://twitter.com/kiliankoe/status/1009788336976908289) - iOS ARKit demo showing departure information
