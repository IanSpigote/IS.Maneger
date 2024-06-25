import json
import csv
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Função para carregar os dados do JSON
def carregar_dados():
    try:
        with open('dados.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Função para salvar os dados no JSON
def salvar_dados(dados):
    with open('dados.json', 'w') as file:
        json.dump(dados, file)

# Função para carregar os dados do CSV para o dicionário `estoque`
def carregar_estoque_from_csv():
    global estoque
    estoque = {}
    with open('estoque.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            produto = row['produto']
            quantidade = int(row['quantidade'])
            estoque[produto] = quantidade

# Função para salvar o dicionário `estoque` de volta ao CSV
def salvar_estoque_to_csv():
    with open('estoque.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['produto', 'quantidade'])
        writer.writeheader()
        for produto, quantidade in estoque.items():
            writer.writerow({'produto': produto, 'quantidade': quantidade})

# Rota para a página inicial que renderiza o template index.html
@app.route('/')
def index():
    carregar_estoque_from_csv()
    return render_template('index.html', estoque=estoque)

# Rota para adicionar ou remover produtos do estoque
@app.route('/atualizar', methods=['POST'])
def atualizar_estoque():
    comando = request.form['comando']
    
    # Interpretar o comando
    partes = comando.split(maxsplit=2)
    if len(partes) != 3:
        return "Comando inválido. Use 'Adicionar 2 morango' ou 'Remover 2 pistache'."

    operacao, quantidade_str, produto = partes
    try:
        quantidade = int(quantidade_str)
    except ValueError:
        return "Quantidade inválida. Use um número inteiro para a quantidade."

    # Atualizar o estoque baseado na operação
    if operacao.lower() == 'adicionar':
        if produto in estoque:
            estoque[produto] += quantidade
        else:
            estoque[produto] = quantidade
    elif operacao.lower() == 'remover':
        if produto in estoque:
            estoque[produto] -= quantidade
            if estoque[produto] < 0:
                estoque[produto] = 0  # Evitar estoque negativo
        else:
            return "Produto não encontrado no estoque."
    else:
        return "Operação inválida. Use 'Adicionar' ou 'Remover'."

    # Salvar as alterações no JSON e CSV
    salvar_dados(estoque)
    salvar_estoque_to_csv()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
