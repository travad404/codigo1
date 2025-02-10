import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração inicial
st.set_page_config(page_title="Gestão de Resíduos", layout="wide")
st.title("📊 Gestão de Resíduos Sólidos Urbanos")

# ==========================================
# FUNÇÕES DE PROCESSAMENTO DE DADOS (Corrigidas)
# ==========================================
@st.cache_data
def carregar_dados(tabela1, tabela2):
    """Carrega e combina dados das planilhas de gravimetria e fluxo"""
    df_grav = pd.read_excel(tabela1).rename(columns=lambda x: x.strip())
    df_fluxo = pd.read_excel(tabela2).rename(columns=lambda x: x.strip())
    
    # Mesclar dados com sufixos explícitos
    df_completo = df_fluxo.merge(
        df_grav.add_suffix('_grav'),  # Adiciona sufixo '_grav' às colunas da gravimetria
        on="Tipo de unidade, segundo o município informante",
        how="left"
    )
    return df_grav, df_fluxo, df_completo

def calcular_fluxo_ajustado(df_completo):
    """Calcula valores ajustados com referências corretas às colunas"""
    df = df_completo.copy()
    
    # Dicionário de percentuais para entulho
    entulho_components = {
        "Concreto": 0.0677, "Argamassa": 0.1065, "Tijolo": 0.078,
        "Madeira": 0.0067, "Papel": 0.0023, "Plástico": 0.0034,
        "Metal": 0.0029, "Material agregado": 0.0484, "Terra bruta": 0.0931,
        "Pedra": 0.00192, "Caliça Retida": 0.3492, "Caliça Peneirada": 0.2,
        "Cerâmica": 0.0161, "Material orgânico e galhos": 0.0087
    }
    
    # Calcular componentes de Dom+Pub (usando sufixo '_grav' para dados gravimétricos)
    dom_pub_components = {
        "Papel/Papelão": "Papel/Papelão_grav",
        "Plásticos": "Plásticos_grav",
        "Vidros": "Vidros_grav",
        "Metais": "Metais_grav",
        "Orgânicos": "Orgânicos_grav"
    }
    
    for col_final, col_grav in dom_pub_components.items():
        df[col_final] = df["Dom+Pub"] * df[col_grav]
    
    # Calcular componentes de Entulho
    for material, perc in entulho_components.items():
        df[material] = df["Entulho"] * perc
    
    # Calcular métricas adicionais (com sufixos corrigidos)
    df["Valor energético (MJ/ton)"] = df["Saúde"] * df["Valor energético p/Incineração_grav"]
    df["Redução Peso Seco"] = df["Podas"] * df["Redução de peso seco com Podas_grav"]
    df["Redução Peso Líquido"] = df["Podas"] * df["Redução de peso Líquido com Podas_grav"]
    
    return df

# ... (restante do código permanece igual)
