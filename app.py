from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

# Chemin du fichier de sauvegarde
DATA_FILE = 'data.json'
TOTAL_FILE = 'total.json'  # Fichier pour sauvegarder les totaux

# Charger les données depuis le fichier JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

# Sauvegarder les données dans le fichier JSON
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Charger les totaux depuis le fichier JSON
def load_totals():
    if os.path.exists(TOTAL_FILE):
        with open(TOTAL_FILE, 'r') as file:
            return json.load(file)
    return {'gold': 0, 'silver': 0, 'copper': 0}

# Sauvegarder les totaux dans le fichier JSON
def save_totals(totals):
    with open(TOTAL_FILE, 'w') as file:
        json.dump(totals, file, indent=4)

@app.route('/')
def index():
    data = load_data()
    totals = load_totals()
    return render_template('index.html', players=data, totals=totals)

@app.route('/add_player', methods=['POST'])
def add_player():
    player_name = request.form['player_name']
    data = load_data()
    if player_name not in data:
        data[player_name] = {'gold': 0, 'silver': 0, 'copper': 0}
    save_data(data)
    return '', 204  # Réponse vide pour indiquer que l'ajout a réussi

@app.route('/update_money', methods=['POST'])
def update_money():
    player_name = request.form['player_name']
    currency = request.form['currency']  # 'gold', 'silver' ou 'copper'
    amount = int(request.form['amount'])  # +1 ou -1
    
    data = load_data()
    if player_name in data:
        data[player_name][currency] += amount
        # Assurer que les valeurs ne deviennent pas négatives
        data[player_name][currency] = max(0, data[player_name][currency])
    save_data(data)
    return '', 204  # Réponse vide pour indiquer que la mise à jour a réussi

@app.route('/update_money_direct', methods=['POST'])
def update_money_direct():
    player_name = request.form['player_name']
    currency = request.form['currency']  # 'gold', 'silver' ou 'copper'
    amount = int(request.form['amount'])  # Nouvelle valeur
    
    data = load_data()
    if player_name in data:
        data[player_name][currency] = amount
        # Assurer que les valeurs ne deviennent pas négatives
        data[player_name][currency] = max(0, data[player_name][currency])
    save_data(data)
    return '', 204  # Réponse vide pour indiquer que la mise à jour a réussi

@app.route('/update_total', methods=['POST'])
def update_total():
    currency = request.form['currency']  # 'gold', 'silver' ou 'copper'
    amount = int(request.form['amount'])  # Nouvelle valeur
    
    totals = load_totals()
    totals[currency] = amount
    save_totals(totals)
    return '', 204  # Réponse vide pour indiquer que la mise à jour a réussi

@app.route('/delete_player', methods=['POST'])
def delete_player():
    player_name = request.form['player_name']
    data = load_data()
    if player_name in data:
        del data[player_name]
    save_data(data)
    return '', 204  # Réponse vide pour indiquer que la suppression a réussi

@app.route('/update_name', methods=['POST'])
def update_name():
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    data = load_data()
    if old_name in data:
        data[new_name] = data.pop(old_name)
    save_data(data)
    return '', 204  # Réponse vide pour indiquer que la mise à jour a réussi

@app.route('/spend_money', methods=['POST'])
def spend_money():
    player_name = request.form['player_name']
    gold = int(request.form['gold'])
    silver = int(request.form['silver'])
    copper = int(request.form['copper'])
    
    data = load_data()
    if player_name in data:
        data[player_name]['gold'] = max(0, data[player_name]['gold'] - gold)
        data[player_name]['silver'] = max(0, data[player_name]['silver'] - silver)
        data[player_name]['copper'] = max(0, data[player_name]['copper'] - copper)
    save_data(data)
    return '', 204  # Réponse vide pour indiquer que la dépense a réussi

@app.route('/split_money', methods=['POST'])
def split_money():
    total_gold = int(request.form['total_gold'])
    total_silver = int(request.form['total_silver'])
    total_copper = int(request.form['total_copper'])
    
    data = load_data()
    num_players = len(data)
    if num_players > 0:
        gold_per_player = total_gold // num_players
        silver_per_player = total_silver // num_players
        copper_per_player = total_copper // num_players
        
        for player in data:
            data[player]['gold'] += gold_per_player
            data[player]['silver'] += silver_per_player
            data[player]['copper'] += copper_per_player
    
    save_data(data)
    return jsonify(data)  # Renvoyer les données mises à jour

if __name__ == '__main__':
    app.run(debug=True)