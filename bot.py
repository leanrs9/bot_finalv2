import discord
import json
from discord.ui import Button, View

# Cargar inventario desde JSON
with open("inventario.json", "r") as f:
    INVENTARIOS = json.load(f)

CANAL_IDS = {
    1379491898598752408: "Armario Recolectores",
    1379491923743477851: "Armario Armeros",
    1381444949039648848: "Armario Almacén",
    1381444864234885220: "Armario Altos Cargos" 

}

EMOJIS = {
    "Pistolas 9mm": "🔫",
    "Cuchillos": "🔪",
    "Radios": "📻",
    "Chalecos": "🦺",
    "Balas 9mm": "💥",
    "Pistolas .50": "🔫",
    "Revolvers": "🔫",
    "Balas de .50": "💥",
    "Balas de Revolver": "💥",
    "Coca": "🍃",
    "Purple Kush": "🍃",
    "Amapolas": "🍃",
    "Amnesia Haze": "🍃",
    "Peyotes": "🌲",
    "Coca Procesada": "🌿",
    "Purple Procesada": "🌿",
    "Amapolas Procesada": "🌿",
    "Amnesia Procesada": "🌿",
    "Dinero": "💵",
    "Dinero Negro": "💴",
    "Metal": "⚙️"
}

def guardar_inventario():
    with open("inventario.json", "w") as f:
        json.dump(INVENTARIOS, f, indent=4)

def crear_embed(canal_id):
    inventario = INVENTARIOS[str(canal_id)]
    embed = discord.Embed(title=f"📦 {CANAL_IDS[canal_id]} 📦", color=0x8A2BE2)
    for item, cantidad in inventario.items():
        embed.add_field(name=f"{EMOJIS.get(item, '')} {item}",
                        value=f"__**{cantidad}**__ unidades",
                        inline=True)
    embed.set_footer(text="💜🤍 BlackJacks Riders 🤍💜")
    return embed

class BotonItem(discord.ui.Button):
    def __init__(self, item, delta, canal_id, row):
        cantidad = abs(delta)
        signo = "💚" if delta > 0 else "💔"
        item_emoji = EMOJIS.get(item, "")
        label = f"{signo} {item_emoji} ({cantidad})"
        style = discord.ButtonStyle.primary
        super().__init__(label=label, style=style, row=row)
        self.item = item
        self.delta = delta
        self.canal_id = canal_id

    async def callback(self, interaction: discord.Interaction):
        inventario = INVENTARIOS[str(self.canal_id)]
        actual = inventario.get(self.item, 0)
        nuevo_valor = max(0, actual + self.delta)
        inventario[self.item] = nuevo_valor
        guardar_inventario()
        nuevo_embed = crear_embed(self.canal_id)
        await interaction.response.edit_message(embed=nuevo_embed, view=self.view)
        accion = "dejó" if self.delta > 0 else "sacó"
        emoji = EMOJIS.get(self.item, "")
        cantidad = abs(self.delta)
        await interaction.channel.send(
            f"**{interaction.user.mention}** {accion} {cantidad} {emoji} en el armario ({nuevo_valor})."
        )

class Botones(View):

    def __init__(self, canal_id):
        super().__init__(timeout=None)
        controles = [("Pistolas 9mm", [1, -1]),
                     ("Balas 9mm", [80, -80, 120, -120, 1000]),
                     ("Chalecos", [1, -1, 5, -5]),
                     ("Radios", [1, -1])]
        if canal_id != 1379491923743477851:
            controles.append(("Cuchillos", [1, -1]))

        row = 0
        col_count = 0
        for item, cambios in controles:
            for delta in cambios:
                if col_count >= 5:
                    row += 1
                    col_count = 0
                self.add_item(
                    BotonItem(item, delta, canal_id=canal_id, row=row))
                col_count += 1

class StockBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f'✅ Bot conectado como {self.user}')
        for canal_id in CANAL_IDS:
            canal = self.get_channel(canal_id)
            if canal:
                embed = crear_embed(canal_id)
                if canal_id in [1381444949039648848, 1381444864234885220]:
                    await canal.send(embed=embed)  
                else:
                    await canal.send(embed=embed, view=Botones(canal_id))  
            else:
                print(f'❌ No encontré el canal con ID: {canal_id}')

bot = StockBot()
