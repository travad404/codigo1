import streamlit as st

# Dicionário com os limites por estado
limites_por_estado = {
    "Acre": 300, "Alagoas": 100, "Amapá": 200, "Amazonas": 200,
    "Bahia": 300, "Ceará": 100, "Distrito Federal": 120, "Espírito Santo": 200,
    "Goiás": 120, "Maranhão": 200, "Mato Grosso": 200, "Mato Grosso do Sul": 200,
    "Minas Gerais": 200, "Pará": 200, "Paraíba": 200, "Paraná": 100,
    "Pernambuco": 100, "Piauí": 120, "Rio de Janeiro": 120, "Rio Grande do Norte": 200,
    "Rio Grande do Sul": 300, "Rondônia": 200, "Roraima": 200, "Santa Catarina": 120,
    "São Paulo": 200, "Sergipe": 200, "Tocantins": 120
}

# Título do aplicativo
st.title("Classificação de Gerador de Resíduos")

# Perguntar o estado
estado = st.selectbox("Selecione o estado:", list(limites_por_estado.keys()))

# Perguntar quantidade de resíduos gerados
quantidade = st.number_input("Informe a quantidade de resíduos gerados por dia (em kg):", min_value=0)

# Verificar se é um grande gerador
limite = limites_por_estado[estado]
grande_gerador = quantidade > limite

# Classificação dos resíduos com base em perguntas adicionais
st.write("Agora, vamos classificar os resíduos gerados.")

# Perguntar se consta nos anexos A ou B
consta_anexos = st.radio("O resíduo consta nos anexos A ou B?", ("Sim", "Não"))

# Perguntar características de periculosidade
perigoso = st.radio(
    "O resíduo apresenta características de inflamabilidade, corrosividade, reatividade, toxicidade ou patogenicidade?",
    ("Sim", "Não")
)

# Perguntar sobre solubilidade em concentrações superiores ao anexo G
solubilidade = st.radio(
    "O resíduo possui constituintes que são solubilizados em concentrações superiores ao anexo G?",
    ("Sim", "Não")
)

# Lógica de classificação
if st.button("Classificar"):
    # Verificar grande gerador
    if grande_gerador:
        st.warning(f"Você é considerado um grande gerador de resíduos no estado de {estado}.")
    else:
        st.success(f"Você NÃO é considerado um grande gerador de resíduos no estado de {estado}.")

    # Classificação de periculosidade
    if perigoso == "Sim":
        st.error("O resíduo gerado é classificado como PERIGOSO (Classe I).")
    else:
        if consta_anexos == "Sim":
            st.info("O resíduo gerado é classificado como NÃO PERIGOSO - NÃO INERTE (Classe II A).")
        elif solubilidade == "Sim":
            st.info("O resíduo gerado é classificado como NÃO PERIGOSO - NÃO INERTE (Classe II A).")
        else:
            st.success("O resíduo gerado é classificado como NÃO PERIGOSO - INERTE (Classe II B).")
