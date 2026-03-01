import streamlit as st
import requests
import openai
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="LinkedIn Ecosystem Optimizer | Crawla Colab",
    page_icon="🔎",
    layout="wide"
)

# --- ESTILOS Y BRANDING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #0077b5; color: white; border-radius: 5px; }
    .footer { text-align: center; margin-top: 50px; color: #666; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- DICCIONARIOS DE CONFIGURACIÓN ---
PAISES = {
    "Global": "gl", "España": "es", "México": "mx", "Colombia": "co", 
    "Argentina": "ar", "Chile": "cl", "Perú": "pe", "EE.UU (Español)": "us",
    "Ecuador": "ec", "Panamá": "pa", "Uruguay": "uy"
}

IDIOMAS = {
    "Español": "es",
    "Inglés": "en",
    "Portugués": "pt"
}

# --- FUNCIONES CORE ---

def get_serp_data(query, country_code, lang_code, api_key):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": f'site:linkedin.com/in "{query}"',
        "gl": country_code,
        "hl": lang_code,
        "num": 7
    })
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json().get('organic', [])
    except:
        return []

def get_ai_recommendations(query, profiles, lang, api_key):
    client = openai.OpenAI(api_key=api_key)
    context = "\n".join([f"- {p.get('title')}: {p.get('snippet')}" for p in profiles])
    
    prompt = f"""
    Eres un experto en SEO de LinkedIn. Idioma de respuesta: {lang}.
    Analiza estos resultados de Google para la búsqueda '{query}':
    {context}
    
    Proporciona:
    1. 10 Keywords de alto impacto para el perfil.
    2. 3 Titulares (Headlines) optimizados.
    Responde estrictamente en formato JSON con llaves 'keywords' (lista) y 'titulares' (lista).
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

# --- INTERFAZ ---

# Header con Branding
st.image("https://colab.crawla.agency/wp-content/uploads/2023/10/Logo-Crawla-Colab.png", width=200) # Ajustar URL si es necesario
st.title("LinkedIn Ecosystem Optimizer")
st.info("Esta es una herramienta exclusiva de **[Crawla Colab](https://colab.crawla.agency)** para el posicionamiento integral en el ecosistema digital.")

# Sidebar de Configuración
with st.sidebar:
    st.header("📍 Segmentación")
    selected_country = st.selectbox("País de búsqueda", list(PAISES.keys()))
    selected_lang = st.selectbox("Idioma de los resultados", list(IDIOMAS.keys()))
    
    st.divider()
    st.markdown("### 📚 Recursos del Curso")
    # REEMPLAZA ESTE LINK CON TU LINK REAL
    st.link_button("Acceder al Workbook de LinkedIn", "https://tu-link-al-workbook.com", use_container_width=True)
    st.caption("Usa el workbook para documentar los hallazgos de esta herramienta.")

# Cuerpo Principal
role = st.text_input("Ingresa el cargo o nicho a analizar:", placeholder="Ej: Especialista en Ciberseguridad")

if st.button("Analizar Ecosistema Digital"):
    # Obtener llaves desde Secrets de Streamlit
    try:
        OPENAI_API = st.secrets["OPENAI_API_KEY"]
        SERPER_API = st.secrets["SERPER_API_KEY"]
    except:
        st.error("Error: Las API Keys no están configuradas en los Secrets de Streamlit.")
        st.stop()

    if role:
        with st.spinner(f"Analizando perfiles en {selected_country}..."):
            # 1. Búsqueda Geocalizada
            results = get_serp_data(role, PAISES[selected_country], IDIOMAS[selected_lang], SERPER_API)
            
            if results:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader(f"🔝 Líderes en {selected_country}")
                    for r in results:
                        with st.expander(r['title'][:60]):
                            st.write(r.get('snippet'))
                            st.link_button("Ver Perfil", r['link'])
                
                with col2:
                    # 2. Análisis IA
                    analysis = get_ai_recommendations(role, results, selected_lang, OPENAI_API)
                    st.subheader("💡 Estrategia de Optimización")
                    
                    st.markdown("**Keywords Recomendadas:**")
                    st.info(", ".join(analysis['keywords']))
                    
                    st.markdown("**Sugerencias de Headline:**")
                    for t in analysis['titulares']:
                        st.code(t, language=None)
            else:
                st.warning("No se encontraron resultados específicos para esa combinación. Intenta ampliar la búsqueda.")
    else:
        st.warning("Por favor ingresa un cargo.")

# Footer
st.markdown("""
    <div class="footer">
    Herramienta desarrollada por Crawla Colab © 2026<br>
    <a href="https://colab.crawla.agency">Visitar Crawla Colab</a>
    </div>
    """, unsafe_allow_html=True)
