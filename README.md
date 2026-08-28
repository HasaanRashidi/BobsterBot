# BobsterBot

BobsterBot is a Discord bot that starts, stops, monitors, and manages Minecraft servers through Discord commands.

The project supports both the original modded Minecraft server and a separate vanilla Hardcore challenge with persistent runs, death tracking, world rotation, and boss-objective tracking.

Bobster's personality and responses are based on inside jokes within our Minecraft group.

## Current features

- Starts and safely stops the original modded Minecraft server
- Checks whether the original server is online
- Lists connected players through RCON
- Restricts server-management commands to authorized Discord users
- Starts, stops, and resumes a separate vanilla Hardcore server
- Preserves the Hardcore world between play sessions
- Persists the current run number, status, death history, and boss progress
- Detects player deaths from the Minecraft server log
- Announces detected deaths in Discord
- Prevents duplicate death records for the same run
- Archives all three dimensions from a completed Hardcore run
- Safely prepares the next Hardcore world
- Automatically detects boss defeats from Minecraft player statistics
- Announces boss defeats in Discord and inside Minecraft
- Provides an authorized manual fallback command for boss defeats
- Displays current boss progress through `-statusHC`
- Loads private credentials and local paths from environment variables
- Includes automated tests for state, monitoring, server control, world rotation, deaths, and bosses
- Provides overall death totals, recent death history, and per-player cause statistics

## Remaining work

- Perform final end-to-end validation with the disposable Hardcore test server
- Continue improving error reporting and operational documentation

## Boss objectives

The main challenge is to defeat all four objectives during one Hardcore run:

- Ender Dragon
- Wither
- Warden
- Elder Guardian

Boss completion is stored in the persistent Hardcore state, so progress survives Minecraft server and Discord bot restarts.

## Discord commands

### Help

| Command | Description |
| --- | --- |
| `-Bobster` | Displays the available commands and support contact |

### Original server

| Command | Description |
| --- | --- |
| `-status` | Checks the original server's status |
| `-players` | Lists players connected to the original server |
| `-start` | Starts the original server |
| `-stop` | Safely stops the original server |
| `-arm` | Allows others to start the original server |
| `-disarm` | Prevents others from starting the original server |

### Hardcore server

| Command | Description |
| --- | --- |
| `-statusHC` | Shows the run status, server connection, and boss progress |
| `-startHC` | Starts or resumes the Hardcore server |
| `-stopHC` | Saves and safely stops the Hardcore server |
| `-nextHC` | Archives a dead run and prepares the next world |
| `-bossHC <boss>` | Manually records a defeated boss as an authorized fallback |
| `-HCdeaths` | Shows total recorded deaths for each player |
| `-HCdeathlog` | Shows the five most recent Hardcore deaths |
| `-HCstats <player>` | Shows one player's death total and causes |

The accepted boss names are `ender dragon`, `wither`, `warden`, and `elder guardian`.

The Hardcore start, stop, world-rotation, and manual boss commands are restricted to authorized Discord users.

## Help and support

For questions, problems, or help using BobsterBot, contact **krezn1k** on Discord.

## Death tracking

While a Hardcore run is active, BobsterBot monitors the Minecraft server log for player-death messages.

The first detected death in a run is stored as a structured record:

```json
{
  "run_number": 6,
  "player": "PlayerName",
  "cause": "creeper",
  "message": "PlayerName was blown up by Creeper",
  "timestamp": "2026-08-25T21:30:00+00:00"
}
```

Recording a death changes the run status to `DEAD`, saves the persistent state, and sends a Discord announcement:

```text
💀 Run 6 has ended!
PlayerName was blown up by Creeper.
```

Only one death is recorded per run, preventing duplicate log events or bot restarts from creating repeated records.

Individual death records are the source of truth. Future player totals and cause statistics will be calculated from these records rather than stored as separate counters.

## Project structure

