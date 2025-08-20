# VVO TRIAS API Documentation

Base URL: `https://trias.vvo-online.de:9000/middleware/data/trias`

Alternative URL: `https://efa.vvo-online.de:8080/std3/trias`

## Overview

TRIAS (Traveller Realtime Information and Advisory Standard) is VVO's official standards-based XML API. It conforms to the European TRIAS specification and the German VDV 431-2 standard, providing a comprehensive interface for public transport data.

**Key Characteristics:**
- XML-based request/response format
- Follows VDV 431-2 standard (versions 1.1 and 1.2)
- No authentication required for basic access (use `<RequestorRef>OpenService</RequestorRef>`)
- Supports real-time data
- Comprehensive functionality for journey planning, stop information, and departures

## Official Documentation

VVO provides official documentation through:
- **VDV 431-2 Specification**: The complete standard documentation (PDF)
- **XML Schema (XSD)**: Defines the exact structure of requests and responses
- **Contact**: opendata@vvo-online.de for questions or API key requests

The full VDV 431-2 documentation can be obtained from:
- [VDV (Verband Deutscher Verkehrsunternehmen)](https://www.vdv.de/)
- [Saxony Open Data Portal](https://www.opendata.sachsen.de/)

## Basic Request Structure

All TRIAS requests follow this XML structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Trias xmlns="trias" xmlns:siri="http://www.siri.org.uk/siri" version="1.2">
  <ServiceRequest>
    <siri:RequestTimestamp>2024-01-15T10:30:00Z</siri:RequestTimestamp>
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
curl -X POST "https://trias.vvo-online.de:9000/middleware/data/trias" \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<Trias xmlns="trias" xmlns:siri="http://www.siri.org.uk/siri" version="1.2">
  <ServiceRequest>
    <siri:RequestTimestamp>2024-01-15T10:30:00Z</siri:RequestTimestamp>
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

## Response Structure

Responses follow the TRIAS XML schema:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Trias xmlns="trias" version="1.2">
  <ServiceDelivery>
    <siri:ResponseTimestamp>2024-01-15T10:30:05Z</siri:ResponseTimestamp>
    <siri:ProducerRef>EFA10_EFFZ_1</siri:ProducerRef>
    <siri:Status>true</siri:Status>
    <DeliveryPayload>
      <!-- Service-specific response content -->
    </DeliveryPayload>
  </ServiceDelivery>
</Trias>
```

## Error Handling

TRIAS uses standard SIRI error codes:

```xml
<ErrorMessage>
  <ErrorCode>LOCATION_NOT_FOUND</ErrorCode>
  <ErrorText>The requested location could not be found</ErrorText>
</ErrorMessage>
```

Common error codes:
- `LOCATION_NOT_FOUND` - Invalid stop or location reference
- `NO_INFO_FOR_TOPIC` - No data available for request
- `INVALID_REQUEST` - Malformed XML or missing required fields
- `UNKNOWN_REQUESTOR` - Invalid RequestorRef

## Best Practices

1. **Use Official Schema**: Validate requests against the VDV 431-2 XSD
2. **Handle Namespaces**: Properly declare and use XML namespaces
3. **Time Zones**: Use UTC times in requests (Z suffix)
4. **Caching**: Cache location searches and static data
5. **Error Handling**: Parse error responses and handle gracefully
6. **Large Responses**: Responses can be large; use streaming XML parsers

## Advantages of TRIAS

- **Standards Compliance**: Follows European and German standards
- **Comprehensive Data**: Includes all transit data in structured format
- **Real-time Support**: Built-in support for delays and disruptions
- **Extensibility**: Schema allows for vendor extensions
- **Stability**: Official API with formal support

## Client Libraries

Several libraries support TRIAS:
- **Python**: Use general TRIAS/VDV libraries
- **Java**: TRIAS client libraries available on Maven
- **C#/.NET**: XML serialization with TRIAS schema

## Migration from Legacy APIs

When migrating from Widget or WebAPI to TRIAS:
1. Map stop IDs to DHID format
2. Convert JSON date formats to ISO 8601
3. Handle XML namespaces properly
4. Adjust for richer response data structure

## Additional Resources

- [VDV Website](https://www.vdv.de/) - Standards documentation
- [TRIAS Schema Files](https://github.com/VDVde/TRIAS) - XSD definitions
- [OpenService Platform](https://www.openservice-online.de/) - Additional TRIAS documentation
