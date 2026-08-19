# Security Policy

This repository is a local engineering project and is not hardened for production or public-network exposure. The default MQTT broker permits anonymous local access for a zero-setup demo.

Do not expose the Compose services to an untrusted network. Before any shared deployment, add unique secrets, MQTT TLS and authentication, API authorization, restricted network rules, dependency scanning, and a documented vulnerability-reporting channel.
