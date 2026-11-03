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
    ["🏠 Visão Geral", "🎓 Formação Acadêmica", "📰 Notícias"]
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


elif pagina == "🎓 Formação Acadêmica":
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

else:
    st.title("📰 Notícias sobre Graduação e Ensino Superior")
    st.write("Notícias e dados relacionados ao tema dos gráficos (resumos escritos com as nossas palavras).")


    noticias = [
        {
            "titulo": "Matrículas no ensino superior crescem 30,5% em dez anos",
            "fonte": "Viva (Censo da Educação Superior 2024 / Inep)",
            "data": "22/09/2025",
            "tema": "Censo",
            "resumo": "O Censo 2024 mostra que o Brasil chegou a 10,2 milhões de matriculados, mas o número de concluintes continua em torno de 1 milhão por ano.",
            "link": "https://viva.com.br/carreira-e-educacao/numero-de-matriculas-na-educacao-superior-cresce-305-em-dez-anos.html"
        },
        {
            "titulo": "Concluintes caem tanto na rede pública quanto na privada",
            "fonte": "Tribuna de Minas",
            "data": "27/09/2025",
            "tema": "Conclusão",
            "resumo": "Entre 2023 e 2024 o número de concluintes caiu 0,3% na rede pública e 3,6% na privada. Só um terço dos concluintes do ensino médio entrou na faculdade no ano seguinte.",
            "link": "https://tribunademinas.com.br/noticias/brasil-e-mundo/27-09-2025/brasil-alunos-cursos-ead.html"
        },
        {
            "titulo": "Cotistas das federais concluem mais a graduação",
            "fonte": "TNH1 (dados do Inep)",
            "data": "2025/2026",
            "tema": "Conclusão",
            "resumo": "Segundo o Censo 2024, 49% dos alunos que entraram por cotas nas federais se formaram, contra 42% dos demais ingressantes.",
            "link": "https://www.tnh1.com.br/noticia/nid/censo-50-de-alunos-cotistas-nas-federais-concluem-graduacao/"
        },
        {
            "titulo": "Pedagogia, Direito e Administração formam mais gente",
            "fonte": "Quero Bolsa",
            "data": "2025",
            "tema": "Cursos",
            "resumo": "Pedagogia lidera em número de concluintes (cerca de 1,83 milhão), seguida de Direito (1,61 milhão) e Administração (1,58 milhão).",
            "link": "https://querobolsa.com.br/revista/censo-da-educacao-superior-2024-pedagogia-lidera-entre-ingressantes-e-concluintes"
        },
        {
            "titulo": "Mulheres são maioria na graduação, mas minoria nas áreas CTEM",
            "fonte": "IBGE (Agência de Notícias)",
            "data": "2022 (dados)",
            "tema": "Mulheres / STEM",
            "resumo": "Em 2022, as mulheres eram 60,3% dos concluintes dos cursos presenciais, mas apenas 22% dos concluintes de ciências físicas, tecnologia, engenharia e matemática.",
            "link": "https://agenciadenoticias.ibge.gov.br/media/com_mediaibge/arquivos/9ac298aaf1203418036ae00bf1272e92.pdf"
        },
        {
            "titulo": "Participação feminina entre os concluintes em 2023",
            "fonte": "Revista Pesquisa FAPESP",
            "data": "2023 (dados)",
            "tema": "Mulheres / STEM",
            "resumo": "Gráfico com a participação das mulheres entre os concluintes por área, a partir dos microdados do Censo da Educação Superior.",
            "link": "https://revistapesquisa.fapesp.br/participacao-feminina-entre-concluintes-no-ensino-superior-em-2023/"
        },
        {
            "titulo": "Brasil tem quase 10 milhões de universitários",
            "fonte": "SBT News",
            "data": "2024",
            "tema": "Censo",
            "resumo": "Reportagem sobre o Censo da Educação Superior que registrou 9,9 milhões de alunos, o maior número em nove anos.",
            "link": "https://sbtnews.sbt.com.br/noticia/brasil/numero-de-universitarios-no-brasil-cresce-para-quase-10-milhoes-o-maior-em-nove-anos"
        },
    ]



    temas = ["Todos"]
    for n in noticias:
        if n["tema"] not in temas:
            temas.append(n["tema"])


    tema_escolhido = st.selectbox("Filtrar por tema:", temas)


    contador = 0
    for n in noticias:
        if tema_escolhido == "Todos" or n["tema"] == tema_escolhido:
            st.subheader(n["titulo"])
            st.caption(f"{n['fonte']} • {n['data']} • Tema: {n['tema']}")
            st.write(n["resumo"])
            st.markdown(f"[Ler a matéria completa]({n['link']})")
            st.markdown("---")
            contador = contador + 1


    st.write(f"Notícias exibidas: {contador}")


    st.subheader("Procure mais no g1")
    st.markdown("[Buscar 'mulheres ensino superior' no g1](https://g1.globo.com/busca/?q=mulheres+ensino+superior)")
    st.markdown("[Buscar 'Censo da Educação Superior' no g1](https://g1.globo.com/busca/?q=censo+educa%C3%A7%C3%A3o+superior)")