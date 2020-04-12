# coding: utf-8


import json
import pdb
import os


class Struct:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []
        self.attributes = {}
        hierarchy_q[name] = self
    
    def __repr__(self):
        return self.name

    
    # Função recursiva que cria as structs hive
    # 'Level' é o nível de identação
    def create_struct(self, level):
        # Identação do texto
        spaces = '  ' * level
        fields = []
        for name, attr in self.attributes.items():
            # Converte o tipo descrito em 'Tipo' para HQL
            data_type = {
                'N': f"DECIMAL({attr['size']}, {attr['decimal']})"
                    if attr['decimal'] != '-' else 'INT',
                'C': f"VARCHAR({attr['size']})",
                'D': f"DATE"
            }[attr['att_type']]
            # Números de ocorrência: min e max
            oc_min, oc_max = attr['occurence'].split('-')
            primary_key = 'PRIMARY KEY' if attr['element'] == 'A' else ''
            constraint = 'NOT NULL' if int(oc_min) > 0 else ''
            if level > 0:
                fields.append(f"{spaces}{name}: {data_type}")
            else:
                fields.append(f"{spaces}{name} {data_type} {primary_key} {constraint}")
        for child_dict in self.children:
            child = child_dict['table']
            oc_min, oc_max = child_dict['occurence'].split('-')
            # Chamada recursiva da estrutura filha
            data_type = f"""STRUCT<
{child.create_struct(level+1)}
{spaces}>"""
            if oc_max == 'N' or int(oc_max) > 1:
            # Se há mais de uma ocorrência possível, insere como array
                data_type = f"""ARRAY<
{spaces}{data_type}
{spaces}>"""
            if level > 0:
                fields.append(f"{spaces}{child.name}: {data_type}")
            else:
                fields.append(f"{spaces}{child.name} {data_type}")
        fields_str = ',\n'.join(fields)
        return fields_str

    # Função que cria o 'CREATE TABLE' HQL
    def create_hql(self, location):
        return f"""
CREATE EXTERNAL TABLE {self.name}(
{self.create_struct(1)},
)
row format delimited
fields terminated by ','
collection items terminated by '|'
stored as parquet
location '{location}';
"""


with open('all_tables_metadata.json', 'r') as f:
    table_numbers = json.load(f)

with open('CONFIG.json', 'r') as f:
    CONFIG = json.load(f)
    HQL_FOLDER = CONFIG['HQL_FOLDER']
    DB_LOCATION = CONFIG['DB_LOCATION']

os.makedirs(HQL_FOLDER, exist_ok=True)


for table_number, table_info in table_numbers.items():
    # Estrutura auxiliar para montar a árvore (hierarquia de structs)
    hierarchy_q = {}
    # Campos da tabela de metadados
    for _, field, parent, element, att_type, occurence, size, decimal, desc in table_info['matrix'][2:]:
        GROUP_TAG = ['G', 'CG']
        # A struct atual é a descrita em 'parent'.
        # Se o elemento é um grupo, 'field' é uma nova struct. Caso contrário, é um campo simples(integer, string, etc )
        table = hierarchy_q[parent] if parent in hierarchy_q else Struct(parent)
        if element in GROUP_TAG:
            # No caso de grupos, ligo a struct pai à struct filha
            child_table = hierarchy_q[field] if field in hierarchy_q else Struct(field)
            child_table.parent = table
            table.children.append({'occurence': occurence, 'table': child_table})
        else:
            table.attributes[field] = {
                'element': element, # Grupo, Atributo ou Elemento
                'att_type': att_type, # Char, Numeric ou Date
                'occurence': occurence, # 1-1, 0-1, 1-N, etc...
                'size': size, # Tamanho do campo
                'decimal': decimal # Tamanho da parte decimal
            }
    try:
        with open(f"{HQL_FOLDER}/{table_number}_{table_info['name']}.hql", 'w') as f:
            f.write(hierarchy_q['eSocial'].children[0]['table'].create_hql(DB_LOCATION))
    except (KeyError, ValueError) as e:
        pdb.set_trace()
