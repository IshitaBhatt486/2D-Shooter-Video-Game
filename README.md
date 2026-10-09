# Quantum Squad Shooter

Quantum Squad Shooter is a 2D side-scrolling action game available as both a
Pygame desktop application and an HTML5 Canvas browser game.

![Python Preview](assets\images\Preview\PythonVersion.png)

![Web Preview Startup](assets\images\Preview\WebPreviewStartup.png)

![Web Preview](assets\images\Preview\WebPreview.png)


## Repository layout

```text
game/
├── assets/
│   ├── audio/              # Shared sound effects and music
│   ├── images/             # Shared sprites, tiles, backgrounds, and UI art
│   └── levels/             # Shared CSV level definitions
├── desktop/
│   └── code/               # Pygame desktop application
├── web/                    # Static HTML, CSS, JavaScript, and browser config
├── internal-docs/          # Technical architecture and test documentation
├── documentation.md        # Project and gameplay documentation
├── README.md
├── requirements.txt
└── vercel.json
```

## Run the desktop application

```powershell
python -m pip install -r requirements.txt
python desktop/code/main.py
```

## Run the browser version locally

```powershell
python -m http.server 4173
```

Open [http://localhost:4173/web/](http://localhost:4173/web/).

## Deploy to Vercel

Import the repository in Vercel as a static project. `vercel.json` routes the
site root to the browser game in `web/` and preserves `/assets/` for shared
game files.

## Configuration

- Desktop: `desktop/code/shooter/config.py`
- Browser: `web/web-config.js`

See [documentation.md](documentation.md) and [internal-docs](internal-docs)
for detailed gameplay, architecture, optimisation, and testing notes.
