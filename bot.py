import discord
from discord.ext import commands
import asyncio
import json
import os
 
# ======================
# ตั้งค่า Bot
# ======================
intents = discord.Intents.default()
intents.message_content = True
 
bot = commands.Bot(command_prefix="!", intents=intents)
 
DATA_FILE = "data.json"
 
MAX_SWORD = 10
MAX_KEY = 395
 
# ======================
# โหลด / บันทึก
# ======================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)
 
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)
 
data = load_data()
 
# ======================
# Progress Bar
# ======================
def make_bar(current, max_val, length=10):
    filled = int((current / max_val) * length)
    return "█" * filled + "░" * (length - filled)
 
# ======================
# Task ระบบนับ
# ======================
async def sword_task(user_id):
    while True:
        await asyncio.sleep(60)
 
        user = data.get(user_id, {})
        current = user.get("sword", 0)
 
        if current >= MAX_SWORD:
            try:
                embed = discord.Embed(
                    description="⚔️ ดาบเต็มแล้ว! `██████████` 10/10",
                    color=0x7F77DD
                )
                await bot.get_user(int(user_id)).send(embed=embed)
            except:
                pass
            break
 
        current += 1
        data[user_id]["sword"] = current
        save_data(data)
 
        if current in [8, 9]:
            try:
                embed = discord.Embed(
                    description=f"⚠️ ดาบใกล้เต็ม `{make_bar(current, 10)}` {current}/10",
                    color=0xEF9F27
                )
                await bot.get_user(int(user_id)).send(embed=embed)
            except:
                pass
 
 
async def key_task(user_id):
    while True:
        await asyncio.sleep(60)
 
        user = data.get(user_id, {})
        current = user.get("key", 0)
 
        if current >= MAX_KEY:
            try:
                embed = discord.Embed(
                    description="🔑 กุญแจเต็มแล้ว! `██████████` 395/395",
                    color=0x1D9E75
                )
                await bot.get_user(int(user_id)).send(embed=embed)
            except:
                pass
            break
 
        current += 1
        data[user_id]["key"] = current
        save_data(data)
 
        if current in [350, 380]:
            try:
                embed = discord.Embed(
                    description=f"⚠️ กุญแจใกล้เต็ม `{make_bar(current, 395)}` {current}/395",
                    color=0xEF9F27
                )
                await bot.get_user(int(user_id)).send(embed=embed)
            except:
                pass
 
# ======================
# Modals
# ======================
class SwordModal(discord.ui.Modal, title="⚔️ เริ่มนับดาบ"):
    current = discord.ui.TextInput(
        label="ดาบปัจจุบัน (0–10)",
        placeholder="กรอกตัวเลข เช่น 0",
        max_length=2
    )
 
    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = int(self.current.value)
            if not (0 <= val <= 10):
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                embed=discord.Embed(description="❌ กรุณากรอกตัวเลข 0–10", color=0xE24B4A),
                ephemeral=True
            )
            return
 
        user_id = str(interaction.user.id)
        data[user_id] = data.get(user_id, {})
        data[user_id]["sword"] = val
        save_data(data)
        asyncio.create_task(sword_task(user_id))
 
        embed = discord.Embed(title="⚔️ เริ่มนับดาบแล้ว", color=0x7F77DD)
        embed.add_field(
            name="ความคืบหน้า",
            value=f"`{make_bar(val, 10)}` {val}/10",
            inline=False
        )
        embed.set_footer(text="บอทจะแจ้งเตือนเมื่อใกล้เต็ม")
        await interaction.response.send_message(embed=embed, ephemeral=True)
 
 
class KeyModal(discord.ui.Modal, title="🔑 เริ่มนับกุญแจ"):
    current = discord.ui.TextInput(
        label="กุญแจปัจจุบัน (0–395)",
        placeholder="กรอกตัวเลข เช่น 0",
        max_length=3
    )
 
    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = int(self.current.value)
            if not (0 <= val <= 395):
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                embed=discord.Embed(description="❌ กรุณากรอกตัวเลข 0–395", color=0xE24B4A),
                ephemeral=True
            )
            return
 
        user_id = str(interaction.user.id)
        data[user_id] = data.get(user_id, {})
        data[user_id]["key"] = val
        save_data(data)
        asyncio.create_task(key_task(user_id))
 
        embed = discord.Embed(title="🔑 เริ่มนับกุญแจแล้ว", color=0x1D9E75)
        embed.add_field(
            name="ความคืบหน้า",
            value=f"`{make_bar(val, 395)}` {val}/395",
            inline=False
        )
        embed.set_footer(text="บอทจะแจ้งเตือนเมื่อใกล้เต็ม")
        await interaction.response.send_message(embed=embed, ephemeral=True)
 
# ======================
# Slash Commands
# ======================
@bot.tree.command(name="startsword", description="เริ่มนับดาบ")
async def startsword(interaction: discord.Interaction, current: int):
    if not (0 <= current <= 10):
        await interaction.response.send_message(
            embed=discord.Embed(description="❌ ค่าต้องอยู่ระหว่าง 0–10", color=0xE24B4A),
            ephemeral=True
        )
        return
 
    user_id = str(interaction.user.id)
    data[user_id] = data.get(user_id, {})
    data[user_id]["sword"] = current
    save_data(data)
    asyncio.create_task(sword_task(user_id))
 
    embed = discord.Embed(title="⚔️ เริ่มนับดาบแล้ว", color=0x7F77DD)
    embed.add_field(
        name="ความคืบหน้า",
        value=f"`{make_bar(current, 10)}` {current}/10",
        inline=False
    )
    embed.set_footer(text="บอทจะแจ้งเตือนเมื่อใกล้เต็ม")
    await interaction.response.send_message(embed=embed)
 
 
