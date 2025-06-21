import os
from html.parser import HTMLParser
import csv


class MyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data_list = []

    def handle_data(self, data):
        stripped = data.strip()
        if stripped: 
            self.data_list.append(stripped)


class Player():
    def __init__(self, name):
        self.name = name
        self.goals = 0
        self.assists = 0
        self.points = 0
        self.penalties = 0
        self.pim = 0

    def __str__(self):
        return f"{self.name}: {self.goals} {self.assists} {self.points} {self.penalties} {self.pim}"

    def add_goal(self):
        self.goals += 1
        self.points += 1

    def add_assist(self):
        self.assists += 1
        self.points += 1

    def add_penalties(self, length):
        self.penalties += 1
        self.pim += length

    def __repr__(self):
        return f"{self.name},{self.goals}, {self.assists}, {self.points}, {self.penalties}, {self.pim}"


def get_player_data(data, players, player_names, my_team):
    home_team = home_or_away(data[12], my_team)
    home_score, away_score = 0, 0

    new_data = data.copy()
    while new_data[0] != "Scoring":
        new_data.pop(0)

    while new_data[0] != "Penalties" and len(new_data) > 1:
        if "(" in new_data[0]:
            if "/" in new_data[1]:
                score_index = 2
            else:
                score_index = 3

            current_score = new_data[score_index].split(" - ")
            proceed = False

            if home_team and int(current_score[1]) == home_score + 1:
                proceed = True
                home_score += 1
            elif not home_team and int(current_score[0]) == away_score + 1:
                proceed = True
                away_score += 1
            elif not home_team:
                home_score += 1
                new_data.pop(0)
            else:
                away_score += 1
                new_data.pop(0)

            if proceed:
                name = get_player_name(new_data.pop(0))
                if name not in player_names:
                    new_player = Player(name)
                    new_player.add_goal()
                    players.append(new_player)
                    player_names.append(name)
                else:
                    players[player_names.index(name)].add_goal()

                if score_index == 3:
                    assists = new_data.pop(0).split(',')

                    for assist in assists:
                        name = get_player_name(assist)
                        if name not in player_names:
                            new_player = Player(name)
                            new_player.add_assist()
                            players.append(new_player)
                            player_names.append(name)
                        else:
                            players[player_names.index(name)].add_assist()

        else:
            new_data.pop(0)

    while len(new_data) > 0:
        if "(" in new_data[0]:
            name = get_player_name(new_data.pop(0))
            team = new_data.pop(0)
            new_data.pop(0)
            penalty = new_data.pop(0)

            if penalty == "Minor":
                length = 2
            elif penalty == "Major (5 min)":
                length = 5
            elif penalty == "Game Misconduct":
                length = 10
            elif penalty == "Misconduct (10 min)":
                length = 10
            else:
                length = 5

            if home_or_away(team, my_team):

                if name not in player_names:
                    new_player = Player(name)
                    new_player.add_penalties(length)
                    players.append(new_player)
                    player_names.append(name)
                else:
                    players[player_names.index(name)].add_penalties(length)



        else:
            new_data.pop(0)


def get_player_name(raw):
    parts = raw.replace("-"," ").split()
    name = " ".join(parts[:-1])

    return name


def home_or_away(line, team) -> bool:
    for word in team.split(" "):
        if word not in line:
            return False
    return True


def run(team):
    path = "data/" + str(team)
    my_team = team
    files = os.listdir(path)

    players = []
    player_names = []

    for file in files:
        with open(path + "/" + file, "rb") as f:
            parser = MyParser()
            parser.feed(str(f.read(), "utf-8"))
            data = parser.data_list

            get_player_data(data, players, player_names, my_team)

            f.close()



    stats = []
    stats.append(["Name", "Goals", "Assists", "Points", "Penalties", "PIM"])

    for player in players:
        stats.append([player.name, player.goals, player.assists, player.points, player.penalties, player.pim])

    with open('data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(stats)

