# Security Policy

## Supported Versions

This repository ([`Onikore/dronekit2`](https://github.com/Onikore/dronekit2)) is a fork of the
original DroneKit-Python that picks up maintenance after upstream went dormant following the
2.9.2 release. Only this fork's own line of releases is supported here.

| Version        | Supported          |
| -------------- | ------------------- |
| 3.0.x          | :white_check_mark: |
| 2.x (upstream) | :x: (unsupported in this fork; see [upstream](https://github.com/dronekit/dronekit-python)) |
| < 2.0          | :x:                 |

If you're running a `2.x` release installed as `dronekit` from PyPI, upgrading to `dronekit2`
`3.0.x` is a drop-in change for application code - see
[`docs/about/migrating_v3.rst`](docs/about/migrating_v3.rst).

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for a suspected security vulnerability.

The recommended way to report a vulnerability privately is through
[GitHub's private vulnerability reporting](https://github.com/Onikore/dronekit2/security/advisories/new)
for this repository (the "Report a vulnerability" button under the repo's **Security** tab). If
that option isn't available to you (private reporting has to be enabled by the repository owner
and we can't guarantee it is at any given time), please open a regular
[GitHub issue](https://github.com/Onikore/dronekit2/issues/new) that avoids exploit details in
the public description and asks a maintainer to follow up on a private channel instead.

When reporting, please include as much of the following as you can:

* The version of `dronekit2` (or commit SHA) affected.
* A description of the vulnerability and its potential impact (e.g. does it require a
  malicious/compromised vehicle connection, a crafted MAVLink stream, a malicious connection
  string, etc.).
* Steps to reproduce, or a minimal proof-of-concept script.

### What to expect

This is a small, part-time maintained open-source fork, not a company with a security team, so
please treat the following as a best effort rather than a contractual SLA:

* An initial acknowledgement within roughly **one week**.
* An assessment of the report and, if valid, a rough plan/timeline for a fix communicated back
  to you - timing depends on severity and maintainer availability.
* Credit in the release notes / advisory for the reporter, unless you'd prefer to remain
  anonymous.

Given DroneKit connects to real, physically-moving vehicles over MAVLink, please treat issues
that could let an untrusted party inject or spoof MAVLink traffic, escalate a read-only
connection into command/control, or otherwise affect vehicle safety as high severity when
reporting.
