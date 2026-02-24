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

## 🖼️ Visual Previews

|                                                Standard Inventory                                                |                                            Custom Transparent Grid                                             |
| :--------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------: |
| ![Standard](https://raw.githubusercontent.com/zKauaFerreira/Exo-Lib/main/examples/output/standard_inventory.png) | ![Custom](https://raw.githubusercontent.com/zKauaFerreira/Exo-Lib/main/examples/output/custom_transparent.png) |

---

## 🚀 Installation

Install the library directly from your local path or git:

```bash
# Git installation (Recommended)
pip install git+https://github.com/zKauaFerreira/Exo-Lib.git
```

> **Note:** The library already comes with **1400+ Minecraft icons and UI assets** bundled in the package. You can start rendering immediately after installation!

---

## ⚡ Quick Start (Plug & Play)

### 1. Minimalistic Rendering

Since assets are bundled, you don't even need to provide a path!

```python
import asyncio
from exo_inventory import InventoryRenderer

async def main():
    # USES BUILT-IN ASSETS AUTOMATICALLY
    renderer = InventoryRenderer()
    await renderer.initialize()

    player_data = {
        "uuid": "caf29aa7-b3f6-494f-b44f-66cdd3fb9a42",
        "armor": [{"id": "diamond_helmet", "slot": 39}],
        "hotbar": [{"id": "netherite_sword", "slot": 0}],
        "main_inventory": [],
        "off_hand": {"id": "shield"}
    }

    render = await renderer.render_player(player_data)
    # Save or send to Discord...

    await renderer.close()

asyncio.run(main())
```

---

## 📂 Examples Folder

We provided a dedicated `examples/` directory in our repository to help you get started with common use cases.

- `standard_inventory.py`: Demonstrates standard player inventory rendering with the requested skin.
- `custom_grid.py`: Shows how to create 100% custom grids with transparent backgrounds.
- `manage_assets.py`: Advanced usage: how to sync assets to a custom external folder instead of using the library internal one.

---

## 🛠️ Advanced Usage

### 🎨 Customizing Asset Locations

If you want to manage your icons in a specific shared folder across multiple projects:

```python
# Pass a path to use an external cache
assets = AssetsManager("./shared_assets")
renderer = InventoryRenderer(assets_dir="./shared_assets")
```

### 🧩 Custom Layouts

```python
# background=None generates a transparent PNG
image = await renderer.render_custom(
    items_map=[{"id": "apple", "x": 10, "y": 10}],
    width=100,
    height=100,
    background=None
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
