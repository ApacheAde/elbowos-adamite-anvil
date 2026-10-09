# Adamite Anvil

Full-colour Python 3 chartreuse forge-strike arcade for ElbowOS.

A hammer swings over a belt of cooling ingots. Strike when the head is centred on a dwelling bar. Perfect timing tempers chartreuse adamite and builds a combo. Miss, and the bar leaves as slag.

Not a commercial emulator. Original rules and art.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 adamite_anvil.py --play
```

Space or click strikes. The swing is automatic.

## Record a 9:16 reel

```bash
python3 adamite_anvil.py --record
```

Writes `ADAMITE_ANVIL_ElbowOS.mp4` (1080x1920, 15s, 30fps, h264). Headless recording uses `SDL_VIDEODRIVER=dummy` and pipes RGB frames to ffmpeg.

## Links

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1jQke4RCMdOgVQWm3-nD-ECl1Lx6EtmeC/view?usp=drivesdk
