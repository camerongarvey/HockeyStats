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


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/get_toggle', methods=['GET'])
def get_toggle():
    return jsonify(toggle_state)

@app.route('/set_toggle', methods=['POST'])
def set_toggle():
    data = request.get_json()
    toggle_state['enabled'] = data.get('enabled', False)
    return jsonify(success=True)

@app.route('/teams')
def teams():
    parent_folder = 'data'
    downloaded_teams = [f for f in os.listdir(parent_folder)
                        if os.path.isdir(os.path.join(parent_folder, f))]
    return render_template('teams.html', downloaded_teams=downloaded_teams)


@app.route('/display-stats', methods=['POST'])
def display_stats():
    team_name = request.form.get('team_name')
    if team_name:
        process_data.run(team_name)
        return redirect("/stats")
    return redirect(url_for('data'))


@app.route('/update-data', methods=['POST'])
def update_data():
    team_name = request.form.get('team_name')
    if team_name:
        bot.run(source[team_name], team_name)
    return redirect(url_for('data'))


@app.route('/delete-data', methods=['POST', 'GET'])
def delete_data():
    team_name = request.form.get('team_name')
    if team_name:
        for file in os.listdir(PATH + team_name):
            os.remove(PATH + team_name + '/' + file)
        os.removedirs(PATH + team_name)
    return redirect(url_for('data'))


@app.route("/header")
def header():
    return render_template('header.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    years = ['2025']
    teams = []
    for item in source:
        teams.append(item)

    selected_year = None
    selected_team = None

    if request.method == 'POST':
        selected_year = request.form.get('year')
        selected_team = request.form.get('team')

        print(f"User selected year: {selected_year}")
        print(f"User selected team: {selected_team}")

        global loaded

        if loaded != selected_team:
            bot.run(source[selected_team], selected_team)
            processor.run(selected_team)
            loaded = selected_team

        return redirect("/stats")

    return render_template(
        'index.html',
        years=years,
        teams=teams,
        selected_year=selected_year,
        selected_team=selected_team
    )


@app.route('/stats')
def stats():
    df = pd.read_csv('data.csv')
    return render_template('table.html', table=df.to_dict(orient='records'), columns=df.columns)


if __name__ == '__main__':
    app.run()
