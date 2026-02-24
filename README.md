# 🎒 Exo-Inventory

**A powerful, high-performance Minecraft inventory rendering library for Python.**

`exo-inventory` is a professional-grade library designed to fetch, mirror, and render Minecraft item icons and player inventories with 100% customizability. Whether you need a standard player inventory or a completely custom 9x6 chest layout, `exo-inventory` handles the assets and coordinates for you.

---

## ✨ Features

- 🔄 **Smart Asset Mirroring**: Local mirror of Jemsire's Minecraft icons with automatic version detection (1.13.2 to 1.21.10+).
- 🖼️ **Flexible Rendering Engine**: Support for arbitrary item placement (`render_custom`) or standard Minecraft layouts (`render_player`).
- 🤖 **Automated Maintenance**: Integrated GitHub Actions workflow to sync assets and rebuild metadata daily.
- 🎨 **UI Customization**: Download and cache UI themes (backgrounds, empty slot icons) from remote repositories.
- 👤 **Player Models**: Automatic integration with `mc-heads.net` for rendering 3D player skins.
- ⚡ **High Performance**: Path caching, recursive item lookup, and asynchronous asset fetching.

---

## 🚀 Installation

Install the library directly from your local path or git:

```bash
# Local installation
pip install ./exo-lib

# Git installation (once published)
pip install git+https://github.com/zKauaFerreira/Exo-Lib.git
```

---

## ⚡ Quick Start (In 5 Minutes)

### 1. Initialize Assets

The `AssetsManager` handles all the heavy lifting of downloading and indexing icons.

```python
import asyncio
from exo_inventory import AssetsManager, InventoryRenderer

async def main():
    # Path where icons will be mirrored
    assets = AssetsManager("./assets_cache")

    # Initialize index and download UI assets
    await assets.initialize()

    # Optional: Perform a full sync of all Minecraft icons (heavy)
    # await assets.full_sync()

asyncio.run(main())
```

### 2. Render a Player Inventory

Use the built-in helper for standard player data.

```python
async def render():
    renderer = InventoryRenderer("./assets_cache")

    player_data = {
        "uuid": "7be0ee8d-389a-44c9-a9bf-513f7960bcbf",
        "armor": [{"id": "diamond_helmet", "slot": 39}],
        "hotbar": [{"id": "netherite_sword", "slot": 0, "count": 1}],
        "main_inventory": [],
        "off_hand": {"id": "shield"}
    }

    image_path = await renderer.render_player(player_data)
    print(f"Inventory saved to: {image_path}")
```

---

## 🛠️ Advanced Usage

### 🧩 100% Custom Layout (`render_custom`)

Don't be limited by standard UI. Place any item anywhere.

```python
items = [
    {"id": "apple", "x": 8, "y": 8, "count": 64},
    {"id": "gold_ingot", "x": 26, "y": 8, "count": 32},
    {"id": "diamond", "x": 8, "y": 26, "empty": "helmet"} # Shows helmet icon if diamond is missing
]

await renderer.render_custom(
    items_map=items,
    width=176,
    height=166,
    background="custom_bg.png"
)
```

### 📦 Asset Utilities & Exporting

Need the icons for something else? You can export assets from the cache to any directory.

```python
# Export specific icons and UI elements to a folder
await assets.export_assets(
    target_dir="./my_resource_pack",
    items_list=["diamond", "netherite_sword"],
    include_ui=True
)

# Or just download icons to the internal cache without rendering
await assets.download_assets(["stone", "grass_block", "dirt"])
```

### 👤 Advanced Player Rendering

Customizing the player model render (poses/angles).

```python
# Get a 3D body render with a 45-degree rotation
body_img = await renderer.get_player_render(
    uuid="zKauaFerreira",
    render_type="body", # options: 'body', 'head', 'avatar', 'player'
    size=400,
    angle=45
)
```

### 🛰️ Remote Asset Synchronization

The library can automatically pull UI themes from your GitHub repo:

| Asset                | Source                                  |
| -------------------- | --------------------------------------- |
| `inventory_bg.png`   | `zKauaFerreira/Exo-Lib/main/src/assets` |
| `jemsire_index.json` | Remote metadata mirror                  |
| `empty_armor_slots`  | PrismarineJS official assets            |

---

## 🤖 Automation (CI/CD)

The library includes a pre-configured GitHub Action (`.github/workflows/update_assets.yml`) that:

1. Runs every day at midnight.
2. Checks Jemsire for new Minecraft versions.
3. Downloads new ZIPs and extracts them recursively.
4. Generates a new `jemsire_index.json`.
5. Commits changes back to your repository automatically.

---

## 📂 Project Structure

```text
exo-inventory/
├── src/
│   └── exo_inventory/
│       ├── __init__.py    # Main exports
│       ├── assets.py      # Jemsire & Remote Sync logic
│       └── renderer.py    # Pillow-based rendering engine
├── pyproject.toml         # Build & Dependency config
└── README.md              # You are here
```

---

## 🛠️ Requirements

- **Python 3.10+**
- **Pillow**: For image processing.
- **aiohttp**: For asynchronous asset downloads.
- **discord.py**: Compatible for bot integrations.

---

## 🖥️ CLI Commands

`exo-inventory` provides built-in CLI commands for easy maintenance and asset extraction.

```bash
# Sync all assets to the library's internal storage
python -m exo_inventory.assets sync

# Export all icons AND UI elements to your current project folder
python -m exo_inventory.assets export ./assets
```

---

## 📜 License & Acknowledgments

- **Icons**: Provided by [Jemsire](https://minecraftallimages.jemsire.com).
- **Player Heads**: Powered by [mc-heads.net](https://mc-heads.net).
- **Core Developers**: [zKauaFerreira](https://github.com/zKauaFerreira).

---

_Maintained with ❤️ for the Minecraft Discord community._
