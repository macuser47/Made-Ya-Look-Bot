import discord
from discord.ext import commands
import sched
import time
from datetime import timedelta 
import datetime
import random
from threading import Thread
from asyncsched import asyncscheduler

class MentionListener(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, message):
		if self.bot.user in message.mentions:
			await message.add_reaction(
				discord.utils.get(bot.emojis, name="ping")
			)

class MessageScheduler:
	def __init__(self, bot):
		self.bot = bot
		self.s = asyncscheduler(timefunc=time.time)

	async def start(self):
		await self.bot.wait_until_ready()
		self.schedule_next(
			min_time=timedelta(seconds=2),
			max_time=timedelta(seconds=2)
		)
		await self.s.run()

	async def wakeup(self):
		self.schedule_next()
		for guild in self.bot.guilds:
			#select first channel bot can send in
			channel = next((
				ch for ch in guild.channels
				if ch.permissions_for(guild.me).send_messages
					and type(ch) is discord.TextChannel
			), None)

			#select random online user and ping
			member_choices = [m for m in guild.members 
				if (m.status == discord.Status.online) and (not m.bot)]

			#ignore if no available channels or no members
			if (channel is None) or (not member_choices):
				continue	

			member = random.choice(member_choices)

			print("Chose member '{}' in channel '{}' for guild '{}'".format(
				member, channel, guild	
			))
			await self.send_msg(guild, channel, member)

		print(
			"Next ping round scheduled for {}".format(
				datetime.datetime.fromtimestamp(self.s.queue[0].time)
					.strftime('%Y-%m-%d %I:%M:%S %p')
			)
		)

	def schedule_next(
		self, 
		min_time=timedelta(minutes=20), 
		max_time=timedelta(days=5)
	):
		self.s.enter(
			random.randint(min_time.total_seconds(), max_time.total_seconds()),
			1,
			self.wakeup
		)

	async def send_msg(self, guild, channel, member):
		async with channel.typing():
			#find emoji
			emoji = discord.utils.get(guild.emojis, name="moon2DEV")
			await channel.send(
				"{} {} {}".format(
					member.mention,
					"made ya look",
					str(emoji)
				)
			)
		

if __name__ == "__main__":
	print("Starting bot...")
	with open("token.key") as f:
		key = f.read()

	intents = discord.Intents.default()
	intents.members = True
	intents.presences = True
	bot = commands.Bot(str(b'\x00'), intents=intents)
	bot.add_cog(MentionListener(bot)) 
	bot.loop.create_task(MessageScheduler(bot).start())

	bot.run(key)
