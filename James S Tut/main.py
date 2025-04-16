# import discord files
import discord
from discord.ext import commands
from discord import app_commands

#for safe token keys
import os
from typing import Final
from dotenv import load_dotenv

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

command_prefix = "!"


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
    

#------------------- Force syncing slash commands -------------------
        try:
            guild = discord.Object(id =  1357697762090549503)
            synced = await self.tree.sync(guild = guild)
            print(f"Synced {len(synced)} commands to guild {guild.id}")

        except Exception as e:
            print(f"Error syncing commands: {e}")
        

#-------------------response to users -------------------
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.lower().startswith(f"{command_prefix}who"):
            await message.channel.send(f"Hi there {message.author.display_name}")
            await message.channel.send(
                f"Server Exclusive nickname: {message.author.nick} \n"
                f"Your name on discord: {message.author.display_name}\n"
                f"Username: {message.author.name}\n"
                f"<@{message.author.id}>"
)
#------------------------ Emoji reaction -----------------------
    async def on_reaction_add(self, reaction, user):
        await reaction.message.channel.send(f"You reacted with: {reaction.emoji} bruh")

#------------------- intents -------------------
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
client = Client(command_prefix="!", intents=intents) # can change the command prefix, may not work.


GUILD_ID = discord.Object(id = 1357697762090549503) # server id

#------------------- Slash Commands -------------------
@client.tree.command(name="hello", description = "Say Hello!", guild = GUILD_ID) # def command infos
async def sayHello(interaction: discord.Interaction):
    #await asyncio.sleep(0.05)
    await interaction.response.send_message("Hi there!")

@client.tree.command(name="printer", description = "I will print whatever you give me!", guild = GUILD_ID) # def command infos
async def sayHello(interaction: discord.Interaction, printer: str):
    #await asyncio.sleep(0.05)
    await interaction.response.send_message(printer)

#-------------------Embed --------------------
@client.tree.command(name="embed", description = "embed demo", guild = GUILD_ID)
async def sayHello(interaction: discord.Interaction):
    #await asyncio.sleep(0.05)

    embed = discord.Embed(title="I am a Title", url="https://www.youtube.com/@Thatrandomblenderguy?sub_confirmation=1", description="I am a description", color=discord.Color.red())
    embed.set_thumbnail(url="https://ih1.redbubble.net/image.313374668.7868/raf,750x1000,075,t,heather_mid_grey.u2.jpg")
    embed.add_field(name = "Field 1", value = "Field 1 Information", inline=False)
    embed.add_field(name = "Field 2", value = "Field 2", inline=False)
    embed.add_field(name = "Field 3", value = "Field 3", inline=True)
    embed.add_field(name = "Field 4", value = "Field 4", inline=True)

    embed.set_footer(text = "This is the footer!")
    embed.set_author(name = interaction.user.name, url = "https://www.youtube.com/@Thatrandomblenderguy?sub_confirmation=1",icon_url = "https://ih1.redbubble.net/image.313374668.7868/raf,750x1000,075,t,heather_mid_grey.u2.jpg")
    await interaction.response.send_message(embed = embed)

####################### Buttons ########################
class View(discord.ui.View):

#---------------------- Button 1 -----------------
    @discord.ui.button(label = "Click Me!", style = discord.ButtonStyle.red, emoji = "🔥")
    async def button_callback1(self, button, interaction):
        await button.response.send_message("You have clicked the button!")
#---------------------- Button 2 -----------------
    @discord.ui.button(label = "No, Click Me!", style = discord.ButtonStyle.blurple, emoji = "👀")
    async def button_callback2(self, button, interaction):
        await button.response.send_message("You have clicked the second button!")
#---------------------- Button 3 -----------------
    @discord.ui.button(label = "HEY, Click Me!", style = discord.ButtonStyle.green, emoji = "😎")
    async def button_callback3(self, button, interaction):
        await button.response.send_message("You have clicked the third button!")

#------------------ Button functions --------------
@client.tree.command(name="button", description = "Displaying a button", guild = GUILD_ID)
async def sayHello(interaction: discord.Interaction):
    #await asyncio.sleep(0.05)
    await interaction.response.send_message(view = View())



################ TOKEN (remove when sharing code) #################
client.run(TOKEN)
