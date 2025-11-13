# Temporal Documentation Helper

> **NOTE**: This branch contains instructions for setting up the "Temporalized" version of the temporal-documentation-helper, switch to the main branch for the original version.

This Slack bot evaluates questions and provides responses if they can be found in the [Temporal Technologies documentation](https://docs.temporal.io/).

### Branches
- `main`: directly queries Ollama to classify questions and generate responses.
- `temporal`: relies on Temporal workflows to handle LLM processing.

## Prerequisites

- Configure a [Slack application](https://docs.slack.dev/tools/bolt-python/building-an-app) in your workspace. Include the following permissions and event subscriptions:
    - Actions: `chat:write`
    - Information: `channels:history`, `reactions:read`
    - Events: `message.channels`, `reaction_added`
- Setup a free [Ngrok account](https://ngrok.com/pricing) to expose the bot to the world.
- Download and install [Ollama](https://ollama.com/)

## Setup
- Clone repo
- Create a new virtualenv `python -m ~/path/to/temporalio`
- Activate virtualenv `source bin ~/path/to/temporalio/bin/activate`
- Install pre-requisites `pip install -r requirements.txt`
- Create a .env file (`touch .env`) in the root directory and populate the following fields:
    - SLACK_BOT_TOKEN
    - SLACK_SIGNING_SECRET
    - SLACK_CLIENT_ID
    - SLACK_CLIENT_SECRET
    - SLACK_REDIRECT_URI
    - SLACK_BOT_USER_ID
- Generate the Chroma vectorstore `python scripts/build_temporal_index.py`
- Install the Temporal CLI `brew install temporal`


## Running
- Start the bot
`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

- Expose it to the world
`ngrok http --url=${NGROK_URL}$ 8000`

- Start Ollama
`ollama run llama3`

- Start the Temporal server
`temporal server start-dev --ui-port 8080`

- Start the Temporal worker
`cd temporalio-doc-helper && python -m temporal.worker`


## Usage
Navigate to the primary channel the bot is configured to listen on and submit a random question, then a question about the Temporal platform. 
- Unrelated questions should be ignored
- Questions about Temporal should receive a reply with a response referencing the documentation.
