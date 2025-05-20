# Discord_Bot
If you use this, please credit me somewhere as `@That-Random-Guy567` (github) or `@thatrandomblenderguy` (youtube, discord)
To install the packages required but this test, Go to `~/Extra/requirements.txt` and folllow the instructions to install the packages.

Table of Contents
    - Introduction
    - Contributing
    - License

## Game Features

### YO Game
- Play in a configurable channel: only "Yo", "Yoo", ..., or "Yooo", "Yoo", "Yo", etc.
- Users must alternate and can increase or decrease O's by exactly one.

### Count Game
- Play in a configurable channel: count up or down by exactly 1 (1, 2, 3, ...)
- Users must alternate.

### Setup
- `/setgame game:<yo|count> channel:<channel>` — set up games in a channel.
- `/autocreate_offender_role game:<yo|count>` — auto-create and attach O-Offender role.
- `/attach_offender_role game:<yo|count> role:<role>` — use an existing role as O-Offender.

Breaking the sequence gives you the O-Offender role for that game.

## Making custom discord bot that allows for:

Moderation
    -> Logs
        -> Edit messages
        -> Delete Messages

Youtube Upload Pings
    -> Send an announcement in channel ID
    -> Creates a forum post for video discussion
        -> Has Tags for Videos and Shorts
            -> Auto tag for shorts if the video title has "#" in it

Bump Remind
    -> Send a bump remimder message in bump channel every 2 hours, then if no one bumps, pings @bumper to bump
    -> has a count interval, and pings all bumpers on the 12th bump

Slash Commands
    -> /Send, which sends messsage as a bot
    -> /next_bump, which shows next bump time
    -> /uptime, shows bot uptime
    -> /latency, shows ping of bot from webhook/servers


(Subject to change)

## Contributing
    We welcome contributions! Please follow these steps:

    1. Fork the repository.
    2. Create a new branch: git checkout -b feature/new-feature
    3. Make your changes.
    4. Commit your changes: git commit -m "Add new feature"
    5. Push to the branch: git push origin feature/new-feature
    6. Submit a pull request.