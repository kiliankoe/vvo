# VVO TRIAS API Documentation

Base URL: `http://efa.vvo-online.de:8080/std3/trias`

## Overview

TRIAS (Traveller Realtime Information and Advisory Standard) is VVO's official standards-based XML API. It conforms to the European TRIAS specification and the German VDV 431-2 standard, providing a comprehensive interface for public transport data.

**Key Characteristics:**

- XML-based request/response format (POST)
- Follows VDV 431-2 standard (versions 1.1 and 1.2)
- No authentication required for basic access (use `<RequestorRef>OpenService</RequestorRef>`)
- Supports real-time data
- Comprehensive functionality for journey planning, stop information, and departures

## Official Documentation

- **VDV 431-2 Specification**: [v1.1](https://www.vdv.de/431-2sds-v1.1.pdfx?forced=true) or [v1.2](https://www.vdv.de/431-2-sdsv1.2.pdfx?forced=false) (PDF)
- **XML Schema (XSD)**: [VDVde/TRIAS](https://github.com/VDVde/TRIAS) on GitHub
- **Contact**: opendata@vvo-online.de for questions or API key requests

## Basic Request Structure

All TRIAS requests follow this XML structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Trias xmlns="trias" xmlns:siri="http://www.siri.org.uk/siri" version="1.2">
  <ServiceRequest>
    <siri:RequestTimestamp>2026-02-20T10:30:00Z</siri:RequestTimestamp>
    <siri:RequestorRef>OpenService</siri:RequestorRef>
    <RequestPayload>
      <!-- Service-specific request content -->
    </RequestPayload>
  </ServiceRequest>
</Trias>
```

**Required Elements:**

- `RequestTimestamp`: ISO 8601 timestamp of the request
- `RequestorRef`: Service identification (use "OpenService" for public access)
- `RequestPayload`: Contains the actual service request

## Main Services

### 1. LocationInformationRequest

Find stops, addresses, or points of interest.

```xml
<RequestPayload>
  <LocationInformationRequest>
    <InitialInput>
      <LocationName>Hauptbahnhof</LocationName>
    </InitialInput>
    <Restrictions>
      <Type>stop</Type>
      <NumberOfResults>10</NumberOfResults>
      <IncludePtModes>true</IncludePtModes>
    </Restrictions>
  </LocationInformationRequest>
</RequestPayload>
```

> **Note**: Some stop names may require a city prefix to return results. For example, "Postplatz" alone returns no results while "Dresden Postplatz" works. "Hauptbahnhof" works without prefix (defaults to Dresden context).

**Features:**

- Text-based location search
- Coordinate-based search
- Filter by location type (stop, address, POI)
- Configurable result limits

### 2. StopEventRequest

Get departure or arrival information for stops.

```xml
<RequestPayload>
  <StopEventRequest>
    <Location>
      <LocationRef>
        <StopPointRef>de:14612:28</StopPointRef>
      </LocationRef>
    </Location>
    <Params>
      <NumberOfResults>10</NumberOfResults>
      <StopEventType>departure</StopEventType>
      <IncludeRealtimeData>true</IncludeRealtimeData>
      <IncludeOperatingDays>false</IncludeOperatingDays>
    </Params>
  </StopEventRequest>
</RequestPayload>
```

**Features:**

- Real-time departure/arrival boards
- Filter by time window
- Filter by transport modes
- Include service alerts and disruptions

### 3. TripRequest

Plan journeys between locations.

```xml
<RequestPayload>
  <TripRequest>
    <Origin>
      <LocationRef>
        <StopPointRef>de:14612:28</StopPointRef>
      </LocationRef>
    </Origin>
    <Destination>
      <LocationRef>
        <StopPointRef>de:14612:201</StopPointRef>
      </LocationRef>
    </Destination>
    <Params>
      <NumberOfResults>5</NumberOfResults>
      <IncludeTrackSections>true</IncludeTrackSections>
      <IncludeIntermediateStops>true</IncludeIntermediateStops>
      <IncludeFares>false</IncludeFares>
    </Params>
  </TripRequest>
</RequestPayload>
```

**Features:**

- Intermodal journey planning
- Multiple algorithm options:
  - `fastest` - Minimize travel time
  - `minChanges` - Minimize transfers
  - `leastWalking` - Minimize walking distance
  - `leastCost` - Minimize fare cost
- Accessibility options:
  - `NoSingleStep`
  - `NoStairs`
  - `NoEscalator`
  - `NoElevator`
- Time-based search (departure or arrival)

## Example: Complete Stop Departure Request

```bash
curl -X POST "http://efa.vvo-online.de:8080/std3/trias" \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<Trias xmlns="trias" xmlns:siri="http://www.siri.org.uk/siri" version="1.2">
  <ServiceRequest>
    <siri:RequestTimestamp>2026-02-20T10:30:00Z</siri:RequestTimestamp>
    <siri:RequestorRef>OpenService</siri:RequestorRef>
    <RequestPayload>
      <StopEventRequest>
        <Location>
          <LocationRef>
            <StopPointRef>de:14612:28</StopPointRef>
          </LocationRef>
        </Location>
        <Params>
          <NumberOfResults>5</NumberOfResults>
          <StopEventType>departure</StopEventType>
          <IncludeRealtimeData>true</IncludeRealtimeData>
        </Params>
      </StopEventRequest>
    </RequestPayload>
  </ServiceRequest>
</Trias>'
```

## Stop ID Format

TRIAS uses DHID (Deutsche Haltestellen-ID) format for stop references:

- Format: `de:DISTRICT:STOPID`
- Example: `de:14612:28` (Dresden Hauptbahnhof)
- District 14612 = Dresden
- Platform-level refs add `:AREA:PLATFORM`, e.g. `de:14612:28:2:4`

## Response Structure

Responses follow the TRIAS XML schema with namespaced elements:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<trias:Trias xmlns:siri="http://www.siri.org.uk/siri"
             xmlns:trias="http://www.vdv.de/trias" version="1.2">
  <trias:ServiceDelivery>
    <siri:ResponseTimestamp>2026-02-20T10:30:05Z</siri:ResponseTimestamp>
    <siri:ProducerRef>DELIVVO2019</siri:ProducerRef>
    <siri:Status>true</siri:Status>
    <trias:DeliveryPayload>
      <!-- Service-specific response content -->
    </trias:DeliveryPayload>
  </trias:ServiceDelivery>
</trias:Trias>
```

## Error Handling

Errors are returned inside the `DeliveryPayload`:

```xml
<trias:LocationInformationResponse>
  <trias:ErrorMessage>
    <trias:Code>-8014</trias:Code>
    <trias:Text>
      <trias:Text>LOCATION_NORESULTS</trias:Text>
      <trias:Language>de</trias:Language>
    </trias:Text>
  </trias:ErrorMessage>
</trias:LocationInformationResponse>
```

## Additional Resources

- [VDV Website](https://www.vdv.de/) - Standards documentation
- [TRIAS Schema Files](https://github.com/VDVde/TRIAS) - XSD definitions
