import pandas as pd
import streamlit as st
import plotly.express as px


st.set_page_config(
    page_title="Formação e Graduação - Taxa de Conclusão do Ensino Superior",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


caminho_ou_arquivo = "Tabela_3_Areas_gerais_de_formacao_na_graduacao.xlsx"


regiao_do_estado = {
    "Rondônia": "Norte", "Acre": "Norte", "Amazonas": "Norte", "Roraima": "Norte",
    "Pará": "Norte", "Amapá": "Norte", "Tocantins": "Norte",
    "Maranhão": "Nordeste", "Piauí": "Nordeste", "Ceará": "Nordeste",
    "Rio Grande do Norte": "Nordeste", "Paraíba": "Nordeste", "Pernambuco": "Nordeste",
    "Alagoas": "Nordeste", "Sergipe": "Nordeste", "Bahia": "Nordeste",
    "Minas Gerais": "Sudeste", "Espírito Santo": "Sudeste",
    "Rio de Janeiro": "Sudeste", "São Paulo": "Sudeste",
    "Paraná": "Sul", "Santa Catarina": "Sul", "Rio Grande do Sul": "Sul",
    "Mato Grosso do Sul": "Centro-Oeste", "Mato Grosso": "Centro-Oeste",
    "Goiás": "Centro-Oeste", "Distrito Federal": "Centro-Oeste",
}


estados_escolhidos = ["Minas Gerais", "São Paulo", "Mato Grosso", "Espírito Santo", "Paraná"]




@st.cache_data
def carregar_e_limpar(caminho):
    bruto = pd.read_excel(caminho)


    df = bruto.iloc[2:36, 0:4].copy()
    df.columns = ["uf_regiao", "total", "homens", "mulheres"]


    stem = bruto.iloc[2:36, [0, 4, 5, 6]].copy()
    stem.columns = ["uf_regiao", "total", "homens", "mulheres"]


  
    for tabela in [df, stem]:
        tabela["uf_regiao"] = tabela["uf_regiao"].astype(str).str.strip()
        for col in ["total", "homens", "mulheres"]:
            tabela[col] = pd.to_numeric(tabela[col], errors="coerce")
        tabela["percentual_mulheres"] = (tabela["mulheres"] / tabela["total"] * 100).round(2)


    return df, stem




def somar_por_regiao(tabela):
    """Soma os estados de cada região e calcula o % de mulheres."""
    estados = tabela[tabela["uf_regiao"].isin(regiao_do_estado.keys())].copy()
    estados["regiao"] = estados["uf_regiao"].map(regiao_do_estado)


    por_regiao = estados.groupby("regiao")[["total", "homens", "mulheres"]].sum().reset_index()
    por_regiao["percentual_mulheres"] = (
        por_regiao["mulheres"] / por_regiao["total"] * 100
    ).round(2)
    return por_regiao




dados, formacao_stem = carregar_e_limpar(caminho_ou_arquivo)


st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Selecione a Visualização:",
    ["🏠 Visão Geral", "🎓 Formação Acadêmica"]
)


if pagina == "🏠 Visão Geral":
    st.title("📊 Visão Geral - Graduação no Brasil")
    st.dataframe(dados)


    pct_brasil = dados.loc[dados["uf_regiao"] == "Brasil", "percentual_mulheres"].item()
    estados = dados[dados["uf_regiao"].isin(estados_escolhidos)].copy()
    abaixo_brasil = estados[estados["percentual_mulheres"] < pct_brasil]


    st.write(f"Percentual de mulheres no Brasil: {pct_brasil}%")
    st.write(f"Estados abaixo do Brasil: {len(abaixo_brasil)}")
    st.dataframe(
        abaixo_brasil[["uf_regiao", "percentual_mulheres"]].sort_values("percentual_mulheres")
    )


    st.subheader("Cursos STEM")
    pct_brasil_stem = formacao_stem.loc[
        formacao_stem["uf_regiao"] == "Brasil", "percentual_mulheres"
    ].item()
    estados_stem = formacao_stem[formacao_stem["uf_regiao"].isin(estados_escolhidos)].copy()
    abaixo_stem = estados_stem[estados_stem["percentual_mulheres"] < pct_brasil_stem]


    st.write(f"Percentual de mulheres no Brasil (STEM): {pct_brasil_stem}%")
    st.write(f"Estados abaixo do Brasil: {len(abaixo_stem)}")
    st.dataframe(
        abaixo_stem[["uf_regiao", "percentual_mulheres"]].sort_values("percentual_mulheres")
    )


else:
    st.title("🎓 Formação Acadêmica por Região")


    tipo = st.selectbox("Tipo de curso:", ["Todas as áreas", "STEM"])
    if tipo == "Todas as áreas":
        tabela = dados
    else:
        tabela = formacao_stem


    por_regiao = somar_por_regiao(tabela)


    st.subheader("Tabela por região")
    st.dataframe(por_regiao)

    fig1 = px.bar(
        por_regiao,
        x="regiao",
        y="total",
        color="regiao",
        title=f"Total de formados por região ({tipo})",
        labels={"regiao": "Região", "total": "Total de formados"}
    )
    st.plotly_chart(fig1, use_container_width=True)


    fig2 = px.bar(
        por_regiao,
        x="regiao",
        y="percentual_mulheres",
        color="regiao",
        title=f"Percentual de mulheres por região ({tipo})",
        labels={"regiao": "Região", "percentual_mulheres": "% de mulheres"}
    )
    st.plotly_chart(fig2, use_container_width=True)


    fig3 = px.bar(
        por_regiao,
        x="regiao",
        y=["homens", "mulheres"],
        barmode="group",
        title=f"Homens x Mulheres por região ({tipo})",
        labels={"regiao": "Região", "value": "Quantidade", "variable": "Gênero"}
    )
    st.plotly_chart(fig3, use_container_width=True)