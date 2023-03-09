import streamlit as st
from PIL import Image

st.set_page_config(
    page_title= 'Home')

image_path = 'Images/ifood.png'
image = Image.open(image_path)
st.sidebar.image(image, width = 120)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown('*Fast Delivery in town*')

st.write("""
         Growth Dashboard foi construido para acompanhar 
         as métricas de crescimento dos entregadores e restaurantes.
         
         ### Como utilizar esse grouth dashboard?
         
         - #### Visão Empresa
            - Visão Gerencial: Métricas gerenciais de comportamento
            - Visão tática: Indicadores semanais de crescimento
            - Visão Geográfica: Insights de geolocalização
        - #### Visão Entregadores
            - Acompanhamento dos indicadores semanais de crescimento
        - #### Visão Restaurante
            - Indicadores semanais de crescimento dos restaurantes
        
        ### Ask for Help
        - ##### Email: ramos.matheus@engenharia.ufjf.br
        - ##### LinkedIn: https://www.linkedin.com/in/oliveiramatheuss/
        
         """)
