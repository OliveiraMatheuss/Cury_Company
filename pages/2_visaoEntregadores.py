#Importações ========================================================================================

import pandas as pd
import pandas as pd   
import plotly.express as px
import plotly.graph_objects as go
import folium
import numpy as np
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title= 'Visão Entregadores',
                   layout= 'wide')
#================================================================================================#
#=========================================== Funções ============================================#
#================================================================================================#

def rank (df2, city, ascending):
    df2 = (df2[df2['City']== city]
        .sort_values(by = 'Time_taken(min)', ascending= ascending)
        .head(10))
    return df2



# dados ==============================================================================================
df = pd.read_csv('datasets/train.csv')
#print(df.head())

#Limpeza de dos Dados
df1 = df.copy()
#1. Limpando os espaços
df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()

#2. Removendo os 'NaN ' do dataset
#Limpeza de dos Dados
df1 = df.copy()
#1. Limpando os espaços
df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()

#2. Removendo os 'NaN ' do dataset
linhas_selecionadas = (
      (df1['Delivery_person_Age'] != 'NaN ') &
      (df1['multiple_deliveries'] != 'NaN ') &
      (df1['Road_traffic_density'] != 'NaN') &
      (df1['City'] != 'NaN') &
      (df1['Festival'] != 'NaN ')
      )
df1 = df1.loc[linhas_selecionadas,:].copy()

# 1. Convertendo as Variaveis
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

#2. Convertendo a variavel Ratings em Float
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

#3. Convertendo a coluna order_date de texto para data

df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

#4. Conertendo 'multiple_delivery' para int
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

#5. Limpando coluna do time_taker
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.replace('(min)', '')).astype(int)





#=======================================================================================
#                               Sidebar                                                #
#=======================================================================================

st.header('Marketplace - Visão dos Entregadores')

image_path = 'Images/ifood.png'
image = Image.open(image_path)
st.sidebar.image(image, width = 120)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown('*Fast Delivery in town*')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
data_slider = st.sidebar.slider('Até qual valor?',
                        value = pd.datetime(2022,4,13),
                        min_value= pd.datetime(2022,2,11),
                        max_value= pd.datetime(2022,4,16),
                        format = 'DD-MM-YYYY')
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições de transito?',
                       ['Low','Medium','High', 'Jam'],
                       default=['Low'])
st.sidebar.markdown("""---""")

st.sidebar.markdown('*Powered Matheus R. de Oliveira*')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] <  data_slider
df1 = df1.loc[linhas_selecionadas,:]

#Filtro de trafego
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]


#=======================================================================================
#                               LAYOUT STREAMLIT                                       #
#=======================================================================================

with st.container():
    st.header('Info Gerais')
    st.markdown("""---""")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # A Maior idade entre os entregadores
        maior_idade = df1.Delivery_person_Age.max()
        col1.metric(label= 'Maior Idade', value = maior_idade)

        
    with col2:
        # A menor idade entre os entregadores
        menor_idade = df1.Delivery_person_Age.min()
        delta = (menor_idade - maior_idade)
        col2.metric(label = 'Menor idade', value = menor_idade)
        
    with col3:
        melhor_condition = df1.Vehicle_condition.max()
        col3.metric(label = 'Melhores Condições', value = melhor_condition)

    with col4:
        pior_condition = df1.Vehicle_condition.min()
        col4.metric(label = 'Pior Condição', value = pior_condition)
st.markdown("""---""")
with st.container():
    col5, col6 = st.columns(2)
    with col5:
        with st.container():
            st.markdown("##### Avaliação Média por entregador")
            df_media_entregador = (df1.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']]
                                   .groupby('Delivery_person_ID')
                                   .mean()
                                   .reset_index())
            st.dataframe(data = df_media_entregador,height=490,  use_container_width= True)
    with col6:
        with st.container():
            st.markdown("##### Avaliação média por tipo de tráfego")
            mean_avg_Ratings_traffic = (df1
                                        .loc[:,['Road_traffic_density','Delivery_person_Ratings']]
                                        .groupby('Road_traffic_density')
                                        .agg({'Delivery_person_Ratings': ['mean','std']}))
            mean_avg_Ratings_traffic.columns = ['mean_ratings', 'avg_ratings']
            mean_avg_Ratings_traffic.reset_index()
            st.dataframe(data = mean_avg_Ratings_traffic)
        
        with st.container():
            st.markdown("##### A avaliação média por clima")
            mean_avg_weatherconditions = (df1.loc[:,['Weatherconditions','Delivery_person_Ratings']]
                                          .groupby('Weatherconditions')
                                          .agg({'Delivery_person_Ratings':['mean','std']}))
            
            mean_avg_weatherconditions.columns = ['mean_ratings','avg_ratings']
            mean_avg_weatherconditions.reset_index()
            st.dataframe(data = mean_avg_weatherconditions)
st.markdown("""---""")
with st.container():

        st.markdown("##### top 10 mais rápidos por cidade")
        df2 = df1.loc[:,['City', 'Delivery_person_ID','Time_taken(min)']].copy()
        
        df2_Metropilitian = rank(df2, city = 'Metropolitian', ascending= True)
        df2_Semi_Urban = rank(df2, city = 'Semi-Urban', ascending=True)
        df2_Urban = rank(df2, city = 'Urban', ascending= True)
        
        df_flash = pd.concat([df2_Metropilitian,df2_Urban,df2_Semi_Urban])
        st.dataframe(data = df_flash, use_container_width= True)
#======================================================================================================

        st.markdown("##### top 10 mais lentos por cidade")
        df2 = df1.loc[:,['City', 'Delivery_person_ID','Time_taken(min)']].copy()
        
        df2_Metropilitian = rank(df2, city = 'Metropolitian', ascending= False)
        df2_Semi_Urban = rank(df2, city = 'Semi-Urban', ascending=False)
        df2_Urban = rank(df2, city = 'Urban', ascending= False)

        df_tartarugas = pd.concat([df2_Metropilitian,df2_Urban,df2_Semi_Urban])
        st.dataframe(data = df_tartarugas, use_container_width= True)
