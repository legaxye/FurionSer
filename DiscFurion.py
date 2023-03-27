from nextcord import Intents
from nextcord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont
import random
import datetime
import os
import nextcord
import requests
import asyncio

user_balances = {}


CanalComandos = 1089045232315809902
CanalFarmear = 1089036406648754278
CanalDuelo = 1089036817111732315
CanalTienda = 1089036919213666365
CanalHistorialCompras = 1089038257133735967

CanalDotaUpdates = 1089052633538502707

CanalBienvenida = 1087117129121276124



class Principal(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.hourly_income.start()

    def cog_unload(self):
        self.hourly_income.cancel()

    @tasks.loop(hours=1)
    async def hourly_income(self):
        for member in self.bot.get_all_members():
            if not member.bot:
                if str(member.id) not in user_balances:
                    user_balances[str(member.id)] = 0
                user_balances[str(member.id)] += 100

    @hourly_income.before_loop
    async def before_hourly_income(self):
        await self.bot.wait_until_ready()

  
    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel = nextcord.utils.get(member.guild.text_channels, id=CanalBienvenida)
        if welcome_channel:
            await welcome_channel.send(f"Bienvenido {member.mention} al servidor!")
            await welcome_channel.send("https://i.imgur.com/NR9xVeY.png")
            

    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.command(name="Farm")
    @commands.has_any_role('Ver')
    async def hourly_coins(self, ctx):
        if ctx.channel.id  != CanalFarmear:  
            return
        if str(ctx.author.id) not in user_balances:
            user_balances[str(ctx.author.id)] = 0
        user_balances[str(ctx.author.id)] += 500
        await ctx.send(f"{ctx.author.mention}, has ganado 500 monedas. Tu nuevo balance es de {user_balances[str(ctx.author.id)]} monedas.")

    @hourly_coins.error
    async def hourly_coins_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time_left = round(error.retry_after / 60)
            await ctx.send(f"{ctx.author.mention}, debes esperar {time_left} minutos antes de usar este comando de nuevo.")   

    @commands.command(name="Monedas")
    async def balance(self, ctx):
        if ctx.channel.id  != CanalComandos:  
            return
        if str(ctx.author.id) not in user_balances:
            user_balances[str(ctx.author.id)] = 0
        await ctx.send(f"{ctx.author.mention}, tu balance actual es de {user_balances[str(ctx.author.id)]} monedas.")

    @commands.command(name="AddMonedas")
    @commands.has_permissions(administrator=True)
    async def add_coins(self, ctx, member: nextcord.Member, coins: int):
        if str(member.id) not in user_balances:
            user_balances[str(member.id)] = 0
        user_balances[str(member.id)] += coins
        await ctx.send(f"Se agregaron {coins} monedas a {member.mention}. Nuevo balance: {user_balances[str(member.id)]}")

    @commands.command(name="BorrarMonedas")
    @commands.has_permissions(administrator=True)
    async def remove_coins(self, ctx, member: nextcord.Member, coins: int):
        if str(member.id) not in user_balances:
            await ctx.send(f"{member.mention} no tiene un saldo registrado")
            return
        if user_balances[str(member.id)] < coins:
            user_balances[str(member.id)] = 0
            await ctx.send(f"{member.mention} no tiene suficientes monedas, por lo que ahora tiene {user_balances[str(member.id)]}")
            return
        user_balances[str(member.id)] -= coins
        await ctx.send(f"Se removieron {coins} monedas de {member.mention}. Nuevo balance: {user_balances[str(member.id)]}")
    
    @commands.command(name="ComprarRol")
    @commands.has_any_role('[Mito]', 'Ver')
    async def buy_temporary_role(self, ctx, role_name: str, duration: int):
        if ctx.channel.id != CanalTienda:  
            return

        OutChat = nextcord.utils.get(ctx.guild.text_channels, id=CanalHistorialCompras)
        allowed_roles = {"[Novato]": 1000, "[Aprendiz]": 2000, "[Maestro]": 4000,"[Veterano]":8000,"[Gladiador]":16000,"[Campeón]":32000} # dictionary of allowed roles and their prices

        if role_name not in allowed_roles:
            await ctx.send(f"El rol {role_name} no está disponible para comprar.")
            return

        role = nextcord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"No se encontró el rol {role_name}.")
            return

        cost = duration * allowed_roles[role_name]  
        user_id = str(ctx.author.id)

        if user_id not in user_balances or user_balances[user_id] < cost:
            await ctx.send("No tienes suficientes monedas para comprar este rol.")
            return

        await ctx.author.add_roles(role)
        user_balances[user_id] -= cost
        await OutChat.send(f"¡Felicidades! {ctx.author.mention} Ha comprado el rol {role_name} por {duration} Dias por {cost} monedas.")


        await asyncio.sleep(duration * 86400)
        await ctx.author.remove_roles(role)
        await ctx.send(f"Tu rol {role_name} temporal ha expirado.")




    @commands.cooldown(1, 180, commands.BucketType.user)
    @commands.command(name="Silenciar")
    @commands.has_any_role('[Mito]', 'Ver')
    async def mute(self,ctx,member:nextcord.Member,time:int):
        if ctx.channel.id  != CanalTienda :  
            return
        if time > 10:
            await ctx.send("No se puede silenciar por mas de 10 segundos a la vez.")
            return
        OutChat = nextcord.utils.get(ctx.guild.text_channels, id=CanalHistorialCompras)
        cost = time * 1000  
        user_id = str(ctx.author.id)

        if user_id not in user_balances or user_balances[user_id] < cost:
            await ctx.send("No tienes suficientes monedas para comprar esto.")
            return
        user_balances[user_id] -= cost
        timeout_duration = datetime.timedelta(seconds=time)
        await member.timeout(timeout=timeout_duration,  reason="no rason")
        await member.disconnect()
       
        await OutChat.send(f"{ctx.author.mention} compró TIMEOUT a {member.mention} por {time} segundos")
    
    @commands.cooldown(1, 1800, commands.BucketType.user)
    @commands.command(name="Desconectar")
    @commands.has_any_role('[Mito]', 'Ver')
    async def desconectar(self,ctx,member:nextcord.Member):
        if ctx.channel.id  != CanalTienda:  #Canal compras
            return
        OutChat = nextcord.utils.get(ctx.guild.text_channels, id=CanalHistorialCompras)
        cost =  1000  # Cantidad de monedas requeridas para comprar el rol temporal
        user_id = str(ctx.author.id)

        if user_id not in user_balances or user_balances[user_id] < cost:
            await ctx.send("No tienes suficientes monedas para comprar esto.")
            return
        user_balances[user_id] -= cost
        await member.disconnect()
        
        await OutChat.send(f"{ctx.author.mention} compró DESCONECTAR a {member.mention}.")
    
    @commands.command(name="CambiarApodo")
    @commands.has_any_role('[Mito]', 'Ver')
    async def cambiar_apodo(self,ctx, member: nextcord.Member, new_nickname: str,tipo: int):
        if ctx.channel.id  != CanalTienda :  #Canal compras
            return
        OutChat = nextcord.utils.get(ctx.guild.text_channels, id=CanalHistorialCompras)
        Intocable = nextcord.utils.get(ctx.guild.roles, name="Intocable")
        if Intocable in member.roles:
            await ctx.send("El usuario definido es Intocable.")
            return
        if tipo == 1:
            cost = 1000
        else:
            cost = 10000
        user_id = str(ctx.author.id)

        if user_id not in user_balances or user_balances[user_id] < cost:
            await ctx.send("No tienes suficientes monedas para comprar esto.")
            return
        user_balances[user_id] -= cost
        if tipo == 1:    
            await member.edit(nick=new_nickname)
            await OutChat.send(f"{ctx.author.mention} compró cambio de NickName.\nEl apodo de {member.mention} ha sido cambiado a {new_nickname} por 10 segundos")
            await asyncio.sleep(10)
            await member.edit(nick="")
        else:
            await member.edit(nick=new_nickname)
            await OutChat.send(f"{ctx.author.mention} compró cambio de NickName.\nEl apodo de {member.mention} ha sido cambiado a {new_nickname}")


    #Enviar Monedas
    @commands.command(name="TransferirMonedas")
    @commands.has_any_role('[Mito]', 'Ver')
    async def transfer_coins(self,ctx, member: nextcord.Member, coins: int):
        if ctx.channel.id  != CanalTienda:  #Canal Compras
            return
        OutChat = nextcord.utils.get(ctx.guild.text_channels, id=CanalHistorialCompras)
        if str(ctx.author.id) == str(member.id):
            await ctx.send(f"{ctx.author.mention} no te puedes enviar monedas a ti mismo")
            return
        if str(ctx.author.id) not in user_balances:
            user_balances[str(ctx.author.id)] = 0
        if str(member.id) not in user_balances:
            user_balances[str(member.id)] = 0
        if user_balances[str(ctx.author.id)] >= coins:
            user_balances[str(ctx.author.id)] -= coins
            user_balances[str(member.id)] += coins
            await OutChat.send(f"Se transfirieron {coins} monedas de {ctx.author.mention} a {member.mention}. Nuevo balance de {ctx.author.mention}: {user_balances[str(ctx.author.id)]}. Nuevo balance de {member.mention}: {user_balances[str(member.id)]}")
        else:
            await ctx.send(f"{ctx.author.mention} no tienes suficientes monedas para realizar esta transacción")
    
    @commands.command(name="VerMonedas")
    @commands.has_any_role('[Mito]', '[Semidiós]','[Héroe]','[Campeón]')
    async def check_balance(self, ctx, member: nextcord.Member):
        if ctx.channel.id  != CanalComandos:  #Canal comandos
            return
        #1087106845082128442 await ctx.send(f"{member.mention} tiene {user_balances[str(member.id)]} monedas.")
        if str(member.id) not in user_balances:
            user_balances[str(member.id)] = 0
        await ctx.send(f"{member.mention} tiene {user_balances[str(member.id)]} monedas.")

    @commands.cooldown(2, 600, commands.BucketType.user)
    @commands.command(name="Duelo")
    @commands.has_any_role('[Mito]', 'Ver')
    async def duelo(self, ctx, oponente: nextcord.Member, monedas: int):
        if ctx.channel.id  != CanalDuelo:  #Canal comandos
            return
        if monedas <= 0:
            await ctx.send("La cantidad de monedas debe ser mayor que 0")
            return
        if str(ctx.author.id) not in user_balances:
            user_balances[str(ctx.author.id)] = 0
        if str(oponente.id) not in user_balances:
            user_balances[str(oponente.id)] = 0

        if user_balances[str(ctx.author.id)] < monedas:
            await ctx.send(f"{ctx.author.mention} no tienes suficientes monedas para apostar {monedas}. Tu balance es {user_balances[str(ctx.author.id)]}")
            return
        await ctx.send(f"{oponente.mention}, {ctx.author.mention} te está retando a un duelo de cara o sello por {monedas} monedas. ¿Aceptas? Responde 'si' o 'no'.")

        # Esperar la respuesta del oponente
        def check(m):
            return m.author == oponente and m.content.lower() in ["si", "no"]

        try:
            respuesta = await self.bot.wait_for('message', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f"{oponente.mention} no ha respondido a tiempo. El duelo se cancela.")
            return

        if respuesta.content.lower() == "no":
            await ctx.send(f"{oponente.mention} ha rechazado el duelo.")
            return

        # Lanzar la moneda
        resultado = random.choice(["cara", "sello"])
        if resultado == "cara":
            ganador = ctx.author
            perdedor = oponente
        else:
            ganador = oponente
            perdedor = ctx.author

        # Actualizar los balances
        user_balances[str(ganador.id)] += monedas
        user_balances[str(perdedor.id)] -= monedas

        # Enviar el resultado
        await ctx.send(f"La moneda ha salido {resultado}. {ganador.mention} ha ganado {monedas} monedas y ahora tiene un balance de {user_balances[str(ganador.id)]}. {perdedor.mention} ha perdido {monedas} monedas y ahora tiene un balance de {user_balances[str(perdedor.id)]}.")

    @commands.command(name="Sumar")
    @commands.has_any_role('[Mito]', 'Ver')
    async def sumita(self, ctx, IDPartida: int):
        CrearImagen(IDPartida)
        with open('ImagenTotal.png', 'rb') as f:
            picture = nextcord.File(f)
        await ctx.send(file=picture)
    #@commands.command(name="obtener_id_canal")
    #async def obtener_id_canal(self, ctx):
    #    canal_id = ctx.channel.id
    #    await ctx.send(f"El ID del canal actual es: {canal_id}")

        
