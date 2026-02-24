import asyncio
import os
from exo_inventory import AssetsManager

async def main():
    # You can specify a separate folder for your project's assets
    project_assets = "./project_data"
    
    print(f"📥 Sycing assets to local project folder: {project_assets}")
    manager = AssetsManager(project_assets)
    
    await manager.initialize()
    
    # This downloads the index and all missing icons from the Jemsire API
    await manager.full_sync()
    
    # You can also use the CLI for this:
    # python -m exo_inventory.assets sync ./project_data
    
    print(f"✅ Assets synced! Total items in index: {len(manager.index)}")
    print(f"Icons stored in: {os.path.join(project_assets, 'versions')}")

if __name__ == "__main__":
    asyncio.run(main())
