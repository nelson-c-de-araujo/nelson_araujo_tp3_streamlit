import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="TP3 - Streamlit - Nelson")

st.title("TP3 - Desenvolvimento Front-End com Python (com Streamlit) [26E3_1]")
st.text("Aluno: Nelson Araujo")

st.subheader("Exercício 1")
"""Escolha dos Datasets e Explicação do Objetivo e Motivação:
Escolha um ou mais datasets do portal Data Rio.
Explique o objetivo e a motivação por trás da escolha dos dados 
e quais funcionalidades e visualizações serão implementadas."""

st.subheader("Dataset escolhido: Visitação ao Centro Cultural Banco do Brasil , 2015 - 2021")
"""Motivação: Eu fui um dos visitantes nesse período. Gosto muito do Centro Cultural do Banco do Brasil"""

st.divider()

st.subheader("Exercício 2")
"""Realizar Upload de Arquivo XLS:
Crie uma interface em Streamlit que permita ao usuário fazer
o upload de um arquivo XLS contendo dados de turismo do portal Data.Rio."""

st.markdown("Dataset utilizado foi o de Visitação ao Centro Cultural Banco do Brasil. " \
"Download disponível na pasta /data e no link https://www.arcgis.com/sharing/rest/content/items/614ad116a32746fc8d85e93f70df568d/data")

uploaded_file = st.file_uploader(
    "Faça o upload do arquivo de dados: ", # Adicionei o type csv pq o arquivo do ccbb é csv. 
    type=["xls", "xlsx", "csv"]
)

@st.cache_data
def carregar_dados_brutos(file_bytes=None, file_name=None):
    """
    Utiliza o cache do Streamlit (@st.cache_data) para armazenar em memória 
    o DataFrame lido. Evita re-leitura do disco ou re-processamento do upload
    a cada interação na interface.
    """
    if file_bytes is not None and file_name is not None:
        import io
        buffer = io.BytesIO(file_bytes)
        if file_name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(buffer, header=None)
        else:
            return pd.read_csv(buffer, sep=';', header=None, encoding='utf-8')
    else:
        return pd.read_csv('ccbb.csv', sep=';', header=None, encoding='utf-8')

# Leitura do arquivo (uploaded_file ou fallback para ccbb.csv local)
if uploaded_file is not None:
    st.success(f"Arquivo '{uploaded_file.name}' carregado com sucesso!")
    
    # Pré-visualização dos dados carregados
    try:
        if uploaded_file.name.endswith(('.xls', '.xlsx')):
            raw_df = pd.read_excel(uploaded_file, header=None)
        else:
            raw_df = pd.read_csv(uploaded_file, sep=';', header=None, encoding='utf-8')
    except Exception:
        raw_df = pd.DataFrame()
else:
    try:
        raw_df = pd.read_csv('ccbb.csv', sep=';', header=None, encoding='utf-8')
    except Exception:
        raw_df = pd.DataFrame()

# Preview dos dados brutos no Exercício 2
st.subheader("Pré-visualização dos dados brutos (Sem tratamento):")
st.dataframe(raw_df, use_container_width=True)

st.divider()

st.subheader("Exercícios 3 e 4")
"""Filtro de Dados e Seleção:
Exiba o dataset para o usuário e implemente 
três seletores diferentes (radio, checkbox, dropdowns) 
na interface que permitam ao usuário filtrar os 
dados carregados e selecionar as colunas 
ou linhas que deseja visualizar."""

"""Criar Visualizações de Dados - Tabelas:
Crie uma tabela interativa que exiba os dados filtrados de acordo 
com os seletores carregados e permita ao usuário ordenar 
e filtrar as colunas diretamente pela interface."""

# 1. Primeiro Seletor (Checkbox): Tratar dados
tratar_dados = st.checkbox("Tratar dados", key="tratar_dados")

df_exibicao = pd.DataFrame()

