import pandas as pd
import numpy as np
import re
import time
import base64



# ===

def has_number(string):
    return any(char.isdigit() for char in string)

def remove_currency(value):
    value = value.replace('R$', '')
    value = value.replace(' ', '')

    return value

def to_float(value):
    value = remove_currency(value)
    original = value

    # prevent dates from being converted
    if ":" in value:
        return value

    # prevent "-" from being converted
    if value.strip() == '-':
        return 0.0

    if not has_number(value):
        return value

    value = get_str_as_number(value)

    parts = value.split('.')
    if (len(parts[1]) > 2):
        print("\nError", original, " | ", value,  "\n")
        raise ValueError

    return float(value)

def get_str_as_number(value):
    original = value
    value = f"{value}"
    pattern = r'\s|R\$'
    value = re.sub(pattern, '', value)

    value = value.replace('.', '')
    value = value.replace(',', '')

    value = value.strip()

    as_str= value[:-2] + '.' + value[-2:]

    return as_str

def to_currency(value):
    if value < 1e3:
        return f"{value:.2f}"
    elif value < 1e6:
        return f"{value / 1e3:.2f} K"
    elif value < 1e9:
        return f"{value / 1e6:.2f} M"
    elif value < 1e12:
        return f"{value / 1e9:.2f} B"
    else:
        return f"{value / 1e12:.2f} T"


# ===

# Importar arquivo Excel
df = pd.read_excel('./cofre.xlsx', sheet_name=['Gastos', 'Quantidade'])

# Acessar a aba 'Gastos'
df_gastos = df['Gastos']

# Acessar a aba 'Quantidade'
df_quantidade = df['Quantidade']

# Lista correta de estados
fields = [
    "AC", "AL", "AM", "AP", "BA", "BR", "CE", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO", 'Total'
]

# Atualizar a coluna 'Estado' com a lista correta
df_gastos['Estado'] = fields
df_quantidade['Estado'] = fields


df_gastos.replace('-', 0.0, inplace=True)

# # Aplicar a função to_float às colunas que não são numéricas

for col in df_gastos.columns[1:]:
    df_gastos[col] = df_gastos[col].map(lambda x: to_float(x) if isinstance(x, str) else x)

df_gastos.drop(columns=['Estado'], inplace=True)
df_gastos.rename(columns={'State': 'Estado'}, inplace=True)
df_gastos = df_gastos[~df_gastos['Estado'].str.startswith('Total')]
gastos_totais = df_gastos.select_dtypes(include=[np.number]).sum(skipna=True)
gastos_totais = gastos_totais.apply(to_currency)
gastos_totais['Estado'] = 'Total R$'
df_gastos = df_gastos._append(gastos_totais, ignore_index=True)
print(df_gastos)

df_quantidade = df_quantidade[~df_quantidade['Estado'].str.startswith('Total')]
quantidade_totais = df_quantidade.select_dtypes(include=[np.number]).sum()
quantidade_totais = quantidade_totais.apply(to_currency)
quantidade_totais['Estado'] = 'Total R$'
quantidade_totais = df_quantidade._append(quantidade_totais, ignore_index=True)
print(quantidade_totais)
