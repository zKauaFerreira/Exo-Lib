import asyncio
import os
from exo_inventory import InventoryRenderer

async def main():
    # When assets_dir is None, it uses the built-in assets from the library
    renderer = InventoryRenderer(assets_dir=None)
    await renderer.initialize()

    # Data for the specific skin requested
    # UUID: caf29aa7-b3f6-494f-b44f-66cdd3fb9a42
    player_uuid = "caf29aa7-b3f6-494f-b44f-66cdd3fb9a42"
    
    player_data = {
        "uuid": player_uuid,
        "armor": [
            {"id": "minecraft:netherite_helmet", "slot": 39},
            {"id": "minecraft:netherite_chestplate", "slot": 38}
        ],
        "hotbar": [
            {"id": "minecraft:netherite_sword", "slot": 0},
            {"id": "minecraft:enchanted_golden_apple", "slot": 1}
        ],
        "main_inventory": [],
        "off_hand": {"id": "minecraft:totem_of_undying"}
    }

    print(f"🎨 Rendering inventory for {player_uuid} using built-in assets...")
    
    render_file = await renderer.render_player(player_data)
    
    output_path = "output/standard_inventory.png"
    with open(output_path, "wb") as f:
        f.write(render_file.fp.read())
    
    print(f"✅ Render saved to examples/{output_path}")
    await renderer.close()

if __name__ == "__main__":
    asyncio.run(main())