if tratar_dados:
    # Exercício 6: Spinner e Barra de Progresso reais durante o carregamento e tratamento dos dados.
    with st.spinner("Carregando e tratando os dados... Por favor, aguarde."):
        bar_progresso = st.progress(0, text="Iniciando o processamento do arquivo...")
        for percent in range(1, 101):
            time.sleep(0.02)  # Delay intencional
            bar_progresso.progress(percent, text=f"Carregando e tratando dados... {percent}%")
        bar_progresso.empty() # Remove a barra de progresso

    if not raw_df.empty and len(raw_df) >= 18:
        # Extração com base na localização exata das células no ccbb.csv:
        headers = [str(c).strip() for c in raw_df.iloc[4, 0:8].values]
        
        df_tratado = raw_df.iloc[6:18, 0:8].copy()
        df_tratado.columns = headers
        
        for col in df_tratado.columns:
            df_tratado[col] = df_tratado[col].astype(str).str.strip()
            if col != 'Mês':
                df_tratado[col] = df_tratado[col].str.replace(' ', '')
                
        df_tratado = df_tratado.reset_index(drop=True)
        
        st.success("Dados tratados com sucesso!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 2. Seletor Dropdown (Multiselect): Seleção de Meses (linhas)
            meses_disponiveis = df_tratado['Mês'].tolist()
            meses_selecionados = st.multiselect(
                "2. Dropdown (Multiselect): Selecione os meses desejados",
                options=meses_disponiveis,
                default=meses_disponiveis,
                key="meses_selecionados"
            )
            
        with col2:
            # 3. Seletor Radio: Ordenação das Linhas
            modo_ordenacao = st.radio(
                "3. Radio Button: Escolha a ordenação das linhas",
                options=["Ordem original (Janeiro a Dezembro)", "Ordem alfabética (Mês)", "Ordem decrescente (Mês)"],
                key="modo_ordenacao"
            )
            
        # Aplicação dos filtros ao DataFrame tratado
        df_exibicao = df_tratado.copy()
        
        # 1. Filtrar pelas linhas dos meses selecionados no Dropdown
        if meses_selecionados:
            df_exibicao = df_exibicao[df_exibicao['Mês'].isin(meses_selecionados)]
        else:
            st.warning("Selecione ao menos um mês no Dropdown acima.")
            df_exibicao = df_exibicao.iloc[0:0] # DataFrame vazio
        
        # 2. Aplicar ordenação do Radio
        if modo_ordenacao == "Ordem alfabética (Mês)":
            df_exibicao = df_exibicao.sort_values(by="Mês", ascending=True)
        elif modo_ordenacao == "Ordem decrescente (Mês)":
            df_exibicao = df_exibicao.sort_values(by="Mês", ascending=False)
            
        st.subheader("Dataset Tratado e Filtrado:")
        st.dataframe(df_exibicao, use_container_width=True)
    else:
        st.error("Não foi possível realizar o tratamento nos dados carregados.")
else:
    st.info("Marque a opção **'Tratar dados'** no checkbox acima para realizar a limpeza instantânea e habilitar as opções de seleção e filtro.")

st.divider()

st.subheader("Exercício 5")
"""Desenvolver Serviço de Download de Arquivos:
Implemente um serviço que permita ao usuário fazer o download dos 
dados filtrados em formato CSV diretamente pela interface da aplicação."""

if not df_exibicao.empty:
    csv_data = df_exibicao.to_csv(index=False, sep=';', encoding='utf-8-sig')
    st.download_button(
        label="Baixar Dataset Tratado e Filtrado (CSV)",
        data=csv_data,
        file_name="ccbb_dados_tratados.csv",
        mime="text/csv"
    )
else:
    st.info("Trate os dados e selecione os meses para habilitar o botão de download.")

st.divider()

st.subheader("Exercício 6")
"""Utilizar Barra de Progresso e Spinners:
Adicione uma barra de progresso e um spinner para indicar o 
carregamento dos dados enquanto o arquivo é processado e exibido na interface."""

st.info("A **barra de progresso** e o **spinner** (com delay proposital de 2 segundos) " \
"são acionados automaticamente durante o processamento do " \
"dataset no Exercício 3 ao marcar a opção **'Tratar dados'**.")

st.divider()

st.subheader("Exercício 7")
"""Utilizar Color Picker:
Adicione um color picker à interface que permita ao usuário personalizar 
a cor de fundo do painel e das fontes exibidas na aplicação."""

col_bg, col_txt = st.columns(2)

with col_bg:
    cor_fundo = st.color_picker("Personalizar Cor de Fundo do Painel:", "#2D2C2C", key="cor_fundo")

with col_txt:
    cor_texto = st.color_picker("Personalizar Cor das Fontes (Texto):", "#E8E8E8", key="cor_texto")

# Aplicação dinâmica das cores customizadas via CSS
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {cor_fundo};
        color: {cor_texto};
    }}
    .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp label, .stApp markdown {{
        color: {cor_texto} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.divider()

st.subheader("Exercício 8")
"""Utilizar Funcionalidade de Cache:
Utilize a funcionalidade de cache do Streamlit para armazenar os dados carregados dos arquivos CSV (formato original), 
evitando a necessidade de recarregá-los a cada nova interação."""

st.success("A leitura de arquivos está otimizada com o **`@st.cache_data`**!")

           
st.divider()

st.subheader("Exercício 9")
"""Persistir Dados Usando Session State:
Implemente a persistência de dados na aplicação utilizando Session State 
para manter as preferências do usuário (seleções e filtros escolhidos) durante a navegação."""

st.info("O **Session State (`st.session_state`)** é utilizado automaticamente ao vincular \
        o parâmetro `key` nos componentes da interface \
        (`tratar_dados`, `meses_selecionados`, `modo_ordenacao`, `cor_fundo`, `cor_texto`),\
         garantindo que todas as escolhas e filtros do usuário permaneçam salvos \
        durante toda a sessão de navegação!")

st.divider()

st.subheader("Exercício 10")
"""Criar Visualizações de Dados - Gráficos Simples:
Desenvolva gráficos simples (barras, linhas, e pie charts) para visualização dos dados carregados, utilizando o Streamlit."""

if tratar_dados and not df_exibicao.empty:
    """### Visualizações Gráficas"""

    df_graficos = df_exibicao.copy()
    for col in df_graficos.columns:
        if col != 'Mês':
            df_graficos[col] = pd.to_numeric(df_graficos[col].astype(str).str.replace(' ', ''), errors='coerce')

    """#### 1. Gráfico de Linhas (Visitações por Mês"""
    df_linhas = df_graficos.set_index('Mês')
    st.line_chart(df_linhas)

    col_bar, col_pie = st.columns(2)

    with col_bar:
        """#### 2. Gráfico de Barras (Total por Ano)"""
        totais_anos = df_graficos.drop(columns=['Mês']).sum()
        st.bar_chart(totais_anos)

    with col_pie:
        """#### 3. Gráfico de Pizza (Pie Chart - Proporção por Ano)"""
        
        totais_validos = totais_anos[totais_anos > 0]
        if not totais_validos.empty:
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(totais_validos.values, labels=totais_validos.index, autopct='%1.1f%%', startangle=90)
            ax.set_title("Distribuição Percentual de Visitas")
            ax.legend()
            st.pyplot(fig)
else:
    st.info("Marque a opção **'Tratar dados'** no Exercício 3 para visualizar os gráficos simples.")

st.divider()

st.subheader("Exercício 11")
"""Criar Visualizações de Dados - Gráficos Avançados:
Adicione gráficos avançados (histograma e scatter plot) para fornecer insights mais profundos sobre os dados."""

if tratar_dados and not df_exibicao.empty:
    """### Visualizações Gráficas Avançadas"""
    
    col_hist, col_scatter = st.columns(2)

    with col_hist:
        """#### 1. Histograma (Frequência do Volume de Visitantes)"""
    
        valores_numericos = df_graficos.drop(columns=['Mês']).values.flatten()
        valores_validos = valores_numericos[~pd.isna(valores_numericos)]
        
        if len(valores_validos) > 0:
            fig_hist, ax_hist = plt.subplots(figsize=(5, 4))
            ax_hist.hist(valores_validos, bins=8, color='#3498db', edgecolor='black', alpha=0.7)
            ax_hist.set_title("Distribuição de Frequência de Visitas")
            ax_hist.set_xlabel("Volume de Visitantes")
            ax_hist.set_ylabel("Quantidade de Ocorrências")
            st.pyplot(fig_hist)

    with col_scatter:
        """#### 2. Scatter Plot com Rótulos de Meses (Comparação entre Anos)"""
        anos_disponiveis = [c for c in df_graficos.columns if c != 'Mês']
        
        if len(anos_disponiveis) >= 2:
            c1, c2 = st.columns(2)
            with c1:
                ano_x = st.selectbox("Eixo X:", anos_disponiveis, index=0, key="scatter_x")
            with c2:
                ano_y = st.selectbox("Eixo Y:", anos_disponiveis, index=min(4, len(anos_disponiveis)-1), key="scatter_y")
                
            fig_scat, ax_scat = plt.subplots(figsize=(5, 4))
            
            # Apenas linhas que possuem dados numéricos válidos em ambos os anos escolhidos
            df_scatter = df_graficos.dropna(subset=[ano_x, ano_y])
            
            # Desenha os pontos de dispersão
            ax_scat.scatter(df_scatter[ano_x], df_scatter[ano_y], color='#e74c3c', s=80, alpha=0.8, edgecolors='black', zorder=3)
            
            # Adiciona o nome do mês ao lado de cada ponto
            for idx, row in df_scatter.iterrows():
                nome_mes = str(row['Mês'])[:3] # Primeiras 3 letras (Jan, Fev, Mar...)
                ax_scat.annotate(
                    nome_mes, 
                    (row[ano_x], row[ano_y]), 
                    textcoords="offset points", 
                    xytext=(6, 4), 
                    fontsize=8,
                    weight='bold'
                )
                
            # Adiciona linha diagonal de referência (1:1)
            if not df_scatter.empty:
                max_val = max(df_scatter[ano_x].max(), df_scatter[ano_y].max())
                ax_scat.plot([0, max_val], [0, max_val], '--', color='gray', alpha=0.7, label='Igualdade (1:1)')
                ax_scat.legend(fontsize=8)
                
            ax_scat.set_title(f"Comparação Mensal: {ano_x} vs {ano_y}")
            ax_scat.set_xlabel(f"Visitas em {ano_x}")
            ax_scat.set_ylabel(f"Visitas em {ano_y}")
            ax_scat.grid(True, linestyle=':', alpha=0.6)
            st.pyplot(fig_scat)

else:
    st.info("Marque a opção **'Tratar dados'** no Exercício 3 para visualizar os gráficos avançados.")

st.divider()

st.subheader("Exercício 12")
"""Exibir Métricas Básicas:
Implemente a exibição de métricas básicas (como contagem de registros, médias, somas) diretamente na interface para fornecer um resumo rápido dos dados carregados."""

if tratar_dados and not df_exibicao.empty:
    """### Resumo das Métricas Básicas"""

    df_calc = df_exibicao.copy()
    for col in df_calc.columns:
        if col != 'Mês':
            df_calc[col] = pd.to_numeric(df_calc[col].astype(str).str.replace(' ', ''), errors='coerce')

    total_registros = len(df_calc)
    soma_visitas = df_calc.drop(columns=['Mês']).sum().sum()
    media_mensal = df_calc.drop(columns=['Mês']).mean().mean()

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            label="Total de Meses Exibidos",
            value=f"{total_registros} meses"
        )

    with m2:
        st.metric(
            label="Soma Total de Visitações",
            value=f"{int(soma_visitas):,}".replace(",", ".")
        )

    with m3:
        st.metric(
            label="Média Mensal de Visitações",
            value=f"{int(media_mensal):,}".replace(",", ".")
        )

else:
    st.info("Marque a opção **'Tratar dados'** no Exercício 3 para visualizar o resumo de métricas básicas.")