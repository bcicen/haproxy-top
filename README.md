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
