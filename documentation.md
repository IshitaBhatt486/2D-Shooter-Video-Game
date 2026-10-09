## Architecture

`Game` is the application coordinator. It owns the Pygame window, active sprite groups, input state, current level, and camera offset. It creates a `World` for each level and updates/draws the entities every frame.

`World` converts tile IDs in each CSV file into collision tiles, scenery, water, exits, pickups, enemies, and the player spawn. `Soldier` implements shared player/enemy movement and animation; player actions are driven by input, while enemy actions are driven by its patrol and vision logic.

## Levels

Each file in `assets/levels/` is a comma-separated 16 × 150 grid. `-1` represents an empty cell. The remaining tile IDs have these roles:

| Tile IDs | Purpose |
| --- | --- |
| `0–8` | Solid terrain / collision tiles |
| `9–10` | Water (kills characters) |
| `11–14` | Decorative scenery |
| `15` | Player spawn |
| `16` | Enemy spawn |
| `17` | Ammo pickup |
| `18` | Grenade pickup |
| `19` | Health pickup |
| `20` | Level exit |

To add a level, create `assets/levels/level4_data.csv` using the same dimensions and tile IDs, then update `MAX_LEVELS` in `desktop/code/shooter/config.py` to `4`.

## Customization

- **Gameplay constants:** Adjust desktop settings in `desktop/code/shooter/config.py` or browser settings in `web/web-config.js`.
- **Sprites and animations:** Player and enemy animations live in `assets/images/player/` and `assets/images/enemy/`.
- **Audio:** Replace files in `assets/audio/` and retain their expected filenames.
- **Tiles:** Artwork is loaded from `assets/images/tile/0.png` through `20.png`.

# Notes
- **Desktop:** Pygame (`desktop/code/shooter/`), launched with `python desktop/code/main.py`.
- **Browser:** HTML5 Canvas (`web/index.html` + `web/webgame.js`), served as a static
  Vercel site.

Note: (The game was originally built as a Desktop app in Python for a competition and a web browser version was later created to allow deployment on a web browser)

## Runtime model

Both editions follow the same basic game-loop pattern:

```text
read input → update simulation → resolve collisions/damage → draw frame → repeat
```

The desktop loop is clock-capped at 60 FPS using `pygame.time.Clock.tick(FPS)`.
The web loop is driven by `requestAnimationFrame`, with a 60-FPS time gate so a
browser that calls animation frames more often does not update the simulation
unnecessarily.

The two runtimes deliberately share assets and level CSV files but do not share
source code. Since Pygame cannot execute in a normal browser, JavaScript is used.

## Desktop architecture

### Entry point and coordinator

`desktop/code/main.py` creates `Game` from `desktop/code/shooter/game.py`. `Game` owns window
creation, input state, the active level, camera offsets, HUD, menu state, and
all Pygame sprite groups. It is the composition root: other objects receive a
reference to it rather than relying on module-level globals.

This gives entity code controlled access to shared state such as the world,
asset cache, scrolling offset, and target groups, while keeping startup and
level transitions in one place.

### World construction

`World.load_data()` reads a 16 × 150 comma-separated tile grid. `process_data()`
turns that grid into a compact set of runtime objects:

| Tile range | Runtime representation |
| --- | --- |
| `0–8` | Tuple of image + collision rectangle in `obstacle_list` |
| `9–10` | Water scrolling sprites |
| `11–14` | Decorative scrolling sprites |
| `15` | Player `Soldier` |
| `16` | Enemy `Soldier` |
| `17–19` | Ammo, grenade, and health `ItemBox` sprites |
| `20` | Exit scrolling sprite |

Static solid terrain is kept as simple image/rectangle tuples rather than full
sprites. That is appropriate because it needs only drawing and rectangle
collision; it does not need a per-object `update()` method.

### Entities and combat

`Soldier` is the common actor class for the player and enemies. It owns:

- position and velocity;
- gravity, horizontal movement, terrain/water/fall checks;
- animation state (`idle`, `run`, `jump`, `death`);
- health and death state;
- fire cooldown, ammunition, and grenade count; and
- a facing direction and an enemy vision rectangle.

Enemy AI is intentionally lightweight. Each enemy checks whether the player is
nearby horizontally, faces the player, and fires if the vision rectangle
overlaps. Otherwise it patrols, periodically reverses, and turns on terrain
collision. This is a local rule system rather than pathfinding, which is a good
fit for a flat side-scroller and keeps CPU cost proportional to enemy count.

Each `Bullet` records its owner. That avoids friendly fire checks against every
possible character: a player bullet tests enemies; an enemy bullet tests only
the player. `take_damage()` centralizes player hit feedback, and both runtimes
clamp death at zero health. Enemy health bars draw only while an enemy is alive.

### Assets and feedback

`Assets` loads UI, backgrounds, tiles, item icons, sounds, and animation frames
once when the game begins. It holds the resulting Pygame surfaces in memory,
which eliminates disk I/O during gameplay. Sprite animations are lists indexed
by action and frame number.

The small menu, hit, death, and completion effects are generated as PCM buffers
at startup. This avoids more binary files while making the feedback immediate.
Damage/death visuals use alpha overlays and a short shake timer.

## Browser architecture

The browser app is a buildless static site. `web/index.html` provides accessible
buttons and overlays, `web/webgame.css` handles responsive presentation, and
`web/webgame.js` owns the canvas simulation.

### Loading and data structures

`loadLevel(number)` fetches the same CSV level files used by the Pygame build,
then produces one numeric grid and small arrays for `enemies`, `bullets`,
`grenades`, and `pickups`. The player is a plain JavaScript object.

The browser keeps world coordinates separate from viewport coordinates. Drawing
uses `worldX - camera`; gameplay/collision calculations stay in world space.
This avoids moving every entity when the player walks and reduces scrolling to
one subtraction at draw time.

### Flags

| Flag | Meaning |
| --- | --- |
| `running` | A mission may advance the simulation. |
| `paused` | Simulation is frozen but the last frame remains visible. |
| `player.dead` | Player is in the death animation window. |
| `level` | Current sector, from 1 through 3. |

The final exit calls `finish(true)`, unlocks `quantum-squad-vanguard` in
`localStorage`, and shows the achievement screen.

(Help and pause are HTML overlays rather than canvas-only controls, which makes them discoverable and keyboard-accessible.)

## Optimisations

- Asset caching / lazy loading: Browser `image(path)` stores each `Image` in a `Map`; future frames reuse it. In Pygame the same is done at startup through `Assets`. This prevents asset
network/disk work in the hot render loop.
- Fixed-size tile grid with constant-time lookups: `tileAt(x, y)` converts a coordinate into row/column indices, then reads one cell. Terrain collision therefore uses four grid lookups at the entity corners, not a scan over all map tiles. (broad-phase collision based on spatial partitioning by the tile grid.)
- Narrow-phase checks only for relevant entities. Projectiles do not test every entity. Their owner selects the opposing target set first. Enemies use a simple proximity/vision condition before AI shooting logic.
- Array filtering for short-lived entities: The browser uses `filter()` to discard spent bullets, exploded grenades, and collected pickups. The Pygame version uses `Sprite.kill()` and `Group.update()`. Both prevent dead objects from accumulating over a session.
- Frame limiting: Pygame limits the loop to 60 FPS. The browser only performs a simulation step
when roughly 16.67 ms have elapsed to keep movement and animation stable on fast displays and avoids unnecessary CPU use.
- Background layers use the same image repeated at different scroll multipliers.
Only the draw position changes; no additional collision or map state is needed.