class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(1087106845082128442) # Reemplazar con el ID del canal de bienvenida
        embed = nextcord.Embed(title="¡Bienvenido!", description=f"{member.mention} se ha unido al servidor.", color=0x00ff00)
        await channel.send(embed=embed)
#End

intents = Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

#Informacion Dota2 7.32e

Heroes = {
    "ABADDON": {"NONE": "Tiempo de ataque base mejorado de 1,7 a 1,5 s"},
    "ALCHEMIST": {"MEZCLA INESTABLE": "Duración máxima del aturdimiento aumentada de 1,75/2,5/3,25/4 s a 2,2/2,8/3,4/4 s", 
                  "FURIA QUÍMICA": "Daño adicional por Cetro aumentado de 20 a 25"},
    "ANCIENT-APPARITION": {"TALENTOS": "Talento de nivel 10 aumentado de +200 a +300 de alcance de ataque para Toque Escalofriante\nTalento de nivel 15 aumentado de +200 a +300 de distancia de ruptura para Pies Fríos"},
    "ANTI-MAGE": {"NONE":"Duración de la animación posataque reducida de 0,6 s a 0,3 s", 
                  "VACÍO DE MANÁ": "Ahora aplica el miniaturdimiento a todas las unidades afectadas"},
    "ARC-WARDEN": {"ESPECTRO CENTELLEANTE": "Radio de búsqueda del Espectro Centelleante secundario con el Cetro de Aghanim reducido de 375 a 225"},
    "AXE": {"NONE":"Velocidad de movimiento base aumentada de 310 a 315", 
            "CONTRAATAQUE ESPIRAL": "Radio aumentado de 275 a 300"},
    "BANE": {"NONE":"Atributos base aumentados en 1", 
             "ABSORCIÓN CEREBRAL": "Curación obtenida de objetivos secundarios con el Cetro de Aghanim aumentada del 25 % al 30 %"},
    "BATRIDER": {"NAPALM PEGAJOSO": "Coste de maná aumentado de 20 a 25", 
                 "LAZO LLAMEANTE": "Alcance (objetivo secundario) con el Cetro Aghanim aumentado de 600 a 650"},
    "BEASTMASTER": {"TAMBORES DE SLOM": "Daño por golpe de tambor aumentado de 110 a 115", 
                    "TALENTOS": "Talento de nivel 15 de aura de velocidad de movimiento para Beastmaster y sus unidades reducido de +25 a +20"},
    "BOUNTY-HUNTER": {"MOVIMIENTO SOMBRÍO": "Ralentización de velocidad de movimiento/ataque modificada de 16/24/32/40 a 15/25/35/45"},
    "BREWMASTER": {"ESCISIÓN PRIMORDIAL": "Armadura de los Brewlecitos de Fuego aumentada de 0/4/8 a 0/8/16"},
    "BROODMOTHER": {"TEJER TELARAÑA": "Bonificación de velocidad de movimiento máxima reducida del 18/28/38/48 % al 10/22/34/46 %", "TRAMPA DE LA TEJEDORA": "Tiempo de regeneración de carga aumentado de 20 a 30 s", "ENGENDRAR CRÍAS": "Tiempo de vida de las crías de araña reducido de 40/45/50 a 40 s\nTiempo de vida de las arañitas reducido de 60 a 40 s"},
    "CENTAUR WARRUNNER": {"SUBIRSE AL CARRO": "Ahora otorga el efecto positivo de Estampida a Centaur (también aumenta la duración del efecto si se lanza durante Estampida en lugar de restablecer la duración del efecto positivo)\nTiempo de recarga reducido de 45 a 30 s"},
    "CHAOS KNIGHT": {"RAYO DEL CAOS": "Coste de maná reducido de 110/120/130/140 a 110"},
    "CLINKZ": {"MOVIMIENTO ESQUELÉTICO": "Después de salir de la invisibilidad, ahora siempre crea 1 esqueleto con la habilidad Ejército Ardiente\nEsqueletos adicionales con el Fragmento de Aghanim reducidos de 2 a 1 (el número total con Fragmento sigue siendo el mismo)"},
    "DARK-SEER": {"PUÑETAZO NORMAL": "Duración máxima del aturdimiento reducida de 2,25 a 2 s"},
    "DAZZLE": {"TALENTOS": "Talento de nivel 10 aumentado de +50 a +60 de daño"},
    "DEATH-PROPHET": {"Ganancia de inteligencia": "reducida de 3,3 to 3,0\nGanancia de fuerza reducida de 3,1 a 2,9\nTALENTOS\nTalento de nivel 10 reducido del +14 % al +12 % de resistencia mágica\nTalento de nivel 15 modificado de +30 de daño/curación para Extracción Espiritual a +300 de vida\nTalento de nivel 20 modificado de +400 de vida a +30 de daño/curación para Extracción Espiritual"},
    "DRAGON-KNIGHT": {"FORMA DE DRAGÓN ANCESTRAL": "Tiempo de recarga reducido de 105 a 100 s", "El Cetro de Aghanim": "ya no reduce 5 s el tiempo de recarga"},
    "DROW-RANGER": {"FLECHAS GÉLIDAS": "Reducción de regeneración por acumulación con Fragmento de Aghanim reducida del 10 % al 8 %", "PUNTERÍA": "Ahora solo otorga la mitad de la agilidad adicional a los héroes a distancia aliados"},
    "ELDER-TITAN": {"PISOTÓN RESONANTE": "Umbral del daño para despertar aumentado de 50/100/150/200 a 55/120/185/250", "ESPÍRITU ASTRAL": "Daño por héroe aumentado de 14/36/58/80 a 17/38/59/80"},
    "EMBER-SPIRIT": {"TALENTOS": "Talento de nivel 10 reducido de +15 a +12 de daño, Talento de nivel 20 reducido de +65 a +55 de daño a héroes para Destreza de Puño"},
    "ENCHANTRESS": {"ENCANTAR": "Tiempo de recarga modificado de 28/24/20/16 a 30/24/18/12 s, Ralentización de movimiento en héroes modificada del 55 % al 30/40/50/60 %, Duración modificada de 3,75/4,5/5,25/6 a 5 s", "PEQUEÑOS AMIGOS": "Alcance de lanzamiento aumentado de 600 a 750"},
    "GRIMSTROKE": {"OLA DE TINTA": "Daño por segundo aumentado de 25/35/45/55 a 25/40/55/70 (daño total de 75/120/165/210)", "VÍNCULO DE ALMAS": "Tiempo de recarga reducido de 90/70/50 a 70/60/50 s"},
    "HOODWINK": {"BELLOTAZO": "Daño adicional aumentado de 50/75/100/125 a 50/80/110/140"},
    "HUSKAR": {"FUEGO INTERIOR": "Duración de Desarmar aumentada de 1,75/2,5/3,25/4,0 a 1,90/2,6/3,3/4,0 s", "TALENTOS": "Talento de nivel 20 aumentado de 4 a 5 s de reducción del tiempo de recarga para Quebrantavidas"},
    "JAKIRO": {"SENDA HELADA": "Duración de la senda aumentada de 2,6/2,9/3,2/3,5 a 3/3,5/4/4,5 s (la duración máxima del aturdimiento no se ha modificado)"},
    "MACROPIRA": {"NONE": "Ahora aplica su daño inmediatamente después del lanzamiento en lugar de 0,5 s después"},
    "JUGGERNAUT": {"NONE": "Daño base aumentado de 50-54 a 53-55", "FURIA DE LA HOJA": "Frecuencia de ataque con Fragmento de Aghanim aumentada de 1,2 a 1,4 s", "DANZA DE LA HOJA": "Daño crítico aumentado del 180 % al 190 %", "TALENTOS": "Talento de nivel 10 aumentado de +75 a +100 de radio para Furia de Hoja"},
    "KEEPER-OF-THE-LIGHT": {"FUEGO FATUO": "Ataques para destruir aumentados de 6 a 7"},
    "KUNKKA": {"BARCO FANTASMA": "Daño retardado aumentado del 40 % al 45 %"},
    "LESHRAC": {"RÁFAGA DE PULSACIONES": "Daño reducido de 90/140/190 a 80/135/180"},
    "LICH": {"NONE": "Ganancia de inteligencia aumentada de 3,6 a 3,8", "EXPLOSIÓN GÉLIDA": "Tiempo de lanzamiento mejorado de 0,4 a 0,3 s, Alcance de lanzamiento modificado de 600 a 575/600/625/650"},
    "LINA": {"ESCLAVO DRACÓNICO": "Tiempo de recarga aumentado de 9 a 12/11/10/9 s", "IMPACTO DE LUZ SOLAR": "Coste de maná aumentado de 100/105/110/115 a 115", "ALMA ÍGNEA": "Bonificación de velocidad de ataque por acumulación reducida de 10/20/30/40 a 8/16/24/32, Bonificación de velocidad de movimiento por acumulación reducida del 1,5/2/2,5/3 % al 1/1,5/2/2,5 %", "TALENTOS": "Talento de nivel 15 reducido de +350 a +250 de vida, Talento de nivel 20 reducido de +15/1 % a +10/1 % de velocidad por acumulación para Alma Ígnea"},
    "LION": {"Armadura base": "aumentada en 1", "Agilidad base": "reducida de 18 a 15", "DEDO DE LA MUERTE": "Tiempo de recarga reducido de 160/100/50 a 140/90/40 s"},
    "LUNA": {"HAZ LUMÍNICO": "Duración con Fragmento de Aghanim aumentada de 12 a 15 s, Daño con Fragmento de Aghanim aumentado de +15 a +17"},
    "MEDUSA": {"SERPIENTE MÍSTICA": "Daño base aumentado de 80/120/160/200 a 85/130/175/220", "TALENTOS": "Talento de nivel 15 aumentado de 2 a 3 s de reducción del tiempo de recarga para Serpiente Mística"},
    "MIRANA": {"BRINCO": "Daño con Fragmento de Aghanim aumentado de 150 a 170, Distancia del proyectil con Fragmento de Aghanim aumentada de 600 a 800"},
    "MONKEY-KING": {"Agilidad base": "aumentada en 1", "BRINCO PRIMORDIAL": "Tiempo de canalización máximo reducido de 1,6 a 1,5 s"},
    "NAGA-SIREN": {"ATRAPAR": "Alcance de lanzamiento reducido de 575/600/625/650 a 500/525/550/575, Alcance de lanzamiento con Cetro de Aghanim aumentado de 1,5 a 1,6 veces", "CANTO DE LA SIRENA": "Tiempo de recarga aumentado de 160/120/80 a 180/130/80 s", "ARRASTRAR": "Velocidad de atracción aumentada de 150 a 200"},
    "NATURES-PROPHET": {"IRA DE LA NATURALEZA": "Daño base reducido de 115/150/185 a 105/145/185", "TALENTOS": "El talento de nivel 20 Brotar Encadena ya no ignora la inmunidad a hechizos", "Agilidad": "reducida de 22+3,6 a 20+3,4", "Ganancia de inteligencia": "reducida de 3,7 a 3,5"},
    "NECROPHOS": {"PULSO MORTAL": "Coste de maná reducido de 100/130/160/190 a 100/120/140/160"},
    "OGRE MAGI": {"IGNICIÓN": "Ralentización aumentada del 20/22/24/26 % al 20/23/26/29 %", "ESCUDO DE FUEGO": "Daño de Bola de Fuego aumentado de 125 a 160"},
    "OMNIKNIGHT": {"AURA DE DEGENERACIÓN": "Radio aumentado de 400 a 450"},
    "ORACLE": {"FIN DE LA FORTUNA": "Velocidad del proyectil aumentada de 1000 a 1200", "Radio": "aumentado de 300 a 350"},
    "OUTWORLD-DESTROYER": {"ECLIPSE DE LA CORDURA": "Ahora inflige el doble de daño a ilusiones"},
    "PANGOLIER": {"SALTO ESTRUENDOSO": "Daño reducido de 90/160/230/300 a 75/150/225/300", "ENROLLAR": "Ya no aplica una disipación básica al lanzarse"},
    "PHANTOM-ASSASSIN": {"DAGA SOFOCANTE": "Daño base aumentado de 65 a 65/70/75/80", "DESVANECER": "Radio de disipación reducido de 600 a 400"},
    "PUCK": {"ESCISIÓN FLUCTUANTE": "Daño reducido de 70/130/190/250 a 60/120/180/240"},
    "PUDGE": {"PUDRIR": "Daño adicional por segundo con Cetro de Aghanim reducido de 100 a 95"},
    "PUGNA": {"SUCCIÓN VITAL": "Porcentaje de absorción de vida con el Fragmento de Aghanim aumentado del 70 % al 75 %"},
    "QUEEN-OF-PAIN": {"Daño de ataque base": "aumentado en 2"},
    "RAZOR": {"OLEADA TORMENTOSA": "Los rayos bifurcados con el Fragmento de Aghanim ahora tienen 1 s de tiempo de recarga interno"},
    "RIKI": {"DARDO ADORMECEDOR": "Alcance de lanzamiento reducido de 1000 a 600", "Tiempo de recarga": "aumentado de 12 a 15 s"},
    "RUBICK": {"TELEQUINESIS": "El Fragmento de Aghanim ya no proporciona tiempo de recarga reducido cuando se utiliza sobre uno mismo o sobre los aliados", "TALENTOS": "Talento de nivel 10 reducido de +175 a +150 de daño por impacto para Telequinesis"},
    "SAND-KING": {"EPICENTRO": "Ralentización de la velocidad de ataque aumentada de 30 al 30/45/60", "TALENTOS": "Talento de nivel 10 aumentado de +0,3 a +0,5 s de duración del aturdimiento para Asalto Subterráneo", "Talento de nivel 15": "aumentado de +100 a +120 de daño para Apoteosis Cáustica"},
    "SHADOW-SHAMAN": {"Recompensa de oro de los Guardianes Serpiente": "reducida de 28-36 a 22-30", "DESCARGA ETÉREA": "Distancia máxima aumentada de 500 a 600", "TALENTOS": "Talento de nivel 15 aumentado de +120 a +140 de alcance de ataque para Guardianes Serpiente"},
    "SILENCER": {"MALDICIÓN ARCANA": "Tiempo de recarga aumentado de 20/18/16/14 a 22/20/18/16 s", "TALENTOS": "Talento de nivel 10 reducido de +12 a +10 de daño para Maldición Arcana", "Talento de nivel 15": "reducido de 25 a 20 s de reducción del tiempo de recarga para Silencio Global"},
    "SLARDAR": {"NEBLINA CORROSIVA": "Alcance de lanzamiento aumentado de 700/800/900 a 900"},
    "SLARK": {"ASALTO": "Tiempo de recarga aumentado de 20/16/12/8 a 22/18/14/10 s", "Distancia con el Cetro de Aghanim": "reducida de 1200 a 1100"},
    "SNAPFIRE": {"GALLETA FOGOSA": "Daño por impacto de Besos de Mortimer con Fragmento de Aghanim reducido un 50 %"},
    "STORM-SPIRIT": {"Tiempo de ataque base": "mejorado de 1,7 a 1,6 s"},
    "TEMPLAR-ASSASSIN": {"Fuerza base": "aumentada en 2"},
    "TINY": {"ANDANADA DE ÁRBOLES": "Intervalo de lanzamiento aumentado de 0,4 a 0,5 s",
    "Tiempo de canalización máximo": "aumentado de 2,4 a 2,5 s"},
    "TREANT-PROTECTOR": {"ARMADURA VIVIENTE": "Armadura adicional reducida de 6/8/10/12 a 4/6/8/10",
    "APARIENCIA DE LA NATURALEZA": "Ya no proporciona amplificación de curación/regeneración"},
    "TUSK": {"FRAGMENTOS DE HIELO": "Alcance de lanzamiento reducido de 1800 a 1400",
    "¡PUÑETAZO DE MORSA!": "Daño crítico reducido del 300/350/400 % al 250/325/400 %"},
    "UNDYING": {"DESCOMPONER": "Duración del robo reducida de 45 a 40 s",
    "DESGARRE DE ALMA": "Coste de maná aumentado de 90/100/110/120 a 120"},
    "WARLOCK": {"OFRENDA DEL CAOS": "Daño del gólem aumentado de 100/150/200 a 110/170/230",
    "Daño del gólem con Cetro de Aghanim": "aumentado de 75/110/150 a 80/125/170",
    "Retraso del segundo gólem con Cetro de Aghanim": "aumentado de 0,2 a 0,5 s",
    "Talento de nivel 10": "aumentado del +3 % al +4 % de daño para Ataduras Funestas"},
    "WINDRANGER": {"DISPARO POTENCIADO": "Distancia de recorrido aumentada de 2600 a 3000", "FUEGO CONCENTRADO": "Reducción de daño reducida del 30 % al 25 %"},
    "WINTER-WYVERN": {"MALDICIÓN DEL INVIERNO": "Ahora aplica una disipación al objetivo"},
    "WITCH-DOCTOR": {"RESTAURACIÓN VUDÚ": "Curación/daño aumentados de 10/20/30/40 a 10/22/34/46","Talento de nivel 20": "aumentado del +20 % al +25 % de daño de ráfaga para Embrujo"}
}





