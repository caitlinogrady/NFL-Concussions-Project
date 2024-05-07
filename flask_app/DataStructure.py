import pandas as pd
#Documentation: https://networkx.org/, suggested by chatgpt and read up on it here
import networkx as nx
import matplotlib.pyplot as plt
import itertools
from flask import Flask, render_template, request, jsonify
from itertools import chain
import os

#importing dataframes, got from kaggle
concussions = pd.read_csv('ConcussionInjuries2012-2014.csv')
stats = pd.read_csv('team_stats_2003_2023.csv')


class Concussions:
	'''
	This class handles all of the network building capabilities for NFL concussions by team 

	Attributes
	---------
	concussions_df: pd.Dataframe 
		the data on concussions in the NFL
	stats_df: pd.Dataframe
		the data on team statistics in the NFL
	G: networkx.classes.graph.Graph
		the graph of Nodes and Edges

	Methods
	-------
	preprocess: processes the data and creates dataframes with the necessary information
	network: creates a network of nodes (players) connected by the teams they played for (edges)
	visualize: creates a graphical representation of the network
	'''
	def __init__(self, concussions_df, stats_df):
		'''
		initializes the attributes of the class, concussions_df, stats_df, G
		'''
		self.concussions = concussions_df
		self.stats = stats_df
		self.G = nx.Graph()

	def preprocess(self):
		'''
		Process the dataframes to clean up the data and convert it into a useable form for this project

		Parameters
		----------
		None

		Returns
		-------
		None
		'''
		#extract columns i want from concussions dataframe
		self.player_info = self.concussions[['Player', 'Team','Date', 'Position','Weeks Injured', 'Games Missed', 'Play Time After Injury', 'Average Playtime Before Injury']].copy()
		#extract numerical values from strings and turn them to floats, used chatgpt to figure out the correct regex string to use
		self.player_info['Play Time After Injury'] = self.player_info['Play Time After Injury'].str.extract(r'(\d+)').astype(float)
		self.player_info['Average Playtime Before Injury'] = self.player_info['Average Playtime Before Injury'].str.extract(r'(\d+)').astype(float)
		#calc number of concussions for each player, as number of times they appear in concussions dataframe (each row represents one concussion instance)
		self.player_info['Concussions'] = 1
		self.player_info['Concussions'] = self.player_info.groupby('Player')['Concussions'].transform('count')
		#add all concussion dates as a list of each occurence for each player
		#convert to datetime object and extract year
		self.player_info['Year'] = pd.to_datetime(self.player_info['Date'], format='%d/%m/%Y').dt.year
		#used chatgpt to figure out how to transform to list using lambda function
		self.player_info['Concussion Years'] = self.player_info.groupby('Player')['Year'].transform(lambda x: list(x))
		#group by player and position and use .agg to correctly combine each data field 
		#used https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html
		self.player_info = self.player_info.groupby(['Player','Position']).agg({
			'Concussions': 'first',
			'Team': lambda x: list(set(x)),
			'Date': 'first',
			'Weeks Injured': 'sum',
			'Games Missed': 'sum',
			'Play Time After Injury': 'mean',
			'Average Playtime Before Injury': 'mean',
			'Concussion Years': 'first'
		})
		#reset index to make the players name a data field and not the index
		self.player_info.reset_index(inplace=True)
		#copy relevant fields of team stats dataframe
		self.stats = self.stats[['year', 'team', 'wins', 'losses', 'win_loss_perc']].copy()


	#chatgpt helped, asked how to build network with nodes and edges, based on player positions and number of concussions
	def network(self):
		'''
		Create a network of nodes and edges based on this data
		the nodes represent each player who has gotten a concussion 
		the edges connect concussed players who have played on the same team as another concussed player
		'''
		#https://stackoverflow.com/questions/13698352/storing-and-accessing-node-attributes-python-networkx
		for idx, data in self.player_info.iterrows():
			#extract player name and teams they played for 
			player = data['Player']
			teams = data['Team']
			#add node for each player, with attributes of team, position, concussions, years, weeks_injured, games_missed, play_after, and play_before
			self.G.add_node(player, team=data['Team'], position=data['Position'], concussions=data['Concussions'], years=data['Concussion Years'], weeks_injured=data['Weeks Injured'], games_missed=data['Games Missed'], play_after=data['Play Time After Injury'], play_before=data['Average Playtime Before Injury'])
			#iterate through all of the teams the player played for 
			for team in teams:
				#get the names of every other player  in the dataframe that played for that team
				players = self.player_info[self.player_info['Team'].apply(lambda x: team in x)]['Player'].tolist()
				#iterate through other players that played for the same team
				for other in players:
					if other != player:
						#add edges between the nodes of each player that has played on the same team as another player 
						self.G.add_edge(player, other)
		return self.G

	
	def visualize(self):
		'''
		Creates a graph visualization of the network
		'''
		pos = nx.spring_layout(self.G)
		nx.draw(self.G, pos, with_labels= True)
		plt.show()



def main():
	#calling each function, ensuring it all works before building the flask app
	concussion_analyzer = Concussions(concussions, stats)
	concussion_analyzer.preprocess()
	network = concussion_analyzer.network()
	concussion_analyzer.visualize()

if __name__ == "__main__":
    main()


	