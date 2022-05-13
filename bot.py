import discord
from discord.ext import commands
import random
import pandas as pd
import numpy as np
import time

class Prediction:
	def __init__(self,discription,outcomes):
		self.discription = discription
		self.outcomes = outcomes
		self.betters = []
		self.betterNames = []
		
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Bet:
	def __init__(self,id,amount,outcome):
		self.id = id
		self.amount = amount
		self.outcome = outcome
	
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

def gibPoints(user,amount):
	usersDf = pd.read_csv("bet.csv",index_col="Name")
	#print(usersDf)
	usersDf.loc[user] = int(usersDf.at[user,"Points"]) + int(amount)
	usersDf.to_csv('bet.csv')
	return

def removePoints(user,amount):
	usersDf = pd.read_csv("bet.csv",index_col="Name")
	#print(usersDf)
	usersDf.loc[user] = int(usersDf.at[user,"Points"]) - int(amount)
	usersDf.to_csv('bet.csv')
	return

def displayPoints():
	usersDf = pd.read_csv("bet.csv")
	usersDf.set_index("Name", inplace = True)
	sortedDF = usersDf.sort_values("Points",ascending=False)
	#print(sortedDF)
	return(str(sortedDF))



intents = discord.Intents.default()
intents.members = True
description =  "Very badly coded bot just for fun and practice to test out the pycord lib"
bot = commands.Bot(command_prefix="?", description=description, intents=intents)

@bot.event
async def on_ready():
	global predict
	predict = None
	global gibTime
	gibTime =  int(time.time())
	#print(gibTime)
	print(f"Logged in as {bot.user} (ID: {bot.user.id})")
	print("------")



@bot.event
async def on_message(message):
	

	if message.author.bot:
		return
	print("message recieved")
	msg = message.content.lower()

	if "sus" in msg:
		await message.channel.send("ඞ")
	
	if msg[0] == '!':
		#print("responding...")
		msg = msg.replace("!","")
		arrMsg = msg.split(",")
		print(arrMsg)
		#print(message.author.name)

		if arrMsg[0] == "add":
			#gibPoints(message.author.name,arrMsg[1])
			#await message.channel.send("Added Points")
			await message.channel.send("Disabled")
		elif arrMsg[0] == "gib pls":
			global gibTime
			print(gibTime)
			if int(time.time()) > gibTime:
				gibTime = gibTime + 86400
				usersDf = pd.read_csv("bet.csv")
				usersDf.set_index("Name", inplace = True)
				usersDf["Points"] = usersDf["Points"].apply(lambda x: x + 100)
				usersDf.to_csv('bet.csv')
				await message.channel.send("100 Points for everyone!!!! ")
			else:
				await message.channel.send("Try again later, ill need more time before i can produce more Points for you.")
		elif arrMsg[0] == "help":
			await message.channel.send("Commands are delimited by commas. Avaliable Commands include: help, register, prediction,bet,current,gib")
			# ---------------------------------------- !register ------------------------------------------------
		elif arrMsg[0] == "register":
			usersDf = pd.read_csv("bet.csv",index_col="Name")
			#print(usersDf)
			if message.author.name in usersDf.index:
				await message.channel.send("Account already exists")
			else:
				usersDf.loc[message.author.name] = [500]
				usersDf.to_csv('bet.csv')
				await message.channel.send("Created associated account")
		# ---------------------------------------- !prediction,(discription),[outcomes] ------------------------------------------------		
		elif arrMsg[0] == "prediction":
			try:
				global predict
				if predict == None:
					predict = Prediction(arrMsg[1],arrMsg[2:])
					await message.channel.send(f"Prediction : {arrMsg[1]} Started. Bet on " + str(predict.outcomes))
				else:
					await message.channel.send("Please reslove the active prediction before you create a new one")
			except:
				await message.channel.send("The format is !prediction,(discription),[outcomes]")
		# ---------------------------------------- !bet,(amount 500),(outcome A) ------------------------------------------------
		elif arrMsg[0] == "bet":
			try:
				if predict != None:
					usersDf = pd.read_csv("bet.csv")
					usersDf.set_index("Name", inplace = True)
					#print("reading csv")
					if message.author.name not in predict.betterNames:
						userTotal = usersDf.loc[message.author.name,"Points"]
						if int(userTotal) >= int(arrMsg[1]):
							#print("placing bet")
							newBet = Bet(message.author.name,arrMsg[1],arrMsg[2])
							removePoints(message.author.name,int(arrMsg[1]))
							predict.betters.append(newBet)
							predict.betterNames.append(message.author.name)
							await message.channel.send(f"{message.author.name} Place a bet of {arrMsg[1]} on outcome {arrMsg[2]}")
						else:
							await message.channel.send("Not enough Points")
					else:
						await message.channel.send("Already placed a bet")
				else:
					await message.channel.send("No prediction currently active")
			except:
				await message.channel.send("The format is !prediction,amount(500),outcome(Yes)")

		# ---------------------------------------- !current------------------------------------------------
		elif arrMsg[0] == "current":
			if predict != None:
				betsTotal = {}
				for ibet in predict.betters:
					if ibet.outcome in betsTotal.keys():
						betsTotal[ibet.outcome] =  int(betsTotal[ibet.outcome]) + int(ibet.amount)
					else:
						betsTotal[ibet.outcome] = int(ibet.amount)
				await message.channel.send("Current total bets per outcome" + str(betsTotal))

				outcomeRatios = {}
				for key1 in betsTotal:
					betAgainst = 0
					for key2 in betsTotal:
						if key1 != key2:
							betAgainst += float(betsTotal[key2])
					outcomeRatios[key1] = betAgainst/float(betsTotal[key1]) + 1

				await message.channel.send("Reward Rations per Outcome are 1 to : " +str(outcomeRatios))
			else:
				await message.channel.send("No prediction currently active")
		# ---------------------------------------- !Points------------------------------------------------
		elif arrMsg[0] == "Points":
			await message.channel.send(displayPoints())
		# ---------------------------------------- !result------------------------------------------------
		elif arrMsg[0] == "resolve":
			if predict != None:
				betsTotal = {}
				outcomeRatios = {}
				for ibet in predict.betters:
					if ibet.outcome in betsTotal.keys():
						betsTotal[ibet.outcome] =  int(betsTotal[ibet.outcome]) + int(ibet.amount)
					else:
						betsTotal[ibet.outcome] = int(ibet.amount)
				
				outcomeRatios = {}
				for key1 in betsTotal:
					betAgainst = 0
					for key2 in betsTotal:
						if key1 != key2:
							betAgainst += float(betsTotal[key2])
					outcomeRatios[key1] = betAgainst/float(betsTotal[key1]) + 1

				for bets in predict.betters:
					if bets.outcome == arrMsg[1]:
						winAmount = float(bets.amount)*float(outcomeRatios[bets.outcome])
						gibPoints(bets.id,int(winAmount))
						await message.channel.send("ඞ " +str(bets.id) + " WINS " + str(winAmount) + " ඞ")
						await message.channel.send(displayPoints())
				predict = None
			else:
				await message.channel.send("No prediction currently active")
		else:
				await message.channel.send("Invalid Command use !help")
 

bot.run("OTA5ODk4NjMxODY2MzUxNjg4.YZK_Ig.hH30IA_TCBkzqGuimqIaddPDkGM")