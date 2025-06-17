from flask import Flask, render_template, request, redirect
from data_sources import source
import scraper as bot
import process_data as processor
import pandas as pd

app = Flask(__name__)
loaded = None


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
            bot.run(source[selected_team])
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
    app.run(debug=True)
