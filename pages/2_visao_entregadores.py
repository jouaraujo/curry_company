# bibliotecas
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import folium
import datetime

from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🛵', layout='wide')

# -------------------------------
# Funções
# -------------------------------

def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe 
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas 
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    """
    # 1. convertendo a coluna age de texto para numero
    df1 = df1[df1['Delivery_person_Age'] != 'NaN ']

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1 = df1[df1['Road_traffic_density'] != 'NaN ']

    df1 = df1[df1['City'] != 'NaN ']

    df1 = df1[df1['Festival'] != 'NaN ']

    # 2. convertendo a coluna ratings de texto para numero decilam float

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 3. convertendo a coluna order_date de texto para data

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 4. convertendo multiple_deliveries de texto para numero inteiro int
    df1 = df1[df1['multiple_deliveries'] != 'NaN ']

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 5. removendo os espacos dentro das strings
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 6. limpando a coluna de time taken 
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1]).astype(int)

    return df1

def top_delivers(df1, top_asc):
    # os 10 entregadores mais rápidos/lentos por cidade.
    df2 = (df1[['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['Delivery_person_ID', 'City'])
                                                                .max()
                                                                .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
                                                                .reset_index())
    df_aux1 = df2[df2['City'] == 'Metropolitian'].head(10)
    df_aux2 = df2[df2['City'] == 'Urban'].head(10)
    df_aux3 = df2[df2['City'] == 'Semi-Urban'].head(10)
    df3 = pd.concat([df_aux1,
                    df_aux2,
                    df_aux3]).reset_index().drop('index', axis=1)
    return df3


# importando dados
df = pd.read_csv('data/train.csv')

# cleaning dataset
df1 = clean_code(df)

##################################################################################################
# Barra Lateral
##################################################################################################

st.header('Marketplace - Visão Entregadores')


#image_path = 'C:/Users/jonat/OneDrive/Documentos/repos/dashboards/'
image = Image.open('cury.png')

st.sidebar.image(image, width=350)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
                  'Até qual valor?',
                   value=datetime.datetime(2022, 4, 13),
                   min_value=datetime.datetime(2022, 2, 11),
                   max_value=datetime.datetime(2022, 6, 4),
                   format='DD-MM-YYYY'
)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
                      'Quais as condições do trânsito',
                      ['Low', 'Medium', 'High', 'Jam'],
                      default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""---""")

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

##################################################################################################
# Layout Streamlit
##################################################################################################

tab1, tab2, tab3 =st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            # maior idade dos entregadores
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)

        with col2:
            # menor idade dos entregadores
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)

        with col3:
            # melhor condição dos veículos
            melhor_condicao = df1['Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)

        with col4:
            # pior condição dos veículos
            pior_condicao = df1['Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)
        
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Avaliação média por entregador')
            # a avaliação média por entregador.

            df_avg_ratings_per_deliver = (df1[['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID')
                                                                                                .mean().reset_index())

            st.dataframe(df_avg_ratings_per_deliver)

        with col2:
            st.markdown('##### Avalição média por trânsito')
            # a avaliação média e o desvio padrão por tipo de tráfego.
            df_avg_std_by_traffic = (df1[['Road_traffic_density', 'Delivery_person_Ratings']].groupby('Road_traffic_density')
                                                                                 .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            df_avg_std_by_traffic.columns = ['delivery_mean', 'delivery_std']

            df_avg_std_by_traffic = df_avg_std_by_traffic.reset_index()

            st.dataframe(df_avg_std_by_traffic)

            st.markdown('##### Avaliação média por clima')
            # a avaliação média e o desvio padrão por condições climáticas.
            df_avg_std_by_Weatherconditions = (df1[['Weatherconditions', 'Delivery_person_Ratings']].groupby('Weatherconditions')
                                                                                        .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            df_avg_std_by_Weatherconditions.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_by_Weatherconditions = df_avg_std_by_Weatherconditions.reset_index()
            
            st.dataframe(df_avg_std_by_Weatherconditions)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)

        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)

