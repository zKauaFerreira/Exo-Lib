import aiohttp
import json
import os
import io
import asyncio
import zipfile
import shutil
from PIL import Image

class AssetsManager:
    """Manages Minecraft icons from Jemsire and UI assets (trims, backgrounds)."""
    
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            # Default to an internal 'data' folder inside the package
            cache_dir = os.path.join(os.path.dirname(__file__), "data")
            
        self.base_url = "https://minecraftallimages.jemsire.com"
        self.version_url = "https://raw.githubusercontent.com/TinyTank800/MinecraftAllImages/refs/heads/main/version.json"
        self.github_assets_url = "https://raw.githubusercontent.com/PrismarineJS/minecraft-assets/master/data/1.17.1/items"
        self.remote_repo_url = "https://raw.githubusercontent.com/zKauaFerreira/Exo-Lib/main/src/exo_inventory/data"
        
        # Centralized Asset Repositories (for customization)
        self.remote_ui_assets = {
            "empty_helmet.png": f"{self.remote_repo_url}/ui/empty_helmet.png",
            "empty_chestplate.png": f"{self.remote_repo_url}/ui/empty_chestplate.png",
            "empty_leggings.png": f"{self.remote_repo_url}/ui/empty_leggings.png",
            "empty_boots.png": f"{self.remote_repo_url}/ui/empty_boots.png",
            "empty_shield.png": f"{self.remote_repo_url}/ui/empty_shield.png",
            "inventory_bg.png": f"{self.remote_repo_url}/inventory_bg.png",
            "jemsire_index.json": f"{self.remote_repo_url}/jemsire_index.json"
        }

        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "jemsire_index.json")
        self.versions_dir = os.path.join(cache_dir, "versions")
        self.ui_dir = os.path.join(cache_dir, "ui")
        
        try:
            os.makedirs(self.ui_dir, exist_ok=True)
            os.makedirs(self.versions_dir, exist_ok=True)
        except:
            # Might be in a read-only environment like site-packages
            pass
        
        self.versions = ["1.21.10", "1.21.6", "1.21.5", "1.21.4", "1.20.6", "1.19.4", "1.18.2", "1.17.1", "1.16.5", "1.15.2", "1.14.4", "1.13.2"]
        self.index = {}
        self.path_cache = {}
        self.local_version = None
        self._ready = False

    async def initialize(self, force_sync=False):
        """Loads index and checks for updates."""
        print(f"📦 [Assets] Initializing using directory: {self.cache_dir}")
        needs_rebuild = force_sync
        
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    data = json.load(f)
                    self.index = data.get("index", {})
                    self.local_version = data.get("version", "")
            except:
                needs_rebuild = True
        else:
            needs_rebuild = True

        async with aiohttp.ClientSession() as session:
            try:
                # Always ensure UI assets exist
                await self._sync_ui_assets(session)
                
                if not force_sync:
                    async with session.get(self.version_url, timeout=10) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            remote_version = json.loads(text).get("message", "")
                            if remote_version != self.local_version:
                                self.local_version = remote_version
                                needs_rebuild = True
                            elif not os.path.exists(self.versions_dir) or not os.listdir(self.versions_dir):
                                needs_rebuild = True
            except Exception as e:
                print(f"⚠️ [Assets] Update check failed: {e}")

        if needs_rebuild:
            await self.full_sync()
        else:
            self._ready = True

    async def _sync_ui_assets(self, session):
        """Syncs the empty armor slot icons, background and index from remote repos."""
        for name, url in self.remote_ui_assets.items():
            if "empty" in name:
                path = os.path.join(self.ui_dir, name)
            else:
                path = os.path.join(self.cache_dir, name)
                
            if not os.path.exists(path) or os.path.getsize(path) < 100:
                print(f"📥 [Assets] Syncing remote asset: {name}")
                try:
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            content = await resp.read()
                            with open(path, "wb") as f:
                                f.write(content)
                except Exception as e:
                    print(f"⚠️ [Assets] Failed sync for {name}: {e}")

    async def build_index_from_web(self, session):
        """Reconstructs item->version mapping using official web data."""
        print("📂 [Assets] Managing gallery metadata...")
        temp_map = {}
        
        # 1. Base Manifest
        try:
            async with session.get(f"{self.base_url}/manifest.json", timeout=10) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    if text.strip().startswith("{"):
                        data = json.loads(text)
                        for item in data.get("images", []):
                            name = item.replace(".png", "").lower()
                            temp_map[name] = []
        except: pass

        # 2. Changes per version (old to new, so new prevails)
        for version in reversed(self.versions):
            url = f"{self.base_url}/images/{version}/changes.json"
            try:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        if text.strip().startswith("{"):
                            data = json.loads(text)
                            items = data.get("added", []) + data.get("modified", [])
                            for item in items:
                                name = item.replace(".png", "").lower()
                                if name not in temp_map: temp_map[name] = []
                                # Add to start so vers[0] is always the most recent
                                temp_map[name].insert(0, version)
            except: pass

        final_index = {}
        for name, vers in temp_map.items():
            if vers:
                final_index[name] = vers[0]
            else:
                final_index[name] = "1.21.10" # Default
        
        return final_index

    async def full_sync(self):
        print("🚀 [Assets] Initiating full repository synchronization...")
        if os.path.exists(self.versions_dir):
            shutil.rmtree(self.versions_dir)
        os.makedirs(self.versions_dir, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            sem = asyncio.Semaphore(4)
            async def download_v(v):
                async with sem:
                    url = f"{self.base_url}/images/{v}.zip"
                    print(f"📦 [Assets] Download: {v}.zip")
                    try:
                        async with session.get(url, timeout=300) as resp:
                            if resp.status == 200:
                                b = await resp.read()
                                with zipfile.ZipFile(io.BytesIO(b)) as z:
                                    z.extractall(os.path.join(self.versions_dir, v))
                                print(f"✅ [Assets] Extracted: {v}")
                    except Exception as e:
                        print(f"❌ [Assets] Sync failed for {v}: {e}")

            await asyncio.gather(*[download_v(v) for v in self.versions])
            self.index = await self.build_index_from_web(session)

        with open(self.cache_file, "w") as f:
            json.dump({"version": self.local_version, "index": self.index}, f)
        
        total_mb = sum(os.path.getsize(os.path.join(r, f)) for r, d, fs in os.walk(self.versions_dir) for f in fs) / (1024*1024)
        print(f"✨ [Assets] Mirror ready! {len(self.index)} items | {total_mb:.2f} MB")
        self._ready = True

    async def get_icon(self, item_id):
        if not self._ready: await self.initialize()
        clean_name = item_id.split(":")[-1].lower()
        version = self.index.get(clean_name)
        if not version: return None

        cache_key = f"{version}:{clean_name}"
        if cache_key in self.path_cache:
            return Image.open(self.path_cache[cache_key]).convert("RGBA")

        v_dir = os.path.join(self.versions_dir, version)
        if not os.path.exists(v_dir): return None

        # Recursive search to handle nested folders in ZIPs
        for root, _, files in os.walk(v_dir):
            filename = f"{clean_name}.png"
            if filename in files:
                path = os.path.join(root, filename)
                self.path_cache[cache_key] = path
                try:
                    return Image.open(path).convert("RGBA")
                except:
                    pass
        return None

    def get_ui_asset(self, name):
        # Checks both UI dir and Root dir (for bg)
        paths = [
            os.path.join(self.ui_dir, f"{name}.png" if not name.endswith(".png") else name),
            os.path.join(self.cache_dir, f"{name}.png" if not name.endswith(".png") else name)
        ]
        for p in paths:
            if os.path.exists(p):
                return Image.open(p).convert("RGBA")
        return None

    async def download_assets(self, items_list):
        """Ensures a list of item icons are downloaded in the local cache."""
        if not self._ready: await self.initialize()
        tasks = [self.get_icon(item_id) for item_id in items_list]
        return await asyncio.gather(*tasks)

    async def export_assets(self, target_dir, items_list=None, include_ui=False):
        """
        Copies assets from the internal cache to a specific directory.
        If items_list is None, it exports ALL known icons (heavy!).
        """
        if not self._ready: await self.initialize()
        os.makedirs(target_dir, exist_ok=True)
        
        # 1. Export UI Assets
        if include_ui:
            ui_export = os.path.join(target_dir, "ui")
            os.makedirs(ui_export, exist_ok=True)
            for name in self.remote_ui_assets.keys():
                src = os.path.join(self.ui_dir if "empty" in name else self.cache_dir, name)
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(ui_export if "empty" in name else target_dir, name))

        # 2. Export Icons
        to_export = items_list if items_list else self.index.keys()
        for item_id in to_export:
            clean_name = item_id.split(":")[-1].lower()
            img = await self.get_icon(clean_name)
            if img:
                # We use the path_cache to find where the file actually is
                version = self.index.get(clean_name)
                cache_key = f"{version}:{clean_name}"
                src_path = self.path_cache.get(cache_key)
                if src_path:
                    shutil.copy2(src_path, os.path.join(target_dir, f"{clean_name}.png"))
