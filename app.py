import pandas as pd
import streamlit as st
import plotly.express as px

# Função para carregar os dados das tabelas
@st.cache_data
def carregar_tabelas(tabela1_path, tabela2_path):
    gravimetria_data = pd.read_excel(tabela1_path)
    resumo_fluxo_data = pd.read_excel(tabela2_path)
    gravimetria_data.columns = gravimetria_data.columns.str.strip()  # Limpando espaços
    resumo_fluxo_data.columns = resumo_fluxo_data.columns.str.strip()  # Limpando espaços
    return gravimetria_data, resumo_fluxo_data


# Percentuais para entulhos
percentuais_entulho = {
    "Concreto": 0.0677, "Argamassa": 0.1065, "Tijolo": 0.078, "Madeira": 0.0067,
    "Papel": 0.0023, "Plástico": 0.0034, "Metal": 0.0029, "Material agregado": 0.0484,
    "Terra bruta": 0.0931, "Pedra": 0.00192, "Caliça Retida": 0.3492,
    "Caliça Peneirada": 0.2, "Cerâmica": 0.0161, "Material orgânico e galhos": 0.0087,
    "Outros": 0
}

# Função para calcular o fluxo ajustado
def calcular_fluxo_ajustado(gravimetria_data, resumo_fluxo_data):
    fluxo_ajustado = []  # Lista para armazenar os resultados
    for index, row in resumo_fluxo_data.iterrows():
        uf = row["UF"]
        unidade = row["Tipo de unidade, segundo o município informante"]
        ajuste_residuos = {"UF": uf, "Unidade": unidade}
        
        for residuo in ["Dom+Pub", "Entulho", "Podas", "Saúde", "Outros"]:
            if residuo in resumo_fluxo_data.columns:
                gravimetricos = gravimetria_data[gravimetria_data["Tipo de unidade, segundo o município informante"] == unidade]
                if not gravimetricos.empty:
                    gravimetricos = gravimetricos.iloc[0]
                    if residuo == "Dom+Pub":
                        ajuste_residuos.update({
                            "Papel/Papelão": row[residuo] * gravimetricos.get("Papel/Papelão", 0),
                            "Plásticos": row[residuo] * gravimetricos.get("Plásticos", 0),
                            "Vidros": row[residuo] * gravimetricos.get("Vidros", 0),
                            "Metais": row[residuo] * gravimetricos.get("Metais", 0),
                            "Orgânicos": row[residuo] * gravimetricos.get("Orgânicos", 0),
                        })
                    elif residuo == "Entulho":
                        for material, percentual in percentuais_entulho.items():
                            ajuste_residuos[material] = row[residuo] * percentual
                    elif residuo == "Saúde":
                        ajuste_residuos["Valor energético (MJ/ton)"] = row[residuo] * gravimetricos.get("Valor energético p/Incineração", 0)
                    elif residuo == "Podas":
                        ajuste_residuos["Redução Peso Seco"] = row[residuo] * gravimetricos.get("Redução de peso seco com Podas", 0)
                        ajuste_residuos["Redução Peso Líquido"] = row[residuo] * gravimetricos.get("Redução de peso Líquido com Podas", 0)
                    elif residuo == "Outros":
                        ajuste_residuos["Outros Processados"] = row[residuo] * gravimetricos.get("Outros", 0)
        fluxo_ajustado.append(ajuste_residuos)
    return pd.DataFrame(fluxo_ajustado)

# Aplicação Streamlit
st.set_page_config(page_title="Gestão de Resíduos", layout="wide")
st.title("📊 Gestão de Resíduos Sólidos Urbanos")
st.sidebar.header("Configurações de Entrada")

# Upload das planilhas
tabela1_path = st.sidebar.file_uploader("Carregue a Tabela 1 (Gravimetria por Tipo de Unidade)", type=["xlsx"])
tabela2_path = st.sidebar.file_uploader("Carregue a Tabela 2 (Resumo por Unidade e UF)", type=["xlsx"])

if tabela1_path and tabela2_path:
    gravimetria_data, resumo_fluxo_data = carregar_tabelas(tabela1_path, tabela2_path)
    fluxo_ajustado = calcular_fluxo_ajustado(gravimetria_data, resumo_fluxo_data)

    # Criação de abas
    aba1, aba2 = st.tabs(["📊 Resumo e Gráficos Gerais", "🔍 Análise por UF e Unidade"])

    # Aba 1 - Resumo e Gráficos Gerais
    with aba1:
        st.header("Resumo dos Indicadores")
        total_residuos = fluxo_ajustado.filter(regex="Papel|Plásticos|Vidros|Metais|Orgânicos|Concreto|Argamassa").sum().sum()
        total_entulho = fluxo_ajustado.filter(regex="Concreto|Argamassa|Tijolo").sum().sum()
        col1, col2 = st.columns(2)
        col1.metric("Total de Resíduos Processados (ton)", f"{total_residuos:,.2f}")
        col2.metric("Total de Entulho Processado (ton)", f"{total_entulho:,.2f}")

        st.header("📈 Resultados Detalhados")
        st.dataframe(fluxo_ajustado)

    # Aba 2 - Análise por UF e Unidade
    with aba2:
        st.header("🔍 Análise por UF e Unidade de Tratamento")
        
        # Seleção de filtros
        uf_selecionado = st.selectbox("Selecione a UF:", fluxo_ajustado["UF"].unique())
        unidade_selecionada = st.selectbox("Selecione o Tipo de Unidade:", fluxo_ajustado["Unidade"].unique())

        # Filtrar dados
        dados_filtrados = fluxo_ajustado[
            (fluxo_ajustado["UF"] == uf_selecionado) &
            (fluxo_ajustado["Unidade"] == unidade_selecionada)
        ]

        # Preparar dados para gráfico de pizza
        if not dados_filtrados.empty:
            residuos_pizza = dados_filtrados.iloc[0].filter(regex="Papel|Plásticos|Vidros|Metais|Orgânicos|Concreto|Argamassa").dropna()
            fig_pizza = px.pie(
                residuos_pizza,
                values=residuos_pizza.values,
                names=residuos_pizza.index,
                title=f"Distribuição de Resíduos para {uf_selecionado} - {unidade_selecionada}"
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado para a combinação selecionada.")
