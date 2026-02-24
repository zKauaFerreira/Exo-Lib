import asyncio
import os
import shutil
from exo_inventory import AssetsManager, InventoryRenderer

# Color constants for console
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

async def test_all():
    assets_dir = os.path.abspath("./test_assets")
    export_dir = os.path.abspath("./exported_resources")
    
    # Do NOT delete assets_dir to test cache persistence
    os.makedirs(assets_dir, exist_ok=True)
    if os.path.exists(export_dir):
        shutil.rmtree(export_dir)
    os.makedirs(export_dir, exist_ok=True)
    
    print(f"{BLUE}🚀 Starting Library Integration Tests...{RESET}")
    
    # 1. Initialize Assets
    print(f"\n{GREEN}1. Initializing AssetsManager...{RESET}")
    assets = AssetsManager(assets_dir)
    await assets.initialize()
    print("✅ Assets initialized.")

    # 2. Render Player (Standard)
    print(f"\n{GREEN}2. Testing standard Player Inventory rendering...{RESET}")
    renderer = InventoryRenderer(assets_dir)
    
    player_data = {
        "uuid": "7be0ee8d-389a-44c9-a9bf-513f7960bcbf", # Example UUID
        "armor": [
            {"id": "minecraft:diamond_helmet", "slot": 39},
            {"id": "minecraft:diamond_chestplate", "slot": 38}
        ],
        "hotbar": [
            {"id": "minecraft:netherite_sword", "slot": 0, "count": 1},
            {"id": "minecraft:apple", "slot": 1, "count": 64}
        ],
        "main_inventory": [
            {"id": "minecraft:grass_block", "slot": 9, "count": 20}
        ],
        "off_hand": {"id": "minecraft:shield"}
    }
    
    try:
        render_file = await renderer.render_player(player_data)
        with open("test_player_inventory.png", "wb") as f:
            f.write(render_file.fp.read())
        print("✅ Player inventory rendered to: test_player_inventory.png")
    except Exception as e:
        print(f"❌ Error rendering player: {e}")

    # 3. Custom Grid Rendering (Transparent)
    print(f"\n{GREEN}3. Testing Custom Grid (Transparent Background)...{RESET}")
    custom_items = [
        {"id": "diamond_pickaxe", "x": 10, "y": 10, "count": 1},
        {"id": "gold_block", "x": 30, "y": 10, "count": 9},
        {"id": "bedrock", "x": 10, "y": 30}
    ]
    
    # Transparent background (None)
    render_custom = await renderer.render_custom(
        custom_items, 
        width=100, 
        height=100, 
        background=None 
    )
    with open("test_custom_grid.png", "wb") as f:
        f.write(render_custom.fp.read())
    print("✅ Custom grid rendered to: test_custom_grid.png")

    # 4. Advanced Player Rendering (Poses)
    print(f"\n{GREEN}4. Testing 3D Player Poses...{RESET}")
    body_45 = await renderer.get_player_render(player_data["uuid"], render_type="body", angle=45)
    if body_45:
        body_45.save("test_player_45deg.png")
        print("✅ 45-degree player body saved to: test_player_45deg.png")
    
    head = await renderer.get_player_render(player_data["uuid"], render_type="head", size=128)
    if head:
        head.save("test_player_head.png")
        print("✅ Player head (128px) saved to: test_player_head.png")

    # 5. Asset Exporting
    print(f"\n{GREEN}5. Testing Asset Export System...{RESET}")
    items_to_export = ["diamond_sword", "ender_pearl", "golden_apple"]
    await assets.download_assets(items_to_export)
    await assets.export_assets(target_dir=export_dir, items_list=items_to_export, include_ui=True)
    print(f"✅ Exported assets to {export_dir}")

    # 6. Cleanup sessions
    await renderer.close()
    print(f"\n{BLUE}✨ All library tests completed successfully!{RESET}")

if __name__ == "__main__":
    asyncio.run(test_all())
