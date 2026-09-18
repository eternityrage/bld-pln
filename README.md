# PlanView Lens

Automated content pipeline for the **PlanView Lens** Facebook page — sharing construction plans, building designs, and architectural content.

## What it does

1. **Fetches** videos from a Google Drive folder
2. **Processes** them (upscales to 1080x1920, normalizes audio)
3. **Generates AI captions** via Pollinations AI
4. **Publishes** to Facebook (Reels + Stories)
5. **Supports Instagram** — automatically publishes when `INSTAGRAM_ACCOUNT_ID` is configured

## Setup

### GitHub Secrets

| Secret | Description |
|--------|-------------|
| `META_LONG_LIVED_ACCESS_TOKEN` | Meta long-lived access token |
| `FB_PAGE_ID` | Facebook page ID (PlanView Lens) |
| `FB_PAGE_ACCESS_TOKEN` | Page-specific access token |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | Google service account JSON |
| `GOOGLE_DRIVE_FOLDER_ID` | Google Drive folder containing videos |
| `POLLINATIONS_API_KEY` | Pollinations API key for AI captions |
| `INSTAGRAM_ACCOUNT_ID` | (Optional) Instagram account ID for auto-publish |

### Automation

Runs 3x daily via GitHub Actions (04:00, 12:00, 20:00 UTC). Can also be triggered manually.

### Local Development

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in .env with your credentials
python auto_pipeline.py
```
