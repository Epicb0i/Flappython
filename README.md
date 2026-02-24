# Flappy Bird — Shadow World

A Flappy Bird clone with a twist: **Shadow World**. As you score higher, darkness creeps across the screen. A shrinking spotlight follows your bird — survive the shadows or be swallowed.

## The Twist

After scoring 4 points, the screen starts going dark. A glowing circle of light surrounds the bird — that's all you can see. The longer you survive:

- **Darkness intensifies** — opacity climbs toward 180, with a breathing pulse effect
- **Your spotlight shrinks** — the glow radius gets smaller every point
- **Darkness accelerates** — the rate increases the higher you score
- **Pipe relief** — passing a pipe pair briefly drops the darkness

## Controls

| Input | Action |
|-------|--------|
| Space / Click / Tap | Flap |
| P / Pause button | Pause / Resume |
| ESC | Quit (or unpause) |

## Features

- Day/Night mode toggle with parallax city backgrounds
- 5 SFX + 5 BGM tracks (day and night variants)
- Music & SFX toggles via settings panel
- Death tumble animation with screen shake
- Score pop effect and medal tiers (Bronze → Platinum)
- Pause/Play support
- Phone simulation mode (`--phone` flag)
- Responsive layout for landscape and portrait

## How to Run

```
pip install pygame
python flappybird.py
```

Phone mode:
```
python flappybird.py --phone
```

## Requirements

- Python 3.10+
- pygame 2.x

## Project Structure

```
flappybird.py              Main game file
FlappySound/               SFX and BGM audio files
free-scrolling-city-backgrounds-pixel-art/   Night parallax layers
Backgroundfull.png         Day background
flappybird.png             Bird sprite
toppipe.png / bottompipe.png   Pipe sprites
day-and-night.png          Day/Night toggle icon
volume.png                 Sound settings icon
pause.png / play-buttton.png   Pause/Play icons
```
