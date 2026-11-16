# OJP API Documentation

Base URL: `https://efa.vvo-online.de/std3/ojp`

## Overview

OJP (Open Journey Planner) is the European standard for linking journey planners across regions and countries, specified as CEN/TS 17118. It extends TRIAS and offers the same core services: stop search, departure boards and journey planning. EU Regulation 2017/1926 asks member states to link their existing journey planners, and OJP is the standard used for that. In Germany, DELFI e.V. is responsible for the national OJP service.

**Key Characteristics:**

- XML-based request/response format (POST), OJP version 1.0. Requests with `version="2.0"` are rejected with HTTP 400
- No authentication required for basic access (use `<RequestorRef>OpenService</RequestorRef>`)
- Also reachable over plain HTTP at `http://efa.vvo-online.de:8080/std3/ojp`. HTTPS on port 8080 does not work
- Requests must use `Content-Type: application/xml` or `text/xml` (`text/plain` is rejected with HTTP 400)
- Not usable from browsers, because the server answers CORS preflight (`OPTIONS`) requests with HTTP 501
- Not officially documented by VVO. For VVO data, [TRIAS](trias.md) on the same server is the better-supported choice

## Endpoints

| Endpoint | Coverage | Stop search | Departures | Trips | Real-time |
| --- | --- | --- | --- | --- | --- |
| `https://efa.vvo-online.de/std3/ojp` | VVO | ✔︎ | ❌ always `STOPEVENT_NOEVENTFOUND` | ✔︎ | ✔︎ (trips) |
| `https://efa.vrr.de/std3/ojp` | Most of Germany (DELFI data) | ✔︎ | ✔︎ except Bavaria and Baden-Württemberg | ✔︎ | Only seen for NRW stops |

VVO's server answers every `OJPStopEventRequest` with `STOPEVENT_NOEVENTFOUND`, whatever the stop or ID format. The same request returns departures from the VRR server, so the request format is not the cause. Use [TRIAS](trias.md) `StopEventRequest` for VVO departures instead.

The VRR server reports `EFA-X-DELFI` as its producer and returns departures for stops across Germany, including Dresden, Leipzig, Berlin and Hamburg. Stops in Bavaria and Baden-Württemberg return `STOPEVENT_NOEVENTFOUND`. Real-time estimates (`EstimatedTime`) appeared only for stops in North Rhine-Westphalia. Dresden departures and trips come with timetabled times only. The server is not documented by VRR or DELFI, so it may change or disappear without notice.

## Official Documentation

