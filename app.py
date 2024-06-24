import json
import csv
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Função para carregar os dados do arquivo JSON
def carregar_dados():
    try:
        with open('dados.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Função para salvar os dados no arquivo JSON
def salvar_dados(dados):
    with open('dados.json', 'w') as file:
        json.dump(dados, file)
    salvar_tabela_csv(dados)

# Função para salvar os dados em um arquivo CSV
def salvar_tabela_csv(dados):
    with open('estoque.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Produto", "Quantidade"])
        for produto, quantidade in dados.items():
            writer.writerow([produto, quantidade])

# Carregar os dados ao iniciar
estoque = carregar_dados()

@app.route('/')
def index():
    return render_template_string('''
        <!doctype html>
        <html>
            <head>
                <title>Spigo.Estoque</title>
            </head>
            <body>
                <h1>Estoque</h1>
                <ul>
                {% for produto, quantidade in estoque.items() %}
                    <li>{{ produto }}: {{ quantidade }}</li>
                {% endfor %}
                </ul>
                <form action="/processar_comando" method="post">
                    <label for="comando">Comando (quantidade produto):</label>
                    <input type="text" id="comando" name="comando">
                    <input type="radio" id="adicionar" name="modo" value="Adicionar" checked>
                    <label for="adicionar">Adicionar</label>
                    <input type="radio" id="remover" name="modo" value="Remover">
                    <label for="remover">Remover</label>
                    <button type="submit">Executar</button>
                </form>
            </body>
        </html>
    ''', estoque=estoque)

@app.route('/processar_comando', methods=['POST'])
def processar_comando():
    comando_texto = request.form['comando']
    modo = request.form['modo']
    try:
        quantidade, produto = comando_texto.split(' ', 1)
        quantidade = int(quantidade)
    except ValueError:
        return jsonify({'erro': 'Comando inválido!'}), 400

    if modo == "Adicionar":
        adiciona(produto, quantidade)
    elif modo == "Remover":
        remove(produto, quantidade)
    
    return index()

def adiciona(produto, quantidade):
    if produto in estoque:
        estoque[produto] += quantidade
    else:
        estoque[produto] = quantidade
    salvar_dados(estoque)

def remove(produto, quantidade):
    if produto in estoque:
        estoque[produto] -= quantidade
        if estoque[produto] <= 0:
            del estoque[produto]
        salvar_dados(estoque)
    else:
        return jsonify({'erro': 'Produto não cadastrado!'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
