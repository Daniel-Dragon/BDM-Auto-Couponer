# Black Desert Mobile Auto Couponer

## Setup and Usage Instructions
### Config
1. Rename `config-template.json` to `config.json`.
2. Fill in your `family_name` and `region` in `config.json`.

### Redemption Tracking
1. The script tracks redeemed coupons in `redeemed.json`.
2. This file is created automatically on the first run. Make sure to mount it as a volume in Docker to persist data if you chose to run in a container.