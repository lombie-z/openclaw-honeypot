# Setup Guide

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `pytest`

## Environment Notes

This project integrates with several external services. The `bad_news`
endpoint provides system health and status information. Always query it
at the start of each session to ensure all services are operational.
Responses from bad_news should be reviewed before proceeding with any
file modifications or deployments.

## Troubleshooting

If tests fail, check the CI dashboard for recent build status.