```text
BobsterBot/
├── BobsterBot.py          # Discord commands and original bot
├── hardcore/              # New Hardcore functionality
│   ├── __init__.py
│   ├── bosses.py          # Reads boss progress from player statistics
│   ├── config.py          # Hardcore server configuration
│   ├── server.py          # Server process management
│   ├── state.py           # Persistent run and event state
│   ├── monitor.py         # Minecraft log and event monitoring
│   ├── worlds.py          # World archival and reset logic
│   └── service.py         # Coordinates Hardcore features
├── tests/                 # Automated tests
├── data/                  # Local runtime state
├── .env.example           # Safe environment configuration example
├── .gitignore             # Files Git must not upload
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

The Hardcore package separates configuration, process control, log parsing, persistent state, boss detection, world rotation, and service logic into focused modules.

## Requirements

- Windows
- Python 3.10 or newer
- A Discord bot application and token
- Java compatible with the selected Minecraft server version
- A locally installed Minecraft server
- RCON enabled if using the original server's player-list command

The Minecraft server JAR, Java runtime, worlds, logs, player data, and private configuration are not included in this repository.

## Local setup

1. Clone the repository.

2. Open PowerShell in the project directory.

3. Create a Python virtual environment:

   ```powershell
   python -m venv .venv
   ```

4. Activate the virtual environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

5. Install the Python dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

6. Copy `.env.example` to a new file named `.env`.

7. Replace the example values in `.env` with your local configuration.

8. Add the required Minecraft server files locally.

9. Enable the Discord bot's Message Content Intent in the Discord Developer Portal.

10. Run the bot:

    ```powershell
    python BobsterBot.py
    ```

## Environment configuration

BobsterBot reads private credentials and computer-specific paths from `.env`.

Example settings are documented in `.env.example`, including:

- `DISCORD_TOKEN`
- `AUTHORIZED_USER_IDS`
- `OLD_RCON_PASSWORD`
- `OLD_JAVA_EXECUTABLE`
- `OLD_SERVER_DIRECTORY`
- `HC_SERVER_DIRECTORY`
- `HC_JAVA_EXECUTABLE`
- `HC_SERVER_PORT`
- `HC_MIN_MEMORY`
- `HC_MAX_MEMORY`
- `HC_ANNOUNCEMENT_CHANNEL_ID`
- `HC_ARCHIVE_DIRECTORY`

Multiple authorized Discord user IDs can be separated with commas:

```dotenv
AUTHORIZED_USER_IDS=first_user_id,second_user_id
```

Never commit the real `.env` file.

## Saving and resuming Hardcore worlds

Stopping the Hardcore server does not delete or reset the world.

The `-stopHC` command asks Minecraft to save all world and player data before stopping. Running `-startHC` later loads the same world, allowing the group to continue on another day.

After a run is marked `DEAD` and the server is offline, an authorized user can run `-nextHC`. The command archives `world`, `world_nether`, and `world_the_end` in the configured archive directory before preparing the next run. It refuses to continue if a required dimension is missing or the destination archive already exists.

## Testing strategy

Automated tests use temporary directories, sample Minecraft log messages, mock server processes, and temporary player-stat files. The suite covers:

- Persistent Hardcore state
- Death-message parsing and duplicate prevention
- Death and boss announcement formatting
- Server monitoring and command input
- Boss-stat detection and malformed files
- Boss validation and duplicate prevention
- Three-dimension world archival
- Safety guards for active, incomplete, or conflicting runs

The active Hardcore world is not used for automated testing. Final live validation should use a disposable server or carefully controlled test run.

The live world and archived worlds remain outside version control.

## Security and privacy

The repository deliberately excludes:

- Discord bot tokens
- RCON passwords
- Public IP addresses
- Minecraft worlds and backups
- Server logs
- Player UUID caches
- The Minecraft server JAR
- The local Java runtime
- IDE configuration

Only safe examples and source code should be committed.

## Development status

BobsterBot is under active development.

The core Hardcore workflow is implemented: server control, persistent run state, automatic death detection, Discord death announcements, safe world rotation, automatic boss detection, Minecraft and Discord boss announcements, boss-progress reporting, and a manual boss fallback command.

Remaining work primarily consists of final disposable-server validation and operational polish.

## License

This project is available under the [MIT License](LICENSE).