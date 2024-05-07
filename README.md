# NFL-Concussions-Project
This was a project made in my intermediate, masters-level programming course. 
This is a program that uses a network to allow users to learn more about concussions and team performance in the NFL. 
The way the network is organized is that data was read in from two different datasets on concussions in the NFL and NFL team performance. 
The nodes in the network are every player who has received a concussion in the NFL. The edges are teams in the NFL, and they connect players
who played on the same team. 

In order to run this program, you will need to first run the app.py file in your terminal, and navigate to http://localhost:{port number specified in app.py}/ in order to use the interactive flask app. The files have to be structured as follows:
folder named flask_app
	folder named __pycache__
		concussions.cpython-39.pyc
		DataStructure.cpython-39.pyc
	folder named static
		styles.css
	folder named templates
		index.html
		team.html
	app.py
	DataStructure.py
	ConcussionInjuries2012-2014.csv
	team_stats_2003_2023.csv
Python packages that are required are pandas, networkx, matplotlib.pyplot, itertools, flask, and os

The interactions that will be available to the user are searching for an NFL team, searching for information on team statistics every year the team had a concussion, searching for information on every player on the team who had a concussion, and searching for information on every other team that had the same amount of concussions in total. 
The potential answers to these prompts are any one of the NFL teams (when searching for a team), each year that the team had a concussion, or each player that had a concussion. The program will then get the relevant information from the databases and display them as a table on the webpage. 