@bot.command(name="Heroe")
async def hero(ctx, name: str):
    if ctx.channel.id  != CanalDotaUpdates :  
        return
    if name.upper() in Heroes:
        hero_data = Heroes[name.upper()]
        # Convertimos el diccionario de datos en un texto formateado para enviarlo en Discord
        await ctx.send("```diff\n+ ╔═════  ≪ °❈° ≫ ══════ ≪ °❈° ≫  ══════╗\n+ |          Parche 7.32e [DOTA 2]          |\n+ ╚═════  ≪ °❈° ≫ ══════ ≪ °❈° ≫  ══════╝\n```")
        hero_text = f"**{name}**:\n"
        for title, description in hero_data.items():
            hero_text += f"- {title}: {description}\n"
        await ctx.send(hero_text)
    else:
        await ctx.send(f"No se encontró información para el héroe '{name}'")




 
#ObtenerInfoPartidaDota
@bot.command(name="game_results")
async def game_results(ctx):
    radiant_scores = [100, 19, 69, 93, 95]
    dire_scores = [9, 31, 138, 98, 41]
    bans = [76, 60, 138, 59, 34]
    duration = "00:31:38"

    radiant_total = sum(radiant_scores)
    dire_total = sum(dire_scores)

    # determine the winner
    if radiant_total > dire_total:
        winner = "Radiant"
    else:
        winner = "Dire"

    # format the output message
    output = f"Radiant: {radiant_scores}\nDire: {dire_scores}\nBans: {bans}\nDuracion: {duration}\nRadiant Score: {radiant_total}\nDire Score: {dire_total}\nWinner: {winner}"

    await ctx.send(output)




