from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'
TOTAL_FILE = 'total.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_totals():
    if os.path.exists(TOTAL_FILE):
        with open(TOTAL_FILE, 'r') as f:
            return json.load(f)
    return {'gold': 0, 'silver': 0, 'copper': 0}

def save_totals(totals):
    with open(TOTAL_FILE, 'w') as f:
        json.dump(totals, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html',
                         players=load_data(),
                         totals=load_totals())

@app.route('/add_player', methods=['POST'])
def add_player():
    data = load_data()
    player = request.form['player_name']
    if player not in data:
        data[player] = {'gold': 0, 'silver': 0, 'copper': 0}
    save_data(data)
    return '', 204

@app.route('/add_to_total', methods=['POST'])
def add_to_total():
    totals = load_totals()
    currency = request.form['currency']
    totals[currency] += int(request.form['amount'])
    save_totals(totals)
    return '', 204

@app.route('/spend_from_total', methods=['POST'])
def spend_from_total():
    totals = load_totals()
    currency = request.form['currency']
    amount = int(request.form['amount'])
    totals[currency] = max(0, totals[currency] - amount)
    save_totals(totals)
    return '', 204

@app.route('/add_money', methods=['POST'])
def add_money():
    data = load_data()
    player = request.form['player_name']
    currency = request.form['currency']
    data[player][currency] += int(request.form['amount'])
    save_data(data)
    return '', 204

@app.route('/spend_money', methods=['POST'])
def spend_money():
    data = load_data()
    player = request.form['player_name']
    currency = request.form['currency']
    amount = int(request.form['amount'])
    data[player][currency] = max(0, data[player][currency] - amount)
    save_data(data)
    return '', 204

@app.route('/delete_player', methods=['POST'])
def delete_player():
    data = load_data()
    player = request.form['player_name']
    if player in data:
        del data[player]
    save_data(data)
    return '', 204

@app.route('/split_money', methods=['POST'])
def split_money():
    totals = load_totals()
    data = load_data()
    players = list(data.keys())
    
    if len(players) > 0:
        for currency in ['gold', 'silver', 'copper']:
            total = totals[currency]
            per_player = total // len(players)
            remainder = total % len(players)
            
            for player in players:
                data[player][currency] += per_player
            if remainder > 0:
                data[players[0]][currency] += remainder
        
        totals = {c: 0 for c in totals}
        save_totals(totals)
        save_data(data)
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)