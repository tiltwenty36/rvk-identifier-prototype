import streamlit as st
from google import genai

# 1. Récupération sécurisée de la clé API (gérée par Streamlit)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("Clé API manquante. Veuillez configurer la clé GEMINI_API_KEY dans les paramètres Streamlit.")
    st.stop()

# 2. Simulation d'une base de données locale
BIBLIOTHEQUE_EXISTANTE = {
    "9782100814947": {"titre": "Introduction à la physique quantique", "rvk": "UK 1000"},
    "9782100824557": {"titre": "Algorithmique et structures de données", "rvk": "ST 130"},
    "design patterns": {"titre": "Design Patterns: Elements of Reusable Object-Oriented Software", "rvk": "ST 230"}
}

# 3. Interface Utilisateur
st.set_page_config(page_title="Classification RVK", page_icon="📚")
st.title("📚 Assistant Intelligent RVK")
st.write("Automatisez la classification de vos livres sans effort.")

# Barre latérale : Recherche
st.sidebar.header("🔍 Recherche Catalogue")
recherche = st.sidebar.text_input("Rechercher un livre existant :")

if recherche:
    cle_trouvee = next((k for k in BIBLIOTHEQUE_EXISTANTE if recherche.lower() in k.lower() or recherche in BIBLIOTHEQUE_EXISTANTE[k]["titre"].lower()), None)
    if cle_trouvee:
        livre = BIBLIOTHEQUE_EXISTANTE[cle_trouvee]
        st.sidebar.success(f"Trouvé !\n\n**Titre :** {livre['titre']}\n\n**Code RVK :** {livre['rvk']}")
    else:
        st.sidebar.warning("Livre non trouvé dans le catalogue.")

# Zone principale : IA
st.subheader("Classer un nouveau livre")
livre_input = st.text_input("Entrez le titre ou le sujet du livre :", placeholder="Ex: Manuel de droit civil")

if livre_input:
    with st.spinner("Analyse RVK en cours..."):
        try:
            prompt = f"""
            Tu es un système expert utilisant la Regensburger Verbundklassifikation (RVK).
            Analyse : "{livre_input}".
            Donne la notation RVK exacte sous ce format strict :
            - **Code RVK** : [Le code, ex: ST 250]
            - **Catégorie** : [Nom de la catégorie]
            - **Explication** : [Une phrase courte]
            """
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            st.success("Classification terminée !")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Erreur : {e}")
