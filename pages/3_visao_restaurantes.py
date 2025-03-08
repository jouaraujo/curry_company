# bibliotecas
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import folium
import datetime
import numpy as np

from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

# -------------------------------
# Funções
# -------------------------------

def clean_code(df1):
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

def distance(df1, fig):
    if fig == False:
        # 2. a distância média dos restaurantes e dos locais de entrega.
        # SAPE
        # SA -> um valor (distância média) -> [10km, 20km, ..., 40km] -> média -> valor
        # P -> calcular a distancia entre os pedidos entregues e os restaurantes -> [10km, 5km,..., 40km]
        # E -> colunas de latitude e longitude tanto dos pedidos (fim) quanto dos restaurantes (inicio) -> comando que calcula distância
        cols = ['Delivery_location_latitude', 'Restaurant_latitude', 'Delivery_location_longitude', 'Restaurant_longitude']
        df1['distance'] = df1[cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
                                                            axis=1)
        avg_distance = np.round(df1['distance'].mean(), 2)

        return avg_distance

    else:
        cols = ['Delivery_location_latitude', 'Restaurant_latitude', 'Delivery_location_longitude', 'Restaurant_longitude']
        df1['distance'] = df1[cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
                                                            axis=1)
        avg_distance = df1[['City', 'distance']].groupby('City').mean().reset_index()

        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])

        return fig

def avg_std_time_delivery(df1,festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                - op: Tipo de operação que precisa ser calculado
                    'mean': Calcula o tempo médio
                    'std': Calcula o desvio padrão do tempo.
            Output:
                - df: Dataframe
    """
    # o tempo médio/desvio de entrega durante os festivais.
    df_aux = df1[['Festival', 'Time_taken(min)']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)
    
    return df_aux

def avg_std_time_graph(df1):
    # o tempo médio e o desvio padrão de entrega por cidade.
    df_aux = df1[['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                        x=df_aux['City'],
                        y=df_aux['avg_time'],
                        error_y=dict(type='data', array=df_aux['std_time'])))                
    fig.update_layout(barmode='group')

    return fig

def avg_std_time_on_traffic(df1):
    df_aux = (df1[['City', 'Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density'])
                                                                    .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'],
                    values='avg_time', color='std_time', color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df_aux['std_time']))                
    return fig

# ---------------------------------------------------------
# importando dados
# ---------------------------------------------------------
df = pd.read_csv('data/train.csv')

# cleaning code
df1 = clean_code(df)

##################################################################################################
# Barra Lateral
##################################################################################################

st.header('Marketplace - Visão Restaurantes')


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
# Layout no Streamlit
##################################################################################################

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            # quantidade de entregadores únicos
            delivery_unique = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores únicos', delivery_unique)
        
        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('Distância média das entregas', avg_distance)
        
        with col3:
            df_aux = avg_std_time_delivery(df1,'Yes', 'avg_time')
            col3.metric('Tempo Médio de entrega c/ Festival', df_aux)
        
        with col4:
            df_aux = avg_std_time_delivery(df1,'Yes', 'std_time')
            col4.metric('Desvio Padrão de entrega c/ Festival', df_aux)
        
        with col5:
            # o tempo médio de entrega sem os festivais.
            df_aux = avg_std_time_delivery(df1,'No', 'avg_time')
            col5.metric('Tempo Médio de entrega s/ Festival', df_aux)
        
        with col6:
            # o desvio padrão de entrega durante os festivais.
            df_aux = avg_std_time_delivery(df1,'No', 'std_time')
            col6.metric('Desvio Padrão de entrega s/ Festival', df_aux)
        

    with st.container():
        st.markdown("""---""")
        
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Tempo Médio de entrega por cidade')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)

        with col2:
            st.markdown('##### Distribuição da Distância')
            # o tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.

            df_aux = (df1[['City', 'Type_of_order', 'Time_taken(min)']].groupby(['City', 'Type_of_order'])
                                                                   .agg({'Time_taken(min)': ['mean', 'std']})
                                                                   .reset_index())
        
            st.dataframe(df_aux)

    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do tempo')
        col1, col2 = st.columns(2)

        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig)

        with col2:            
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)

