# DänAPP - A Web-app for our yearly vacation in Denmark
#### Video Demo:  <https://youtu.be/7qi74Xz_X1A>
#### Description:
A small web-app that generates random teams from its list of users or manually entered names and provides a system for proposing ideas and voting on them.
## Where the project idea came from
For more than 8 years now, every year at the same time I am on vacation in Denmark with a group of 10-12 friends. This year, at the time I was working on the CS50x course and we brainstormed ideas for my final project. Soon we noticed that we could actually use a small app for our vacation itself. We established that it should be able to solve two problems: Firstly, because we are often playing games together, are cooking in groups or doing some form of competition we could use a function that generates random teams from a list of participants. Secondly because we have a lot of free time we wanted to have a tool that collects ideas on what we could do from everyone and lets us vote on them.
## How to use the app
The app only works when you are logged in. So to use it you need to create a new account with a name and a password. After logging in you can see the two main functions in the navbar on top. By default "Team-Generator" is selected. The main view is a list of all users that are currently registered in the app's database. It's possible to manually remove or add participants and they are saved until teams are generated. You must then fill the input field for the number of teams to tell the app how many different groups there should be. Upon clicking on "Generate Teams" the participants are distributed randomly on the given number of teams.

The app's second function "Idea-Finder" shows an empty table by default. From there you can add new ideas to the database or delete all ideas with a click on "Reset". A "Show"-button toggles the visibility of all ideas in the database. When the ideas are shown you can remove them one by one with a click on "Remove". Alternatively all ideas can be removed with a click on "Reset". "Vote on ideas" lets you vote "yes" or "no" on all ideas that you did not vote on with your user id yet. At any time you can click on "Show Results" to show how many votes each idea currently has.
## How it works
The app's main framework is based in CS50's finance problem set. It reuses its login functionality while adding "flash"-messages instead of finance's meme for feedback. Its also built on  "templates/layout.html" which gets expanded by the other html files to display each webpage. The main backend funcionality can be found in "app.py" as a python/flask programm.

The app's two main functions are based on two different systems. It utilises an individual list for each user stored in their session for the "Team-Generator"-function and a shared database called "database.db" for saving ideas and votes as part of the "Idea-Finder".

Upon logging in, a temporary list of participants for the "Team-Generator" is generated by opening the database and getting a list of all users in it. This list is then stored inside a session key called "participants". If at any time the list is empty and the teams overview is called via get, this process is repeated. Removing a participant works by first removing it from the html-table from "templates/teams.html" and then sending a list of all remaining entries to the server where they are written to the variable inside the session. Similarly, adding a new participant generates a list of all participants in the html table again and then just adds the new entry to it before sending it to the server. Lastly, the reset-button just sends an empty list of participants to the server which then automatically generates a new one from the database of users as described above. To generate teams a function inside "helpers.py" is called. It takes a list of names and a number of teams as input and distributes all names randomly while ensuring that the teams are evenly sized. It outputs a dictionary with the team numbers as keys and lists for each team as values. This dictionary of lists is then converted to a list of lists. Afterwards it is send to the user's browser via "templates/teams_output.html" and each team/list is displayed as a bootstrap card.

The second function uses two tables in the app's database. In "ideas" all ideas are saved with an idea_id, a referenced user_id and the idea itself. "votes" saves all votes as a "0" or "1" referencing a user_id and a idea_id.
When adding an idea in "templates/ideas.html", it is sent together with an "add"-keyword from the user's browser to the server via post as json data. Removing an idea just sends the idea_id and a "delete"-keyword via json. Clicking the "Reset"-button sends a "reset"-keyword via json. The keywords are used in the "/ideas"-route to execute the corresponding sql-commands. Voting on ideas pulls all ideas for which no vote with the current user_id exists in the database and uses "templates/vote.html" to show one idea randomly to the user to vote on. If at any time the results are requested by clicking on the "Results"-button, an sql-command counts all votes for each idea and orders them in descending order. The ideas and the count are then displayed via "templates/results.html" as a simple table to the user.