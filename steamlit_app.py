import streamlit as st
import requests
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px 


import io
from azure.storage.blob import BlobServiceClient



st.set_page_config(
    page_title="Tableau de bord Projet 9",
    page_icon="🧊",
    layout="wide"
)


@st.cache_data(persist=True)
def load_file():
    source = 'https://iaprojet9.blob.core.windows.net/datap09-2/training.1600000.processed.noemoticon.csv?sp=racwdyt&st=2024-10-16T16:07:39Z&se=2024-11-08T01:07:39Z&spr=https&sv=2022-11-02&sr=b&sig=ytlI1KJUF65RcN4vMnDsF7QE6eLqJBbcuzZQ5rxPmao%3D'
    col = ["sentiment", "ids", "date", "flag", "user", "text"]
    data = pd.read_csv(source,encoding='latin1',names=col)
    data['sentiment'] = data['sentiment'].map({0: 'negative', 4: 'positive'})
    return data


data = load_file()
data_sample = data.sample(50)


st.markdown("<h1 style='color: #7350EA;'>Tableau de bord Projet 9 :\n Analyse de sentiments avec le Deep learning</h1>", unsafe_allow_html=True)

st.write('### Aperçu des données')       
st.dataframe(data_sample,use_container_width= True)


# définir la disposition des graphiques
col1,col2,col3 = st.columns([.5,.25,.25],gap='medium',
                        vertical_alignment= "bottom")

#WordCloud
with col1:
    col1.subheader('Nuage de Mots')
    text_cloud = " ".join(data_sample['text'])
    wordcloud = WordCloud(width=800, height=400, background_color='white',colormap = 'Set2').generate(text_cloud)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

# Histogram
with col2:
    col2.subheader('Distribution de la Longueur des Phrases')
    data['txt_length'] = data['text'].apply(len)
    fig1 = px.histogram(data, x='txt_length', nbins=10, 
    labels={'txt_length': 'Nombre de caractères'},
    color_discrete_sequence=['#7350EA'])
    fig1.update_xaxes(
        tickfont = dict(size=15 ,color = 'black'),
        title_font = dict(size=15 ,color = 'black')
        )
    fig1.update_yaxes(
        tickfont = dict(size=15 ,color = 'black'),
        title_font = dict(size=15 ,color = 'black')
        )    
    st.write(fig1)

# Histogram
with col3:
    col3.subheader('Distribution des classes')
    fig2 = px.histogram(
            data_frame=data, x="sentiment",
            color_discrete_sequence=['#7350EA'])
    fig2.update_xaxes(
        tickfont = dict(size=15 ,color = 'black'),
        title_font = dict(size=15 ,color = 'black')
        )
    fig2.update_yaxes(
        tickfont = dict(size=15 ,color = 'black'),
        title_font = dict(size=15 ,color = 'black')
    )
    st.write(fig2)


# URL API Azure
API_URL = "https://apip09.azurewebsites.net/predict"
API_INTERPRET = "https://apip09.azurewebsites.net/interpret"

# Fonction pour analyser le sentiment
st.write('### Test du modèle')

user_input = st.text_input("Saisissez une phrase en anglais:")

def analyze_sentiment():
    if user_input:
        response = requests.post(f"{API_URL}", json={"text": user_input})
        if response.status_code == 200:
            result = response.json()

    st.session_state.sentiment= result['sentiment']        
    st.write(f"**Résultat de l'analyse :** {st.session_state.sentiment}")       

# Afficher le sentiment si déjà calculé
# if 'sentiment' in st.session_state:
#     st.write(f"**Résultat de l'analyse :** {st.session_state.sentiment}")


# Bouton pour analyser
if st.button("Analyser"):
    analyze_sentiment()

if st.button("Interpretation"):
    response = requests.post(f"{API_INTERPRET}", json={"text": user_input})
    result = response.json()
    df  = pd.DataFrame(result.get('interpretation'))
    st.session_state.interpretation = result['interpretation']

    # Affiche l'interpretation

    st.write("")

    st.markdown(
        """
        <div style="background-color: #E6F4FA; padding: 10px; border-radius: 5px;">
            <h3 style="color: #262730;">Analyse de l'interprétation</h3>
            <p style="color: #262730;">Les mots avec des valeurs positives élevées sont les plus influents dans le résultat de l'analyse.<br> A l'opposé, les mots avec des valeurs négatives vont à l'encontre de la prédiction.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    fig2 = px.bar(
    data_frame= df, x="contribution", y="word",
    color_discrete_sequence=['#7350EA'])
    st.write(fig2)
