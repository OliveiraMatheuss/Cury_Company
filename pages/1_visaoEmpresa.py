#===================================================================================================#
#=================================== Importações ===================================================#
#===================================================================================================#
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

st.set_page_config(page_title= 'Visão Empresa',
                   layout= 'wide')

#===================================================================================================#
#==================================== Funções ======================================================#
#===================================================================================================#

def clean_code(df1):
      
      """ 
      Essa função faz toda a limpeza e transformação dos dados
      
      Tipos de Limpeza e transformações:
      1. Limpa os espaços presentes nas colunas
      2. Remove os 'Nan ' 
      3. Converte variaveis object para int ou float
      4. Remove string da coluna Taken_time(min)
      """

      #Limpeza de dos Dados
      #1. Limpando os espaços
      df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
      df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
      df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
      df1.loc[:, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
      df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
      df1.loc[:, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()

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
      
      return df1
def quant_ped_dia(df1):
                  df_aux = df1.loc[:,['ID','Order_Date']].groupby('Order_Date').count().reset_index()
                  fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
                  return fig
def quant_ped_seman(df1):
      df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
      df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
      fig = px.line(df_aux, x = 'week_of_year', y = 'ID' )
      return fig
def dist_ped_traff(df1):
      df_aux = df1.loc[:, ['ID','City', 'Type_of_vehicle']].groupby(['Type_of_vehicle','City']).count().reset_index()
      fig = px.scatter(data_frame= df_aux, x = 'City', y = 'Type_of_vehicle', size= 'ID', color= 'City')
      return fig
def med_semana(df1):
      df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
      df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
      fig = px.line(df_aux, x = 'week_of_year', y = 'ID' )
      return fig
def chart(df1):   
      cols = ['Delivery_person_ID', 'ID']
      df_aux = df1.loc[:,cols].groupby('Delivery_person_ID').count().sort_values(by = 'ID', ascending= False).head(30).reset_index()
      fig = px.bar(df_aux, x = 'Delivery_person_ID', y = 'ID')
      return fig
def mapMaker(df1):
      df_aux = df1.loc[ :, ['City','Road_traffic_density', 'Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
      map = folium.Map()
      for intex, location_info in df_aux.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude']] ).add_to(map)
            folium_static(map, width = 800, height=600)


#=================================================================================================#
#===================================== Chamada das Funções =======================================#
#=================================================================================================#

#Carga de Dados

df = pd.read_csv('datasests/train.csv')
df1 = clean_code(df)

#=======================================================================================
#                               Sidebar                                                #
#=======================================================================================

st.header('Marketplace - Visão da Empresa')

image_path = 'images/ifood.png'
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


tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
      with st.container():
            # Gráfico Quantidade de Pedidos por dia
            fig = quant_ped_dia(df1)
            st.plotly_chart(fig, use_container_width= True)
            st.markdown("""---""")
            col1, col2 = st.columns(2)
            
      with st.container():
            # Quantidade de pedidos por semana
            with col1:
                  fig = quant_ped_seman(df1)
                  st.plotly_chart(fig, use_container_width= True, )
            
            # Distribuição dos pedidos por tipo de tráfego.
      
            with col2:
                  fig = dist_ped_traff(df1)
                  st.plotly_chart(fig, use_container_width= True)
      
with tab2:
      with st.container():
            fig = med_semana(df1)
            st.plotly_chart(fig, use_container_width=True)
      st.markdown("""---""")
      
      with st.container():
            fig = chart(df1)
            st.plotly_chart(fig, use_container_width=True)

            
      
with tab3:
      st.header('Country Map')
      mapMaker(df1)
      

