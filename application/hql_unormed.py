# coding: utf-8
# Semelhante ao hql.py, mas em vez de gerar structs, gera tabelas separadas.

import json
import pdb
import os


class Struct:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []
        self.attributes = {}
    
    def __repr__(self):
        return self.name

    def create_struct(self):
        # Id próprio da tabela. Nem todas as tabelas possuem um PRIMARY KEY
        fields = [f"{self.name}_id BIGINT "]
        for name, attr in self.attributes.items():
            data_type = {
                'N': f"DECIMAL({attr['size']}, {attr['decimal']})"
                    if attr['decimal'] != '-' else 'INT',
                'C': f"VARCHAR({attr['size']})",
                'D': f"DATE"
            }[attr['att_type']]
            oc_min, oc_max = attr['occurence'].split('-')
            primary_key = 'PRIMARY KEY' if attr['element'] == 'A' else ''
            constraint = 'NOT NULL' if int(oc_min) > 0 else ''
            fields.append(f"{name} {data_type} {primary_key} ")
        for child_dict in self.children:
            child = child_dict['table']
            oc_min, oc_max = child_dict['occurence'].split('-')
            data_type = "ARRAY<BIGINT>" if oc_max == 'N' or int(oc_max) > 1 else "BIGINT"
            constraint = 'NOT NULL' if int(oc_min) > 0 else ''
            foreign = f"FOREIGN KEY REFERENCES {child.name}({child.name}_id)"
            fields.append(f"{child.name}_id {data_type} ")
        fields_str = ',\n\t'.join(fields)
        return fields_str

    def create_hql(self, location):
        return f"""
CREATE EXTERNAL TABLE {self.name}(
    {self.create_struct()},
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
    HQL_UNORMED_FOLDER = CONFIG['HQL_UNORMED_FOLDER']
    DB_LOCATION = CONFIG['DB_LOCATION']

os.makedirs(HQL_UNORMED_FOLDER, exist_ok=True)

eSocial = Struct('eSocial')
for table_number, table_info in table_numbers.items():
    hierarchy_q = {'eSocial': eSocial}
    for i, t in enumerate(table_info['matrix'][2:]):
        if len(t) != 9:
            print(table_number, table_info['matrix'][2:][i-1], t)
    for n, field, parent, element, att_type, occurence, size, decimal, desc in table_info['matrix'][2:]:
        GROUP_TAG = ['G', 'CG']
        if parent not in hierarchy_q:
            hierarchy_q[parent] = Struct(parent)
        table = hierarchy_q[parent]
        if element in GROUP_TAG:
            if field not in hierarchy_q:
                hierarchy_q[field] = Struct(field)
            child_table = hierarchy_q[field]
            child_table.parent = table
            table.children.append({'occurence': occurence, 'table': child_table})
        else:
            table.attributes[field] = {
                'element': element,
                'att_type': att_type,
                'occurence': occurence,
                'size': size,
                'decimal': decimal
            }
    for name, table in hierarchy_q.items():
        if name != 'eSocial':
            with open(f"{HQL_UNORMED_FOLDER}/{table_number}_{name}.hql", 'w') as f:
                f.write(table.create_hql(DB_LOCATION))

with open(f"{HQL_UNORMED_FOLDER}/{eSocial}.hql", 'w') as f:
                f.write(eSocial.create_hql(DB_LOCATION))
