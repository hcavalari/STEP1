# coding: utf-8

from unidecode import unidecode as uni
import json
import pdb
import re

with open('index.txt', 'r') as f:    # Ler o sumário
    index = f.read()
with open('all_text.txt', 'r') as f: # Ler as tabelas em texto
    all_text = f.read()

# Regex que identifica o título de todas as tabelas, sendo do tipo 'Registro' ou não
TABLE_TITLE_REGEX = r'\n((Registros do \n?evento )?S\n-\n(\d+) \n-\n \n([\w,. /]+\n))'
titles = re.findall(TABLE_TITLE_REGEX, all_text, re.MULTILINE|re.UNICODE)
# As tabelas são o conteúdo entre dois títulos consecutivos
tables = re.sub(TABLE_TITLE_REGEX, '$', all_text).split('$')[1:]

# Dicionário que contém como chave o número da tabela, e como valor o nome da tabela
# e seus dados, como uma list(list(string))
table_numbers = {
    re.sub(r'\n', '', number): {
        'name': re.sub(r'[\-/\.,\s]+', '_', uni(desc[:-3].lower().replace('\n', '')))
    }
    for number, desc in re.findall(
        # Procura no índice o número  e nome da tabela
        r' \nS\n-\n(\d+(?:\n\d+)?) \n-\n \n((?:(?:\w[\w,\. /]+| |-)\n)+)\.{2,}',
        index, re.IGNORECASE)
}

# Um grande problema é que o único separador presente nas tabelas é a quebra de linha ('\n \n').
# Entretanto, em muitos textos do campo 'Condição' há quebras de linha, o que impede diferenciar
# se uma quebra representa uma nova célula da tabela ou uma quebra de linha dentro da mesma célula.
# Isso será explicado adiante.

for title, table in list(zip(titles, tables))[1::2]:
    # Transforma o campo 'Ocorr.' para uma única linha
    tables_cells = re.sub(r'(\d+)\n-\n(\d+)', r'\g<1>-\g<2>', table)
    # Transforma textos quebrados numa única linha
    tables_cells = re.sub(r'(\w) \n-\n \n(\w)', r'\g<1>-\g<2>', tables_cells, re.IGNORECASE|re.MULTILINE)
    # Remove texto inútil antes da tabela. Há uma exceção no texto da tabela '2245'
    split_index = {'2245': 4}.get(title[2], 2)
    # Divide o texto pelo regex, para obter as células
    tables_cells = re.sub('\n \n', '$', tables_cells).strip().split('$')[split_index:]
    # Insere células ausentes no início para ficar no formato certo (9 colunas cada)
    tables_cells.insert(0, '')
    tables_cells.insert(11, '')
    matrix = []
    i = 0
    while i < len(tables_cells):
        # Insere linha na tabela
        matrix.append(tables_cells[i:i+9])
        # No campo 'Condição' há muitas linhas quebradas. Uma forma de contornar
        # isso é ir adicionando as células na última linha até que a próxima
        # célula seja somente um número. Aí garantimos que quebramos a linha
        # no lugar certo
        while (i+9 < len(tables_cells)) and (not re.match(r'^[1-9][\d\n]*$', tables_cells[i+9])):
            matrix[-1][-1] += tables_cells.pop(i+9)
        # Exceção a regra na tabela 1010 linha 92
        if title[2] == '1010' and matrix[-1][0] == '92':
            matrix[-2][-1] += ' '.join(matrix.pop(-1))
        i += 9
    for i, row in enumerate(matrix):
        # Remove todas as quebras de linha
        matrix[i] = [re.sub(r'\n', '', col) for col in row]
    table_numbers[title[2]]['matrix'] = matrix

with open('all_tables_metadata.json', 'w') as f:
    json.dump(table_numbers, f)