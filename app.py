import streamlit as st
import requests
import openai
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="LinkedIn Ecosystem Optimizer | Crawla Colab",
    page_icon="🚀",
    layout="wide"
)

# --- ESTILOS Y BRANDING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #0077b5; color: white; border-radius: 5px; font-weight: bold; }
    .stAlert { border-radius: 10px; }
    .footer { text-align: center; margin-top: 50px; color: #666; font-size: 0.8em; border-top: 1px solid #ddd; padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE DATOS ---
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
    
    # Prompt ajustado para evitar sesgos y promover lenguaje inclusivo
    prompt = f"""
    Eres un experto en Personal Branding y SEO de LinkedIn con un enfoque de diversidad e inclusión.
    Idioma de respuesta: {lang}.
    
    TAREA:
    Analiza estos resultados de búsqueda para '{query}':
    {context}
    
    REQUISITOS DE INCLUSIÓN:
    - Evita términos que refuercen sesgos de género (ej. preferir 'Liderazgo de equipos' sobre 'Jefe de equipo', o usar términos neutrales).
    - Asegúrate de que las keywords y titulares no asuman un género masculino por defecto.
    - Proporciona opciones que funcionen para cualquier identidad de género.

    ENTREGABLES:
    1. 12 Keywords de alto impacto (mezcla de Hard Skills y conceptos de liderazgo inclusivo).
    2. 3 Titulares (Headlines) que sean profesionales, magnéticos y neutrales.
    
    Responde estrictamente en formato JSON con llaves 'keywords' (lista) y 'titulares' (lista).
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

# --- INTERFAZ ---

# Header con Branding de Crawla Colab
st.image("https://colab.crawla.agency/wp-content/uploads/2023/10/Logo-Crawla-Colab.png", width=180) 
st.title("LinkedIn Ecosystem Optimizer")
st.markdown("### Optimización integral para el mercado digital actual")

# Sidebar
with st.sidebar:
    st.header("📍 Personalización")
    selected_country = st.selectbox("País objetivo", list(PAISES.keys()))
    selected_lang = st.selectbox("Idioma principal", list(IDIOMAS.keys()))
    
    st.divider()
    st.header("🛠️ Herramientas Crawla")
    
    # Enlaces a recursos
    st.markdown("#### 📘 Material del Curso")
    st.link_button("Descargar Workbook LinkedIn", "https://tu-link-al-workbook.com", use_container_width=True)
    
    st.markdown("#### 🤖 Asistente IA Personalizado")
    st.link_button("Ir al GEM de Optimización", "https://gemini.google.com/gems/tu-link-al-gem", use_container_width=True)
    
    st.divider()
    st.caption("Esta herramienta es parte del ecosistema de formación de [Crawla Colab](https://colab.crawla.agency).")

# Sección de Input
role = st.text_input("¿Qué cargo o rol deseas analizar?", placeholder="Ej: Dirección de Proyectos, Desarrollo de Software...")

if st.button("🚀 Analizar Ecosistema"):
    # Acceso seguro a credenciales
    try:
        OPENAI_API = st.secrets["OPENAI_API_KEY"]
        SERPER_API = st.secrets["SERPER_API_KEY"]
    except:
        st.error("Error de configuración: Las API Keys no se encuentran en los Secrets de Streamlit.")
        st.stop()

    if role:
        with st.spinner(f"Escaneando ecosistema digital en {selected_country}..."):
            # 1. Obtener datos de la SERP
            results = get_serp_data(role, PAISES[selected_country], IDIOMAS[selected_lang], SERPER_API)
            
            if results:
                tab1, tab2 = st.tabs(["📊 Análisis de Visibilidad", "💡 Estrategia Inclusiva"])
                
                with tab1:
                    st.markdown(f"**Top Perfiles detectados por Google en {selected_country}:**")
                    for r in results:
                        with st.expander(r['title'][:70]):
                            st.write(f"*Meta-descripción:* {r.get('snippet')}")
                            st.link_button("Explorar Perfil", r['link'])
                
                with tab2:
                    # 2. Análisis IA con enfoque inclusivo
                    analysis = get_ai_recommendations(role, results, selected_lang, OPENAI_API)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("#### 🏷️ Keywords Semánticas")
                        st.info(", ".join(analysis['keywords']))
                        st.caption("Nota: Estas palabras han sido filtradas para evitar sesgos de género y maximizar la neutralidad profesional.")
                    
                    with col_b:
                        st.markdown("#### ✍️ Titulares Sugeridos")
                        for t in analysis['titulares']:
                            st.code(t, language=None)
                            
                st.success("Análisis completado con éxito.")
            else:
                st.warning("No se encontraron resultados suficientes para este cargo. Prueba con términos más amplios.")
    else:
        st.warning("Por favor, introduce un cargo para comenzar.")

# Footer
st.markdown(f"""
    <div class="footer">
    Herramienta impulsada por <b>Crawla Colab</b><br>
    Potenciando el ecosistema digital desde <a href="https://colab.crawla.agency" target="_blank">colab.crawla.agency</a>
    </div>
    """, unsafe_allow_html=True)
