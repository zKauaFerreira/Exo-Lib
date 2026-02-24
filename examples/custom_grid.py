import asyncio
from exo_inventory import InventoryRenderer

async def main():
    renderer = InventoryRenderer(assets_dir=None)
    await renderer.initialize()

    # Custom mapping of items at specific coordinates
    # Coordinates are in MC GUI pixels (unscaled)
    # Background=None makes the result transparent
    items = [
        {"id": "diamond", "x": 10, "y": 10, "count": 64},
        {"id": "emerald", "x": 30, "y": 10, "count": 12},
        {"id": "netherite_ingot", "x": 50, "y": 10}
    ]

    print("👻 Rendering custom transparent grid...")
    
    # 100x50 transparent canvas
    render_file = await renderer.render_custom(
        items, 
        width=100, 
        height=50, 
        background=None 
    )
    
    with open("output/custom_transparent.png", "wb") as f:
        f.write(render_file.fp.read())
        
    print("✅ Transparent grid saved to examples/output/custom_transparent.png")
    await renderer.close()

if __name__ == "__main__":
    asyncio.run(main())
