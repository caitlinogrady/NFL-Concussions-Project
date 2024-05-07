from flask import Flask, render_template, request
import networkx as nx
import pandas as pd
from DataStructure import Concussions
from itertools import chain
from flask import send_file

#asked chat gpt for help in how to structure the flask app and how to correctly structure the entire file so that it would work properly 
#also used  https://flask.palletsprojects.com/en/3.0.x/ to understand what chatgpt was telling me better/ understanding how to work the file structure so that the app could find the correct stuff in the correct place 

# Initialize Flask app
app = Flask(__name__)
app.static_url_path = '/static'

#setting up data
conc = pd.read_csv('ConcussionInjuries2012-2014.csv')
st = pd.read_csv('team_stats_2003_2023.csv')

#creating instance of Concussions class
concussions = Concussions(conc, st)
#process data
concussions.preprocess()
#create network
G = concussions.network()

#get processed data from class
player_info = concussions.player_info
stats_data = concussions.stats

#all NFL teams
teams = ['New England Patriots' 'Miami Dolphins' 'Buffalo Bills' 'New York Jets'
 'Baltimore Ravens' 'Cincinnati Bengals' 'Pittsburgh Steelers'
 'Cleveland Browns' 'Indianapolis Colts' 'Tennessee Titans'
 'Jacksonville Jaguars' 'Houston Texans' 'Kansas City Chiefs'
 'Denver Broncos' 'Oakland Raiders' 'San Diego Chargers'
 'Philadelphia Eagles' 'Dallas Cowboys' 'Washington Redskins'
 'New York Giants' 'Green Bay Packers' 'Minnesota Vikings' 'Chicago Bears'
 'Detroit Lions' 'Carolina Panthers' 'New Orleans Saints'
 'Tampa Bay Buccaneers' 'Atlanta Falcons' 'St. Louis Rams'
 'Seattle Seahawks' 'San Francisco 49ers' 'Arizona Cardinals'
 'Los Angeles Rams' 'Los Angeles Chargers' 'Las Vegas Raiders'
 'Washington Football Team' 'Washington Commanders']

#index page, has the search bar for each team
@app.route('/')
def index():
    '''
    returns the data required for the index page
    '''
    return render_template('index.html', teams=teams)

#teams page, handles the results after a team is picked from the index page 
@app.route('/team', methods=['POST'])
def get_team_info():
    '''
    returns the information necessary to display search results on the team.html page 
    '''
    #team that the user selected
    selected = request.form.get('team')
    #get players who have received a concussion and played for the selected team
    #handles duplicates so that 
    already_seen = []
    stats = concussions.stats
    #iterates through the nodes (players) in the network
    for node in G.nodes:
        #gets the team that player played for 
        team = G.nodes[node]['team'][0]
        if team not in already_seen:
            #based on the edges in the network originating from that player, get all other players who have played on the same team and gotten a concussion
            players = list(set(chain(*G.edges(node))))
            #handles duplicates, so not going through the teams multiple times 
            already_seen.append(team)
        #if the team was the one the user wants to get information on
        if team == selected:
            #empty variable initializers
            player_data = {}
            years_for_stats = []
            total = 0

            #iterates through each player that has gotten a concussion playing for that team
            for player in players:
                #gets data on each player based on the nodes
                data ={
                    'Position': G.nodes[player]['position'],
                    'Concussions': G.nodes[player]['concussions'],
                    'Year': G.nodes[player]['years'],
                    'Weeks_Injured': G.nodes[player]['weeks_injured'],
                    'Games_Missed': G.nodes[player]['games_missed'],
                    'Play_Time_Before_Injury': G.nodes[player]['play_before'],
                    'Play_Time_After_Injury': G.nodes[player]['play_after']
                }
                #will be used for between-team comparison later
                total += G.nodes[player]['concussions']
                #add player data to larger data dictionary
                player_data[player] = data
                #will be used to get the team's statistics from each relevant year 
                years_for_stats.append(G.nodes[player]['years'])
            #sort the years list and make sure there are no duplicates
            years_for_stats = sorted(years_for_stats, reverse=True)
            years_for_stats = set(years_for_stats)
            #empty accumulator
            stats_data = {}
            #iterate through each year someone on the team got a concussion
            for year in years_for_stats:
                #get the statistic information for the correct year and team
                row = stats[(stats['year'] == year) & (stats['team'] == team)]
                #add data to dictionary
                data = row[['wins','losses','win_loss_perc']].to_dict(orient='records')[0]
                stats_data[year] = data
            #finding teams with the same amount of concussions
            #variables going to be used for comparison between each team
            closestDif = 100
            closestTeam = []
            #iterate through all players, in same format as before, to total how many concussions players on each team received in total
            for node in G.nodes:
                team = G.nodes[node]['team'][0]
                comp_players = list(set(chain(*G.edges(node))))
                comp = 0
                if team != selected:
                    for player in comp_players:
                        #get the total amount of concussions all players on the team received
                        comp += G.nodes[player]['concussions']
                    #how many more/less concussions did this team get than the selected team
                    dif = abs(total - comp)
                    #if the team is closer to the selected team, becomes the only team in the list
                    if dif  < closestDif:
                        closestDif = dif
                        closestTeam = [team]
                    #if the team is equally close to the selected team, gets added to the list 
                    if dif == closestDif:
                        closestTeam.append(team)
            #ensures there are no duplicates 
            closestTeam = set(closestTeam)
            #return the relevant dictionaries of data so that they can be displayed on the page 
            try:
                return render_template('team.html', team=selected, players=player_data, team_stats=stats_data, closest = closestTeam)
            except:
                return None
            


if __name__ == '__main__':
    app.run(debug=True, port='5033')