@bot.tree.command(name="startkey", description="เริ่มนับกุญแจ")
async def startkey(interaction: discord.Interaction, current: int):
    if not (0 <= current <= 395):
        await interaction.response.send_message(
            embed=discord.Embed(description="❌ ค่าต้องอยู่ระหว่าง 0–395", color=0xE24B4A),
            ephemeral=True
        )
        return
 
    user_id = str(interaction.user.id)
    data[user_id] = data.get(user_id, {})
    data[user_id]["key"] = current
    save_data(data)
    asyncio.create_task(key_task(user_id))
 
    embed = discord.Embed(title="🔑 เริ่มนับกุญแจแล้ว", color=0x1D9E75)
    embed.add_field(
        name="ความคืบหน้า",
        value=f"`{make_bar(current, 395)}` {current}/395",
        inline=False
    )
    embed.set_footer(text="บอทจะแจ้งเตือนเมื่อใกล้เต็ม")
    await interaction.response.send_message(embed=embed)
 
 
@bot.tree.command(name="status", description="เช็คสถานะ")
async def status(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user = data.get(user_id, {})
 
    if not user:
        await interaction.response.send_message(
            embed=discord.Embed(description="❌ ยังไม่ได้เริ่มนับอะไรเลย", color=0xE24B4A),
            ephemeral=True
        )
        return
 
    sword = user.get("sword", 0)
    key = user.get("key", 0)
 
    embed = discord.Embed(title="📊 สถานะของคุณ", color=0x534AB7)
    embed.add_field(
        name="⚔️ ดาบ",
        value=f"`{make_bar(sword, 10)}` {sword}/10",
        inline=False
    )
    embed.add_field(
        name="🔑 กุญแจ",
        value=f"`{make_bar(key, 395)}` {key}/395",
        inline=False
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
 
 
@bot.tree.command(name="stop", description="หยุดทั้งหมด")
async def stop(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
 
    if user_id in data:
        data.pop(user_id)
        save_data(data)
        embed = discord.Embed(description="🛑 หยุดนับทั้งหมดแล้ว", color=0xD85A30)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(
            embed=discord.Embed(description="❌ ยังไม่ได้เริ่ม", color=0xE24B4A),
            ephemeral=True
        )
 
# ======================
# ปุ่ม UI
# ======================
class ControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
 
    @discord.ui.button(label="⚔️ Start Sword", style=discord.ButtonStyle.primary)
    async def start_sword(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SwordModal())
 
    @discord.ui.button(label="🔑 Start Key", style=discord.ButtonStyle.success)
    async def start_key(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(KeyModal())
 
    @discord.ui.button(label="📊 Status", style=discord.ButtonStyle.secondary)
    async def status_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        user = data.get(user_id, {})
 
        if not user:
            await interaction.response.send_message(
                embed=discord.Embed(description="❌ ยังไม่ได้เริ่มนับอะไรเลย", color=0xE24B4A),
                ephemeral=True
            )
            return
 
        sword = user.get("sword", 0)
        key = user.get("key", 0)
 
        embed = discord.Embed(title="📊 สถานะของคุณ", color=0x534AB7)
        embed.add_field(
            name="⚔️ ดาบ",
            value=f"`{make_bar(sword, 10)}` {sword}/10",
            inline=False
        )
        embed.add_field(
            name="🔑 กุญแจ",
            value=f"`{make_bar(key, 395)}` {key}/395",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
 
    @discord.ui.button(label="🛑 Stop", style=discord.ButtonStyle.danger)
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
 
        if user_id in data:
            data.pop(user_id)
            save_data(data)
            await interaction.response.send_message(
                embed=discord.Embed(description="🛑 หยุดนับทั้งหมดแล้ว", color=0xD85A30),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(description="❌ ยังไม่ได้เริ่ม", color=0xE24B4A),
                ephemeral=True
            )
 
 
@bot.tree.command(name="panel", description="เปิดเมนูปุ่ม")
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚔️ Resource Tracker",
        description="ติดตามดาบและกุญแจของคุณแบบ real-time",
        color=0x7F77DD
    )
    embed.add_field(name="⚔️ ดาบ", value="สูงสุด 10", inline=True)
    embed.add_field(name="🔑 กุญแจ", value="สูงสุด 395", inline=True)
    embed.add_field(
        name="วิธีใช้",
        value="กด **Start Sword** หรือ **Start Key** แล้วกรอกค่าปัจจุบัน",
        inline=False
    )
    embed.set_footer(text="บอทจะ DM แจ้งเตือนเมื่อใกล้เต็มหรือเต็มแล้ว")
    await interaction.response.send_message(embed=embed, view=ControlView())
 
# ======================
# Ready
# ======================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")
 
# ======================
# RUN
bot.run(os.getenv("TOKEN"))