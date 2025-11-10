# Temporal Documentation Helper

This Slack bot evaluates questions and provides responses if they can be found in the Temporal documentation.

## Setup
- Create a .env file in the root directory and populate the following fields:
    - SLACK_BOT_TOKEN
    - SLACK_SIGNING_SECRET
    - SLACK_CLIENT_ID
    - SLACK_CLIENT_SECRET
    - SLACK_REDIRECT_URI
    - SLACK_BOT_USER_ID

## Running

- Start the bot
`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

- Expose it to the world
`ngrok http --url=${NGROK_URL}$ 8000`
