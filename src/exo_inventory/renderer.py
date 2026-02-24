import discord
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
import os
from .assets import AssetsManager

# Minecraft Standard Constants
SCALE = 4
SLOT_SIZE = 16
SLOT_STEP = 18

class InventoryRenderer:
    def __init__(self, assets_dir):
        self.assets = AssetsManager(assets_dir)
        self.session = None
        self._initialized = False
        
        # Default Minecraft GUI Layout (Modern)
        # Coordinates in pixels (unscaled)
        self.layout = {
            "armor": {
                "helmet": (8, 8),
                "chestplate": (8, 26),
                "leggings": (8, 44),
                "boots": (8, 62)
            },
            "offhand": (77, 62),
            "inventory_start": (8, 84),
            "hotbar_start": (8, 142),
            "char_box": {"x": 26, "y": 8, "w": 51, "h": 72}
        }

    async def initialize(self):
        if not self._initialized:
            await self.assets.initialize()
            self._initialized = True

    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Closes the underlying aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_player_render(self, uuid, render_type="body", size=400, angle=None):
        """
        Fetches player render from mc-heads.net.
        render_type: 'body', 'head', 'avatar', 'player'
        angle: optional rotation angle for body renders
        """
        url = f"https://mc-heads.net/{render_type}/{uuid}/{size}"
        if angle is not None:
            url += f"/{angle}"
            
        session = await self.get_session()
        try:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    return Image.open(io.BytesIO(await resp.read())).convert("RGBA")
        except: return None

    async def fetch_player_body(self, uuid):
        # Legacy support
        return await self.get_player_render(uuid, "body", 400)

    def _get_font(self):
        try:
            # Common paths
            paths = [
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "C:\\Windows\\Fonts\\arialbd.ttf",
                "C:\\Windows\\Fonts\\tahomabd.ttf"
            ]
            for p in paths:
                if os.path.exists(p):
                    return ImageFont.truetype(p, 22)
        except: pass
        return ImageFont.load_default()

    async def draw_item(self, img, draw, font, item_id, count, x, y, empty_type=None):
        """Draws an item at specific coordinates."""
        rx, ry = x * SCALE, y * SCALE
        
        if not item_id or item_id in ["minecraft:air", "air"]:
            if empty_type:
                e_icon = self.assets.get_ui_asset(f"empty_{empty_type}")
                if e_icon:
                    e_rendered = e_icon.resize((SLOT_SIZE * SCALE, SLOT_SIZE * SCALE), Image.Resampling.NEAREST)
                    img.paste(e_rendered, (rx, ry), e_rendered)
            return

        icon = await self.assets.get_icon(item_id)
        if icon:
            target_size = SLOT_SIZE * SCALE
            resample = Image.Resampling.NEAREST if icon.width <= 32 else Image.Resampling.LANCZOS
            icon_rendered = icon.resize((target_size, target_size), resample)
            img.paste(icon_rendered, (rx, ry), icon_rendered)
            
            if count > 1:
                txt = str(count)
                tw = draw.textlength(txt, font=font)
                tx, ty = rx + (SLOT_SIZE * SCALE) - tw - 4, ry + (SLOT_SIZE * SCALE) - 24
                # Shadow
                draw.text((tx + 2, ty + 2), txt, fill=(0, 0, 0, 180), font=font)
                draw.text((tx, ty), txt, fill=(255, 255, 255, 255), font=font)

    async def render_custom(self, items_map, background=None, player_uuid=None, width=176, height=166):
        """
        Renders a custom grid or inventory.
        items_map: List of dicts [{'id': 'id', 'count': 1, 'x': 8, 'y': 8, 'empty': 'helmet'}]
        background: Image object, color tuple (R,G,B,A), or None (fully transparent)
        """
        await self.initialize()
        
        target_w, target_h = width * SCALE, height * SCALE
        
        # 1. Background Logic
        if isinstance(background, Image.Image):
            bg = background.convert("RGBA").resize((target_w, target_h), Image.Resampling.NEAREST)
        elif isinstance(background, (tuple, list)):
            bg = Image.new("RGBA", (target_w, target_h), background)
        else:
            # Default to transparent
            bg = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        
        draw = ImageDraw.Draw(bg)
        font = self._get_font()

        # 2. Optional Player Body
        if player_uuid:
            body = await self.fetch_player_body(player_uuid)
            if body:
                c = self.layout["char_box"]
                target_h = int(c["h"] * SCALE * 0.95)
                ratio = target_h / body.height
                target_w = int(body.width * ratio)
                body_hd = body.resize((target_w, target_h), Image.Resampling.LANCZOS)
                bx, by = c["x"] * SCALE, c["y"] * SCALE
                bw, bh = c["w"] * SCALE, c["h"] * SCALE
                bg.paste(body_hd, (bx + (bw - target_w) // 2, by + (bh - target_h) // 2), body_hd)

        # 3. Draw Items
        for item in items_map:
            await self.draw_item(
                bg, draw, font, 
                item.get('id'), 
                item.get('count', 1), 
                item.get('x'), 
                item.get('y'), 
                item.get('empty')
            )

        output = io.BytesIO()
        bg.save(output, format="PNG")
        output.seek(0)
        return discord.File(fp=output, filename="render.png")

    async def render_player(self, player_data):
        """High-level helper for standard MC player data."""
        await self.initialize()
        
        # 1. Load background with solid fallback
        bg_path = os.path.join(self.assets.cache_dir, "inventory_bg.png")
        # Standard Minecraft GUI size
        w, h = 176, 166
        
        # Base solid color (ignoring transparency by filling the canvas)
        final_bg = Image.new("RGBA", (w * SCALE, h * SCALE), (198, 198, 198, 255))
        
        if os.path.exists(bg_path):
            try:
                gui_img = Image.open(bg_path).convert("RGBA")
                # If it's smaller than 176x166, we paste it at (0,0) on the final_bg
                # But we must scale it first
                gh = gui_img.height
                gw = gui_img.width
                
                # We resize the UI image to match our scale
                # If it's shorter than 166, it will just cover the top part
                gui_scaled = gui_img.resize((gw * SCALE, gh * SCALE), Image.Resampling.NEAREST)
                final_bg.paste(gui_scaled, (0, 0), gui_scaled)
            except: pass

        items = []
        
        # Armor
        armor_map = {39: "helmet", 38: "chestplate", 37: "leggings", 36: "boots"}
        for slot_id, name in armor_map.items():
            item = next((a for a in player_data.get('armor', []) if a and a.get('slot') == slot_id), None)
            x, y = self.layout["armor"][name]
            items.append({
                'id': item.get('id') if item else None,
                'count': item.get('count', 1) if item else 1,
                'x': x, 'y': y, 'empty': name
            })

        # Offhand
        oh = player_data.get('off_hand')
        ox, oy = self.layout["offhand"]
        items.append({'id': oh.get('id') if oh else None, 'count': oh.get('count', 1) if oh else 1, 'x': ox, 'y': oy, 'empty': 'shield'})

        # Inventory
        start_x, start_y = self.layout["inventory_start"]
        for row in range(3):
            for col in range(9):
                slot_id = 9 + row * 9 + col
                item = next((i for i in player_data.get('main_inventory', []) if i and i.get('slot') == slot_id), None)
                items.append({
                    'id': item.get('id') if item else None,
                    'count': item.get('count', 1) if item else 1,
                    'x': start_x + col * SLOT_STEP,
                    'y': start_y + row * SLOT_STEP
                })

        # Hotbar
        sx, sy = self.layout["hotbar_start"]
        for col in range(9):
            item = next((i for i in player_data.get('hotbar', []) if i and i.get('slot') == col), None)
            items.append({
                'id': item.get('id') if item else None,
                'count': item.get('count', 1) if item else 1,
                'x': sx + col * SLOT_STEP,
                'y': sy
            })

        return await self.render_custom(items, background=final_bg, player_uuid=player_data['uuid'])
