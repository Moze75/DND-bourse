from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Chemins des fichiers de sauvegarde
DATA_FILE = 'data.json'
TOTAL_FILE = 'total.json'

# Charger les données des joueurs
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

# Sauvegarder les données des joueurs
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Charger les totaux (or, argent, cuivre)
def load_totals():
    if os.path.exists(TOTAL_FILE):
        with open(TOTAL_FILE, 'r') as file:
            return json.load(file)
    return {'gold': 0, 'silver': 0, 'copper': 0}

# Sauvegarder les totaux
def save_totals(totals):
    with open(TOTAL_FILE, 'w') as file:
        json.dump(totals, file, indent=4)

# Route principale
@app.route('/')
def index():
    data = load_data()
    totals = load_totals()
    return render_template('index.html', players=data, totals=totals)

# Ajouter un joueur
@app.route('/add_player', methods=['POST'])
def add_player():
    player_name = request.form['player_name']
    data = load_data()
    if player_name not in data:
        data[player_name] = {'gold': 0, 'silver': 0, 'copper': 0}
    save_data(data)
    return '', 204

# Mettre à jour l'argent d'un joueur
@app.route('/update_money', methods=['POST'])
def update_money():
    player_name = request.form['player_name']
    currency = request.form['currency']
    amount = int(request.form['amount'])
    
    data = load_data()
    if player_name in data:
        data[player_name][currency] += amount
        data[player_name][currency] = max(0, data[player_name][currency])
    save_data(data)
    return '', 204

# Mettre à jour l'argent directement (sans ajout/soustraction)
@app.route('/update_money_direct', methods=['POST'])
def update_money_direct():
    player_name = request.form['player_name']
    currency = request.form['currency']
    amount = int(request.form['amount'])
    
    data = load_data()
    if player_name in data:
        data[player_name][currency] = amount
        data[player_name][currency] = max(0, data[player_name][currency])
    save_data(data)
    return '', 204

# Mettre à jour les totaux (or, argent, cuivre)
@app.route('/update_total', methods=['POST'])
def update_total():
    currency = request.form['currency']
    amount = int(request.form['amount'])
    
    totals = load_totals()
    totals[currency] = amount
    save_totals(totals)
    return '', 204

# Ajouter de la valeur aux totaux
@app.route('/add_to_total', methods=['POST'])
def add_to_total():
    currency = request.form['currency']
    amount = int(request.form['amount'])
    
    totals = load_totals()
    totals[currency] += amount
    save_totals(totals)
    return '', 204

# Dépenser de la valeur des totaux
@app.route('/spend_from_total', methods=['POST'])
def spend_from_total():
    currency = request.form['currency']
    amount = int(request.form['amount'])
    
    totals = load_totals()
    totals[currency] = max(0, totals[currency] - amount)
    save_totals(totals)
    return '', 204

# Supprimer un joueur
@app.route('/delete_player', methods=['POST'])
def delete_player():
    player_name = request.form['player_name']
    data = load_data()
    if player_name in data:
        del data[player_name]
    save_data(data)
    return '', 204

# Mettre à jour le nom d'un joueur
@app.route('/update_name', methods=['POST'])
def update_name():
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    data = load_data()
    if old_name in data:
        data[new_name] = data.pop(old_name)
    save_data(data)
    return '', 204

# Dépenser de l'argent
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
    return '', 204

# Ajouter de l'argent à un joueur
@app.route('/add_money', methods=['POST'])
def add_money():
    player_name = request.form['player_name']
    gold = int(request.form['gold'])
    silver = int(request.form['silver'])
    copper = int(request.form['copper'])
    
    data = load_data()
    if player_name in data:
        data[player_name]['gold'] += gold
        data[player_name]['silver'] += silver
        data[player_name]['copper'] += copper
    save_data(data)
    return '', 204

# Partager l'argent entre les joueurs
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
        
        # Attribuer l'unité indivisible au premier joueur
        first_player = list(data.keys())[0]
        data[first_player]['gold'] += total_gold % num_players
        data[first_player]['silver'] += total_silver % num_players
        data[first_player]['copper'] += total_copper % num_players
        
        for player in data:
            data[player]['gold'] += gold_per_player
            data[player]['silver'] += silver_per_player
            data[player]['copper'] += copper_per_player
    
    save_data(data)
    
    # Remettre à zéro les totaux
    totals = {'gold': 0, 'silver': 0, 'copper': 0}
    save_totals(totals)
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)