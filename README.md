# haproxy-top
CLI tool for viewing real-time HAProxy metrics across multiple instances

## Installing

```bash
pip install haproxy-top
```

## Usage

Simply start haproxy-top with the stat socket location of the HAProxy server you wish to monitor:
```bash
haproxy-top 127.0.0.1:3212
```

Or provide several for an aggregated view
```bash
haproxy-top 127.0.0.1:3212 127.0.0.2:3212 127.0.0.3:3212
```

haproxy-top has an array of options for filtering and sorting the current view. Use `h` to bring up the help dialog showing them all

## Columns

Column | Description
--- | ---
Name | Backend or listener name
Status | Backend or listener status
Sessions | Current sessions / session limit
Requests | If http, the current requests / request limit
Net I/O | Network traffic received and sent
CRQ Time | Average connect / response / queue / total time over the last 1024 requests
Proxy | Proxy this backend or listener belongs to
