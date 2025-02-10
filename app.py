import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração inicial
st.set_page_config(page_title="Gestão de Resíduos", layout="wide")
st.title("📊 Gestão de Resíduos Sólidos Urbanos")

# ==========================================
# FUNÇÕES DE PROCESSAMENTO DE DADOS
# ==========================================
@st.cache_data
def carregar_dados(tabela1, tabela2):
    """Carrega e combina dados das planilhas de gravimetria e fluxo"""
    df_grav = pd.read_excel(tabela1).rename(columns=lambda x: x.strip())
    df_fluxo = pd.read_excel(tabela2).rename(columns=lambda x: x.strip())
    
    # Mesclar dados para acesso rápido aos percentuais
    df_completo = df_fluxo.merge(
        df_grav,
        on="Tipo de unidade, segundo o município informante",
        how="left"
    )
    return df_grav, df_fluxo, df_completo

def calcular_fluxo_ajustado(df_completo):
    """Calcula valores ajustados usando operações vetorizadas"""
    # Cópia segura para evitar warnings
    df = df_completo.copy()
    
    # Dicionário de percentuais para entulho
    entulho_components = {
        "Concreto": 0.0677, "Argamassa": 0.1065, "Tijolo": 0.078,
        "Madeira": 0.0067, "Papel": 0.0023, "Plástico": 0.0034,
        "Metal": 0.0029, "Material agregado": 0.0484, "Terra bruta": 0.0931,
        "Pedra": 0.00192, "Caliça Retida": 0.3492, "Caliça Peneirada": 0.2,
        "Cerâmica": 0.0161, "Material orgânico e galhos": 0.0087
    }
    
    # Calcular componentes de Dom+Pub
    dom_pub_components = [
        "Papel/Papelão", "Plásticos", "Vidros", 
        "Metais", "Orgânicos"
    ]
    for col in dom_pub_components:
        df[col] = df["Dom+Pub"] * df[col + "_y"]
    
    # Calcular componentes de Entulho
    for material, perc in entulho_components.items():
        df[material] = df["Entulho"] * perc
    
    # Calcular métricas adicionais
    df["Valor energético (MJ/ton)"] = df["Saúde"] * df["Valor energético p/Incineração"]
    df["Redução Peso Seco"] = df["Podas"] * df["Redução de peso seco com Podas"]
    df["Redução Peso Líquido"] = df["Podas"] * df["Redução de peso Líquido com Podas"]
    
    return df

# ==========================================
# FUNÇÕES DE VISUALIZAÇÃO
# ==========================================
def criar_grafico(df, cols, title, height=500):
    """Cria gráfico de barras agrupadas para múltiplas colunas"""
    df_melt = df.melt(id_vars="UF", value_vars=cols, var_name="Componente")
    fig = px.bar(
        df_melt, x="UF", y="value", color="Componente",
        title=title, height=height
    )
    fig.update_layout(barmode="stack")
    return fig

# ==========================================
# INTERFACE STREAMLIT
# ==========================================
with st.sidebar:
    st.header("Configurações de Entrada")
    tabela1 = st.file_uploader("Tabela 1 - Gravimetria", type="xlsx")
    tabela2 = st.file_uploader("Tabela 2 - Fluxo de Resíduos", type="xlsx")

if tabela1 and tabela2:
    # Carregar e processar dados
    df_grav, df_fluxo, df_completo = carregar_dados(tabela1, tabela2)
    df_ajustado = calcular_fluxo_ajustado(df_completo)
    
    # Seção de métricas
    st.header("📈 Métricas Principais")
    total_residuos = df_ajustado.select_dtypes(include='number').sum().sum()
    total_entulho = df_ajustado["Entulho"].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("Total de Resíduos Processados (ton)", f"{total_residuos:,.2f}")
    col2.metric("Total de Entulho Processado (ton)", f"{total_entulho:,.2f}")
    
    # Seção de gráficos
    st.header("📊 Visualizações")
    
    # Gráfico para componentes urbanos
    componentes_urbanos = [
        "Papel/Papelão", "Plásticos", "Vidros", 
        "Metais", "Orgânicos"
    ]
    st.plotly_chart(
        criar_grafico(
            df_ajustado.groupby("UF")[componentes_urbanos].sum().reset_index(),
            componentes_urbanos,
            "Composição de Resíduos Urbanos por UF"
        ), 
        use_container_width=True
    )
    
    # Gráfico para entulho
    componentes_entulho = list(entulho_components.keys())
    st.plotly_chart(
        criar_grafico(
            df_ajustado.groupby("UF")[componentes_entulho].sum().reset_index(),
            componentes_entulho,
            "Composição de Entulho por UF"
        ), 
        use_container_width=True
    )
    
    # Gráfico para valor energético
    if "Valor energético (MJ/ton)" in df_ajustado:
        st.plotly_chart(
            px.bar(
                df_ajustado.groupby("UF")["Valor energético (MJ/ton)"].sum().reset_index(),
                x="UF", y="Valor energético (MJ/ton)",
                title="Valor Energético por Incineração"
            ),
            use_container_width=True
        )