- **Schemas (XSD)**: [VDVde/OJP](https://github.com/VDVde/OJP) on GitHub, tag `v1.0.3` for the version these servers speak
- **DELFI**: [Open Journey Planner](https://www.delfi.de/de/forschung-entwicklung/open-journey-planner-ojp/), on DELFI's role in Germany. Its download is a 2017 CEN working draft of the specification
- **Examples**: The Swiss [OJP cookbook](https://opentransportdata.swiss/en/cookbook/open-journey-planner-ojp-landing-page/) shows complete requests and responses for every service

## Basic Request Structure

Unlike TRIAS, the root `OJP` element and the `ServiceRequest` wrapper are in the SIRI namespace. Only the service payload uses the OJP namespace:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<OJP xmlns="http://www.siri.org.uk/siri" xmlns:ojp="http://www.vdv.de/ojp" version="1.0">
  <OJPRequest>
    <ServiceRequest>
      <RequestTimestamp>2026-11-16T10:30:00Z</RequestTimestamp>
      <RequestorRef>OpenService</RequestorRef>
      <!-- Service-specific request, e.g. ojp:OJPStopEventRequest -->
    </ServiceRequest>
  </OJPRequest>
</OJP>
```

Each service request carries its own `RequestTimestamp` in the SIRI namespace as its first child.

The servers do not validate requests against the schema. Elements in the wrong namespace are ignored silently, so a stop search with a misplaced `LocationName` returns unrelated stops instead of an error. If results look arbitrary, check the namespaces first.

## Main Services

### 1. OJPLocationInformationRequest

Find stops, addresses, or points of interest.

```xml
<ojp:OJPLocationInformationRequest>
  <RequestTimestamp>2026-11-16T10:30:00Z</RequestTimestamp>
  <ojp:InitialInput>
    <ojp:LocationName>Dresden Postplatz</ojp:LocationName>
  </ojp:InitialInput>
  <ojp:Restrictions>
    <ojp:Type>stop</ojp:Type>
    <ojp:NumberOfResults>5</ojp:NumberOfResults>
  </ojp:Restrictions>
</ojp:OJPLocationInformationRequest>
```

Stops come back as `ojp:StopPlace` with an `ojp:StopPlaceRef` such as `de:14612:28`.

### 2. OJPStopEventRequest

Get departure or arrival information for a stop. Send this to the VRR server, see [Endpoints](#endpoints).

```xml
<ojp:OJPStopEventRequest>
  <RequestTimestamp>2026-11-16T10:30:00Z</RequestTimestamp>
  <ojp:Location>
    <ojp:PlaceRef>
      <ojp:StopPlaceRef>de:14612:28</ojp:StopPlaceRef>
      <ojp:LocationName><ojp:Text>Dresden Hauptbahnhof</ojp:Text></ojp:LocationName>
    </ojp:PlaceRef>
  </ojp:Location>
  <ojp:Params>
    <ojp:NumberOfResults>5</ojp:NumberOfResults>
    <ojp:StopEventType>departure</ojp:StopEventType>
    <ojp:IncludeRealtimeData>true</ojp:IncludeRealtimeData>
  </ojp:Params>
</ojp:OJPStopEventRequest>
```

Without `ojp:DepArrTime` after the `ojp:PlaceRef`, the board starts at the current time. `ojp:StopEventType` also accepts `arrival` and `both`.

### 3. OJPTripRequest

Plan journeys between locations.

```xml
<ojp:OJPTripRequest>
  <RequestTimestamp>2026-11-16T10:30:00Z</RequestTimestamp>
  <ojp:Origin>
    <ojp:PlaceRef>
      <ojp:StopPlaceRef>de:14612:28</ojp:StopPlaceRef>
      <ojp:LocationName><ojp:Text>Dresden Hauptbahnhof</ojp:Text></ojp:LocationName>
    </ojp:PlaceRef>
  </ojp:Origin>
  <ojp:Destination>
    <ojp:PlaceRef>
      <ojp:StopPlaceRef>de:14612:13</ojp:StopPlaceRef>
      <ojp:LocationName><ojp:Text>Dresden Albertplatz</ojp:Text></ojp:LocationName>
    </ojp:PlaceRef>
  </ojp:Destination>
  <ojp:Params>
    <ojp:NumberOfResults>3</ojp:NumberOfResults>
    <ojp:IncludeIntermediateStops>true</ojp:IncludeIntermediateStops>
  </ojp:Params>
</ojp:OJPTripRequest>
```

## Example: Complete Departure Request

```bash
curl -X POST "https://efa.vrr.de/std3/ojp" \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<OJP xmlns="http://www.siri.org.uk/siri" xmlns:ojp="http://www.vdv.de/ojp" version="1.0">
  <OJPRequest>
    <ServiceRequest>
      <RequestTimestamp>2026-11-16T10:30:00Z</RequestTimestamp>
      <RequestorRef>OpenService</RequestorRef>
      <ojp:OJPStopEventRequest>
        <RequestTimestamp>2026-11-16T10:30:00Z</RequestTimestamp>
        <ojp:Location>
          <ojp:PlaceRef>
            <ojp:StopPlaceRef>de:14612:28</ojp:StopPlaceRef>
            <ojp:LocationName><ojp:Text>Dresden Hauptbahnhof</ojp:Text></ojp:LocationName>
          </ojp:PlaceRef>
        </ojp:Location>
        <ojp:Params>
          <ojp:NumberOfResults>5</ojp:NumberOfResults>
          <ojp:StopEventType>departure</ojp:StopEventType>
          <ojp:IncludeRealtimeData>true</ojp:IncludeRealtimeData>
        </ojp:Params>
      </ojp:OJPStopEventRequest>
    </ServiceRequest>
  </OJPRequest>
</OJP>'
```

## Stop ID Format

OJP uses the same DHID (Deutsche Haltestellen-ID) format as [TRIAS](trias.md#stop-id-format). Stops are `ojp:StopPlaceRef` (`de:14612:28`). Platforms are `siri:StopPointRef` (`de:14612:28:19:5`) and carry an `ojp:ParentRef` to their stop. A few stops, mostly outside Dresden, come back with numeric IDs instead of DHIDs.

## Response Structure

Responses are sent as `text/xml`. The envelope is in the SIRI namespace and each service delivery in the OJP namespace:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<siri:OJP xmlns:siri="http://www.siri.org.uk/siri" xmlns:ojp="http://www.vdv.de/ojp" version="1.0">
  <siri:OJPResponse>
    <siri:ServiceDelivery>
      <siri:ResponseTimestamp>2026-11-16T10:30:05Z</siri:ResponseTimestamp>
      <siri:ProducerRef>EFAController10.6.34.3-EFA-X-DELFI13</siri:ProducerRef>
      <siri:Status>true</siri:Status>
      <ojp:OJPStopEventDelivery>
        <!-- ojp:StopEventResponseContext with all referenced places, then one
             ojp:StopEventResult per departure -->
      </ojp:OJPStopEventDelivery>
    </siri:ServiceDelivery>
  </siri:OJPResponse>
</siri:OJP>
```

Times are in UTC. `ojp:TimetabledTime` is the scheduled time, and `ojp:EstimatedTime` the real-time estimate where one exists.

## Error Handling

Errors in the request content are returned with HTTP 200. The service delivery then has `siri:Status` `false` and a `siri:ErrorCondition`:

```xml
<ojp:OJPStopEventDelivery>
  <siri:ResponseTimestamp>2026-11-16T10:30:05Z</siri:ResponseTimestamp>
  <siri:Status>false</siri:Status>
  <siri:ErrorCondition>
    <siri:NoInfoForTopicError number="0">
      <siri:ErrorText>STOPEVENT_NOEVENTFOUND</siri:ErrorText>
    </siri:NoInfoForTopicError>
    <siri:Description>STOPEVENT_NOEVENTFOUND</siri:Description>
  </siri:ErrorCondition>
</ojp:OJPStopEventDelivery>
```

Malformed XML and OJP 2.0 requests result in HTTP 400 with an HTML body.
