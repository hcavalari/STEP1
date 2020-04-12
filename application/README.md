São 3 scripts principais.
O primeiro deles extrai o conteúdo da pasta dos pdfs (Configuração PDF_FOLDER)
e os converte em dois textos: index.txt(sumário) e all_text.txt(tabelas).
O segundo faz a distinção entre tabelas distintas e obtém os metadados.
O terceiro pode ser tanto o `hql.py` (usando structs) quanto o `hql_unormed.py`
(denormalizadas). O comando abaixo já faz o pipeline completo.

```python
python pdf2txt.py table_metadata.py hql.py hql_unormed.py
```

As configurações necessárias estão no CONFIG.json.
Os scripts estão comentados onde achei que pudesse haver mais dúvidas.