@bot.command(name="Borrar")
@commands.has_any_role('[OWNER]', 'Ver')
async def reborar(ctx):
    if ctx.channel.id  != CanalDotaUpdates :  
        return
    await ctx.channel.purge()


@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")


def sumar(a,b):
    suma = a + b
    return suma
#TEMPORAL
def convertir_segundos(segundos):
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segundos = segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


def CrearImagen(Id_partida):
    #Obtener Info
    match_id = str(Id_partida)
    url = f"https://api.opendota.com/api/matches/{match_id}"
    response = requests.get(url)
    if response.status_code == 200:
        # El request fue exitoso
        match = response.json()
        #print(match_data) # Aquí puedes hacer lo que quieras con los datos del partido
    else:
        # El request no fue exitoso
        print(f"Error: {response.status_code}")
        return
    Radiant = []
    Dire = []
    Bans = []
    Duracion = 0
    # Obtener picks o bans
    for pick in match["picks_bans"]:
        hero_id = pick["hero_id"]
    
        if pick["team"] == 0 and pick["is_pick"] == True:
            Radiant.append(hero_id)
        elif pick["team"] == 1 and pick["is_pick"] == True:
            Dire.append(hero_id)
        else:
            Bans.append(hero_id)
    # Obtener Duracion
    Duracion = match["duration"]
    Duracion = convertir_segundos(Duracion)
    #Obtener Score
    Radiant_Score = match["radiant_score"]
    Dire_Score = match["dire_score"]
    #Obtener Ganador
    if match["radiant_win"] == True:
        Winner="Radiant"
    else:
        Winner="Dire"

    # Imprimimos las listas resultantes
    print("Radiant: ", Radiant)
    print("Dire: ", Dire)
    print("Bans: ", Bans)
    print("Duracion: ", Duracion)
    print("Radiant Score: ", Radiant_Score)
    print("Dire Score: ", Dire_Score)
    print("Winner: ", Winner)

    #Insertamos heroes
    imagen_principal = Image.open("Heros//NewFondo.png")
    #Cargamos Heroes
    # Cargar las imágenes a insertar
    imagenes_insertar = []
    #Radiant = [80, 83, 107, 55, 11]
    #Dire = [62, 90, 40, 17, 36]
    
    for i in Radiant:
        #imagenes_insertar.append(Image.open(f"Heros//{i}.png"))
        imagenes_insertar.append(Image.open(f"Heros//{i}.png"))
        
    
    for i in Dire:
        imagenes_insertar.append(Image.open(f"Heros//{i}.png"))
    
    # Obtener el tamaño de la imagen principal
    ancho, alto = imagen_principal.size

    # Calcular la posición de las imágenes a insertar
    #posiciones = [(100, 200), (265, 200), (430, 200), (595, 200), (760, 200), (100,480), (265, 480), (430, 480), (595, 480), (760, 480)]
    posiciones = []
    for i in range(2):
        for j in range(5):
            x = 100 + j * 165
            y = 200 + i * 280
            posiciones.append((x, y))

    # Pegar las imágenes en las posiciones calculadas
    for i, pos in enumerate(posiciones):
        imagen_principal.paste(imagenes_insertar[i], pos)

    # Dibujar los bordes de las imágenes
    dibujo = ImageDraw.Draw(imagen_principal)
    dark_mag = (139,0,139)
    for pos in posiciones:
        dibujo.rectangle((pos[0], pos[1], pos[0] + 165, pos[1] + 92), outline=dark_mag, width=5)

    # Guardar la imagen resultante
    imagen_principal.save("ImagenConHeroes.png")
    # Crear un objeto ImageDraw para dibujar sobre la imagen
    dibujar = ImageDraw.Draw(imagen_principal)


    texto = f"Winner:{Winner}"
    # Definir los textos y las fuentes a utilizar
    #texto = "Winner:Dire"
    #partida_id = 7075443082
    textoid = "ID PARTIDA: " + match_id
    #Tiempo = "00:30:51"
    Tiempo = str(Duracion)
    ScoreRadiant, ScoreDire = str(Radiant_Score), str(Dire_Score)
    fuentes = {
        "normal": ImageFont.truetype("Fuentes//cocobiker-heavy.ttf", 62),
        "id": ImageFont.truetype("Fuentes//Montserrat-Arabic Regular 400.otf", 30),
        "tiempo": ImageFont.truetype("Fuentes//Montserrat-Arabic Regular 400.otf", 40),
        "score": ImageFont.truetype("Fuentes//Montserrat-Arabic Regular 400.otf", 90)
    }

    # Insertar los textos en la imagen
    posicion_texto = ((imagen_principal.width - dibujar.textsize(texto, font=fuentes["normal"])[0]) // 2, 40)
    posicion_textoid = (60, 710)
    posicion_tiempo = ((imagen_principal.width - dibujar.textsize(Tiempo, font=fuentes["tiempo"])[0]) // 2, 384)
    posicion_ScoreRad = (((imagen_principal.width - dibujar.textsize(ScoreRadiant, font=fuentes["score"])[0]) // 2) - 200, 355)
    posicion_ScoreDir = (((imagen_principal.width - dibujar.textsize(ScoreDire, font=fuentes["score"])[0]) // 2) + 200, 355)

    dibujar.text(posicion_texto, texto, font=fuentes["normal"], fill=(225, 225, 225))
    dibujar.text(posicion_textoid, textoid, font=fuentes["id"], fill=(225, 225, 225))
    dibujar.text(posicion_tiempo, Tiempo, font=fuentes["tiempo"], fill=(225, 225, 225))
    dibujar.text(posicion_ScoreRad, ScoreRadiant, font=fuentes["score"], fill=(225, 225, 225))
    dibujar.text(posicion_ScoreDir, ScoreDire, font=fuentes["score"], fill=(225, 225, 225))

    # Guardar la imagen con el texto insertado
    imagen_principal.save("ImagenTotal.png")


# Cargamos la extensión
bot.add_cog(Principal(bot))

if __name__ == '__main__':
    bot.run(os.environ("DISCO_MARINELA"))

