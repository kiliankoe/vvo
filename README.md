# 🚏VVO

This is a list of API endpoints, libraries, apps, tools and anything else that's available to access data in the [Verkehrsverbund Oberelbe](https://www.vvo-online.de/de) network. This includes the [Dresdner Verkehrsbetriebe](https://www.dvb.de/de-de/).

This document is inspired by [derhuerst/vbb-modules](https://github.com/derhuerst/vbb-modules).

Got any more info, details, links? Please don't hesitate to open an issue and/or PR 🙃



## Static Data

- [`stations.csv`](https://raw.githubusercontent.com/kiliankoe/vvo/master/stations.csv) - A list of all stations including coordinates.




## APIs

- [`Widgets`](http://widgets.vvo-online.de)
  - For the [VVO widgets](https://www.vvo-online.de/de/service/widgets/index.cshtml)
  - No known official documentation
  - See [Wiki](https://github.com/kiliankoe/vvo/wiki/Widgets) for reverse-engineered docs
- [`WebAPI`](https://webapi.vvo-online.de)
  - New API used by the mobile page (and therefore the official app)
  - No known official documentation
  - See [Wiki](https://github.com/kiliankoe/vvo/wiki/WebAPI) for reverse-engineered docs
- [`EFA`](http://efa.vvo-online.de:8080)
  - "Classic" interface for trip requests
  - No known (public) documentation ([yet?](https://github.com/kiliankoe/vvo/wiki))
- [`Trias`](http://trias.vvo-online.de:9000/middleware/data/trias)
  - Brand new and still in the process of being implemented afaik
  - "Documentation" [here](https://www.vdv.de/431-2sds-v1.1.pdfx?forced=true)
- [`DVB WebDFI`](http://dfi.dvb.de/)
  - Closed access
  - For web-based [departure monitors](https://www.dvb.de/de-de/service/geschaeftskunden/abfahrtsmonitor/)
  - See [#3](https://github.com/kiliankoe/vvo/issues/3) for some more information
  - No known (public) documentation ([yet?](https://github.com/kiliankoe/vvo/wiki))
- [`DVB Maps App`](https://www.dvb.de/apps/map/)
  - POI search and reverse geocoding
  - No known (public) documentation ([yet?](https://github.com/kiliankoe/vvo/wiki))



## Libraries

Client libraries for various languages, sorted in no particular order. Although the names are specific to the DVB, most if not all of them are compatible with everything in the VVO network.

- [`dvbjs`](https://github.com/kiliankoe/dvbjs) - Client library for Node.js
- [`dvbpy`](https://github.com/kiliankoe/dvbpy) - Client library for Python
- [`dresdner-verkehrsbetriebe`](https://github.com/offenesdresden/dresdner-verkehrsbetriebe) - Client library for Haskell
- [`DVB`](https://github.com/kiliankoe/DVB) - Client library for Swift
- [`dvbrb`](https://github.com/kiliankoe/dvbrb) - Client library for Ruby
- [`dvbgo`](https://github.com/kiliankoe/dvbgo) - Client library for Go
- [`dvb-rs`](https://github.com/hoodie/dvb-rs) - Client library for Rust


To make it more obvious which lib support which features, here's a nifty table.

|                       | JavaScript | Python  | Haskell | Swift | Ruby |  Go  | Rust |
| --------------------- | :--------: | :-----: | :-----: | :---: | :--: | :--: | :--: |
| Find stops via name   |     ✅      |    ✅    |         |   ✅   |  ✅   |      |  ✅   |
| Find stops via coords |     ✅      |    ✅    |         |   ✅   |      |      |      |
| Departure Monitor     |     ✅      |    ✅    |    ✅    |   ✅   |  ✅   |  ✅   |  ✅   |
| Routing               |     ✅      |    ✅    |    ✅    |   ✅   |      |      |      |
| Reverse Geocoding     |     ✅      |    ✅    |         |   ✅   |      |      |      |
| POI Search            |     ✅      |    ✅    |         |       |      |      |      |
| Route Changes         |            |         |         |   ✅   |      |      |      |
| Supported Lines       |            |         |         |   ✅   |      |      |      |
| Route Map Location    |            |         |         |        |      |      |      |
| Used API              |  A, E, D   | W, E, D |  W, E   |   A   |  W   |  W   |  W   |

W: Widgets, E: EFA, A: WebAPI, D: DVBApps



## Apps

Mobile apps known and used in Dresden.

- [`DVB mobil`](https://www.dvb.de/de-de/fahrplan/dvb-mobil/) - Official, cross-platform
- [`Faplino`](https://play.google.com/store/apps/details?id=de.faplino) - Android
- [`FahrInfo Dresden`](https://itunes.apple.com/de/app/fahrinfo-dresden/id314790387?mt=8) - cross-platform
- [`Öffi`](https://play.google.com/store/apps/details?id=de.schildbach.oeffi) - Android
- [`DVB-Verspaetungen`](https://github.com/alexander-fischer/DVB-Verspaetungen) - Android app informing you about the current delay situation



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
