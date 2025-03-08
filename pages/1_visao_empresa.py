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

st.set_page_config(page_title='Visão Negócio', page_icon='📈', layout='wide')

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

def order_metric(df1):
    # colunas
    cols = ['ID', 'Order_Date']
    # selecao de linhas
    df_aux = df1[cols].groupby('Order_Date').count().reset_index()
    # desenhar o gráfico de linhas
    # Plotly
    fig = px.bar(df_aux, x='Order_Date',
                y='ID')            
    return fig

def traffic_order_share(df1):
    df1 = df1[df1['Road_traffic_density'] != 'NaN']
    df_aux = df1[['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values='entregas_perc',
                names='Road_traffic_density')   
                 
    return fig

def traffic_order_city(df1):
    df1 = df1[df1['City'] != 'NaN']
    df_aux = df1[['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City',
                    y='Road_traffic_density',
                    size='ID',
                    color='City')
    
    return fig

def  order_by_week(df1):
    # criar a coluna de semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1[['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year',
                y='ID')            
    return fig

def order_share_by_week(df1):
    # quantidade de pedidos por semana / número único de entregadores por semana
    df_aux1 = df1[['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2 = df1[['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, 
            how='inner')
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year',
                y='order_by_delivery')
    
    return fig

def country_maps(df1):
    df_aux = df1[['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density'])\
                                                                                                        .median().reset_index()
    map = folium.Map()
    for i in range(len(df_aux)):
            folium.Marker([df_aux.loc[i,'Delivery_location_latitude'], df_aux.loc[i,'Delivery_location_longitude']],
            popup=df_aux.loc[i, ['City', 'Road_traffic_density']]).add_to(map)
    #for index, location_info in df_aux.iterrows():
    #    folium.Marker([location_info['Delivery_location_latitude'], 
    #                  location_info['Delivery_location_longitude']]).add_to(map)        
    folium_static(map, width=1024, height=600)

# ---------------------------- Início da estrutura lógica do código ----------------------
# -------------------------------
# importando dados
# -------------------------------
df = pd.read_csv('data/train.csv')

# -------------------------------
# Limpando dados
# -------------------------------
df1 = clean_code(df)


##################################################################################################
# Barra Lateral
##################################################################################################

st.header('Marketplace - Visão Cliente')


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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = traffic_order_city(df1)
            st.header('Traffic Order City')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)