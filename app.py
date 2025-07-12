import os

from flask import Flask, render_template, request, redirect, url_for, jsonify

import process_data
from data_sources import source
import scraper as bot
import process_data as processor
import pandas as pd

app = Flask(__name__)
loaded = None
toggle_state = {'enabled': False}  # Global dictionary
PATH = "data/"

data_map = {}

for item in source:
    data_map[item[0]] = item[1]


#Start of Webpages
@app.route('/', methods=['GET', 'POST'])
def index():
    years = list(data_map.keys())

    if request.method == 'POST':
        selected_year = request.form.get('year')
        selected_association = request.form.get('association')
        selected_team = request.form.get('team')

        if not (selected_year and selected_association and selected_team and selected_year in years):
            return redirect(url_for('index'))

        print(f"User selected year: {selected_year}")
        print(f"User selected association: {selected_association}")
        print(f"User selected team: {selected_team}")

        global loaded

        if loaded != selected_association + ' ' + selected_association:

            bot.run(data_map[selected_year][selected_association][selected_team],
                    selected_association + ' ' + selected_team)
            processor.run(selected_association + ' ' + selected_team)
            loaded = selected_association + ' ' + selected_team

        return redirect("/stats")

    return render_template(
        'index.html',
        years=years,
    )


@app.route('/teams')
def teams():
    parent_folder = 'data'
    downloaded_teams = [f for f in os.listdir(parent_folder)
                        if os.path.isdir(os.path.join(parent_folder, f))]
    downloaded_teams.sort()
    return render_template('teams.html', downloaded_teams=downloaded_teams)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/stats')
def stats():
    df = pd.read_csv('data.csv')
    return render_template('table.html', table=df.to_dict(orient='records'), columns=df.columns)


#End of Webpages



#Start of Settings Options
@app.route('/get_toggle', methods=['GET'])
def get_toggle():
    return jsonify(toggle_state)


@app.route('/set_toggle', methods=['POST'])
def set_toggle():
    data = request.get_json()
    toggle_state['enabled'] = data.get('enabled', False)
    return jsonify(success=True)


#End of Settings Options


#Start of Buttons on Teams Page
@app.route('/display-stats', methods=['POST'])  #Display Button
def display_stats():
    team_name = request.form.get('team_name')
    if team_name:
        process_data.run(team_name)
        return redirect("/stats")
    return redirect(url_for('data'))


@app.route('/update-data', methods=['POST'])  #Update Button
def update_data():
    team_name = request.form.get('team_name')
    if team_name:
        pass
        #bot.run(source[team_name], team_name)
    return redirect(url_for('teams'))


@app.route('/delete-data', methods=['POST', 'GET'])  #Delete Button
def delete_data():
    team_name = request.form.get('team_name')
    if team_name:
        for file in os.listdir(PATH + team_name):
            os.remove(PATH + team_name + '/' + file)
        os.removedirs(PATH + team_name)
    return redirect(url_for('teams'))

#Start of Buttons on Teams Page


@app.route("/header")  #Header bar
def header():
    return render_template('header.html')


@app.route('/get-associations')  #Dynamiclly Loads Associations on Home page
def get_associations():
    year = request.args.get('year')
    t = []
    for i in data_map.get(year).keys():
        t.append(i)
    t.sort()
    return jsonify(t)


@app.route('/get-teams')  #Dynamiclly Loads Teams on Home page
def get_teams():
    year = request.args.get('year')
    association = request.args.get('association')
    t = []
    print(data_map)
    for i in data_map.get(year).get(association).keys():
        t.append(i)
    t.sort()
    return jsonify(t)


if __name__ == '__main__':
    app.run()
