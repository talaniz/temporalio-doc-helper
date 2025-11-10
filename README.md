#digital-developer-advocate

To start the application:

- Start the bot
`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

- Expose it to the world
`ngrok http --url=noticeably-nearby-dory.ngrok-free.app 8000`

Or

`tmuxinator start slackbot`