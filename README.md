# GitHub Webhook Event Tracker

## Overview
Tracks GitHub Push, Pull Request, and Merge events using GitHub Webhooks,
stores minimal data in MongoDB, and displays recent activity via a polling UI.

## Tech Stack
- Flask
- MongoDB
- Vanilla JS
- GitHub Webhooks

## Setup
1. Run MongoDB
2. Install dependencies
3. Start Flask server

## Testing
- Manual Postman webhook simulation
- GitHub Webhook integration

## UI Polling
UI fetches latest events every 15 seconds from MongoDB.
