import pandas as pd

def format_currency(value):
    """Formata valores como moeda USD com 2 casas decimais"""
    if pd.isna(value):
        return None
    return f"${value:,.2f}"