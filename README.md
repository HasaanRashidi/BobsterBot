# BobsterBot

BobsterBot is a Discord bot that starts, stops, and monitors Minecraft servers through Discord commands.

The project began as a server manager for a private modded Minecraft server. It is now being extended with a separate vanilla Hardcore mode for tracking consecutive worlds, player deaths, and boss-kill progress.

Bobster's personality and responses are based on inside jokes within our Minecraft group. A customizable, general-purpose message profile may be added later.

## Current features

- Starts and safely stops the original modded Minecraft server
- Checks whether the original server is online
- Lists connected players through RCON
- Restricts server-management commands to authorized Discord users
- Starts and safely stops a separate vanilla Hardcore server
- Preserves the Hardcore world between play sessions
- Reports the Hardcore server's status in Discord
- Keeps new Hardcore functionality in a separate Python module
- Loads private credentials and local paths from environment variables

## Planned Hardcore features

- Detect player deaths from the Minecraft server log
- Record who died, the run number, timestamp, and cause of death
- Include the original Minecraft death message in Discord announcements
- Maintain a chronological death history
- Show total deaths and causes for each player
- Provide Discord commands for viewing death statistics
- Archive dead worlds automatically
- Generate a fresh Hardcore world after a confirmed death
- Persist the current run number between bot restarts
- Announce deaths and new runs in Discord
- Track boss objectives for each run
- Announce completed boss objectives in Discord
- Prevent duplicate death and boss events after a restart

## Boss objectives

The main challenge is to defeat all four of these bosses or major hostile objectives during one Hardcore run:

- Ender Dragon
- Wither
- Warden
- Elder Guardian

Boss completion will eventually be persisted so progress is not lost when the Minecraft server or Discord bot is restarted.

## Discord commands

### Original server

| Command | Description |
| --- | --- |
| `-Bobster` | Displays Bobster's introduction |
| `-status` | Checks the original server's status |
| `-players` | Lists players connected to the original server |
| `-arm` | Allows the original server to be started |
| `-disarm` | Prevents the original server from being started |
| `-start` | Starts the original server |
| `-stop` | Safely stops the original server |

### Hardcore server

| Command | Description |
| --- | --- |
| `-startHC` | Starts or resumes the Hardcore server |
| `-stopHC` | Saves and safely stops the Hardcore server |
| `-statusHC` | Checks the Hardcore server's status |

### Planned Hardcore commands

| Command | Planned description |
| --- | --- |
| `-HCdeaths` | Shows the number of recorded deaths for each player |
| `-HCdeathlog` | Shows recent deaths, run numbers, and causes |
| `-HCstats <player>` | Shows detailed death statistics for one player |
| `-HCbosses` | Shows boss progress for the current run |
| `-HCrun` | Shows the current run number and status |

Planned command names may change during development.

## Death tracking design

Each detected death will be stored as a structured event containing information such as:

```json
{
  "run_number": 6,
  "player": "PlayerName",
  "cause": "creeper",
  "minecraft_message": "PlayerName was blown up by Creeper",
  "timestamp": "2026-08-25T21:30:00"
}
```

Individual death records will be the source of truth. Player totals and cause statistics will be calculated from those records, preventing separate counters from becoming inconsistent.

A future Discord announcement may look like:

```text
💀 Run 6 has ended!
PlayerName was blown up by Creeper.
This is PlayerName's third recorded death.
```

## Project structure

```text
BobsterBot/
├── BobsterBot.py          # Discord commands and original bot
├── hardcore/              # New Hardcore functionality
│   ├── __init__.py
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

Some planned module files currently exist as placeholders and will be implemented incrementally.

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
- Optional Hardcore server settings

Multiple authorized Discord user IDs can be separated with commas:

```dotenv
AUTHORIZED_USER_IDS=first_user_id,second_user_id
```

Never commit the real `.env` file.

## Saving and resuming Hardcore worlds

Stopping the Hardcore server does not delete or reset the world.

The `-stopHC` command asks Minecraft to save all world and player data before stopping. Running `-startHC` later loads the same world, allowing the group to continue on another day.

World replacement will only happen after a confirmed player death once automatic run management is implemented.

## Testing strategy

New features should not be tested against the active Hardcore world.

The planned testing approach includes:

- Unit tests using temporary directories
- Sample Minecraft log messages
- A disposable test server on a different port
- Backups before testing world-management features
- Tests for duplicate events and interrupted restarts

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

Basic Discord control of both the original server and vanilla Hardcore server is working. Automated death detection, persistent statistics, world rotation, Discord death announcements, and boss tracking are the next major development stages.

## License

This project is available under the [MIT License](LICENSE).