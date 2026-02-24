import asyncio
import os
import sys
from .assets import AssetsManager

async def run_cli():
    args = sys.argv[1:]
    # Default internal path inside the library
    internal_path = os.path.join(os.path.dirname(__file__), "data")
    
    if not args or args[0] == "sync":
        path = args[1] if len(args) > 1 else internal_path
        print(f"🔄 Syncing assets to: {os.path.abspath(path)}")
        manager = AssetsManager(path)
        await manager.initialize()
        await manager.full_sync()
        print("\n✅ Assets updated!")
        
    elif args[0] == "export":
        target = args[1] if len(args) > 1 else "./exo_assets"
        print(f"📦 Exporting assets to: {os.path.abspath(target)}")
        manager = AssetsManager(internal_path)
        await manager.initialize()
        await manager.export_assets(target, include_ui=True)
        print(f"\n✅ Assets exported to {target}")
    else:
        print("Usage:")
        print("  python -m exo_inventory sync [path]    - Syncs assets to library or path")
        print("  python -m exo_inventory export [path]  - Exports assets to a folder")

if __name__ == "__main__":
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        pass
