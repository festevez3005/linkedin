import streamlit as st
import requests
import openai
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="LinkedIn Optimizer | Crawla Colab",
    page_icon="🌈",
    layout="wide"
)

# --- ESTILOS Y BRANDING INCLUSIVO ---
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stButton>button { background-color: #6366f1; color: white; border-radius: 8px; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #4f46e5; border: none; }
    .inclusive-banner { 
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899); 
        padding: 10px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;
    }
    .footer { text-align: center; margin-top: 50px; color: #888; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE SEGMENTACIÓN ---
PAISES = {
    "Global": "gl", "España": "es", "México": "mx", "Colombia": "co", 
    "Argentina": "ar", "Chile": "cl", "Perú": "pe", "Ecuador": "ec", "Uruguay": "uy"
}

IDIOMAS = {"Español": "es", "Inglés": "en", "Portugués": "pt"}

# --- LÓGICA DE IA CON ENFOQUE INCLUSIVO ---

def get_ai_recommendations(query, profiles, lang, api_key):
    client = openai.OpenAI(api_key=api_key)
    context = "\n".join([f"- {p.get('title')}: {p.get('snippet')}" for p in profiles])
    
    # Prompt diseñado para eliminar sesgos de género y promover la diversidad
    prompt = f"""
    Eres una Coach experta en Marca Profesional y Estrategia de LinkedIn, con un enfoque profundamente inclusivo y consciente de la diversidad (Mujeres, comunidad LGBT+, hombres y minorías).
    
    TU MISIÓN:
    Analizar estos resultados de búsqueda para '{query}' y ofrecer optimización:
    {context}
    
    GUÍAS DE INCLUSIVIDAD:
    - Utiliza lenguaje neutro o inclusivo que no asuma género.
    - Evita sesgos históricos (ej: no sugerir términos masculinizados para roles de liderazgo).
    - Empodera la identidad del usuario sugiriendo keywords que resalten valor, no solo jerarquía.
    
    RESPUESTA (en {lang}):
    Proporciona 10 Keywords y 3 Titulares creativos y potentes.
    Responde en formato JSON con llaves 'keywords' (lista) y 'titulares' (lista).
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Eres una Coach inclusiva de Crawla Colab."},
                  {"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

def get_serp_data(query, country_code, lang_code, api_key):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": f'site:linkedin.com/in "{query}"', "gl": country_code, "hl": lang_code, "num": 6})
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        return response.json().get('organic', [])
    except: return []

# --- INTERFAZ ---

st.markdown('<div class="inclusive-banner">✨ Entorno de formación inclusivo: Mujeres, LGBT+ y aliados son bienvenidos.</div>', unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://colab.crawla.agency/wp-content/uploads/2023/10/Logo-Crawla-Colab.png", width=120) 
with col_title:
    st.title("LinkedIn Ecosystem Optimizer")
    st.caption("Una herramienta de **Crawla Colab** para un posicionamiento digital sin sesgos.")

# Sidebar de Recursos
with st.sidebar:
    st.header("🛠️ Recursos Crawla")
    st.link_button("📓 Descargar Workbook", "https://tu-link-al-workbook.com", use_container_width=True)
    st.link_button("🤖 Hablar con la Coach GEM", "https://tu-link-al-gem.com", use_container_width=True)
    
    st.divider()
    st.header("📍 Personalización")
    selected_country = st.selectbox("País objetivo", list(PAISES.keys()))
    selected_lang = st.selectbox("Idioma", list(IDIOMAS.keys()))
    
    st.info("Esta herramienta analiza el ecosistema digital para que tu perfil no solo exista, sino que destaque.")

# Entrada de Usuario
role = st.text_input("¿Qué rol o especialidad quieres potenciar?", placeholder="Ej: Dirección de Proyectos")

if st.button("Analizar Ecosistema"):
    try:
        api_o = st.secrets["OPENAI_API_KEY"]
        api_s = st.secrets["SERPER_API_KEY"]
    except:
        st.error("Configura las API Keys en los Secrets de Streamlit.")
        st.stop()

    if role:
        with st.spinner("Analizando con perspectiva inclusiva..."):
            results = get_serp_data(role, PAISES[selected_country], IDIOMAS[selected_lang], api_s)
            
            if results:
                t1, t2 = st.tabs(["🔍 Visibilidad en Google", "✨ Recomendaciones de la Coach"])
                
                with t1:
                    st.write(f"Perfiles que lideran la búsqueda en **{selected_country}**:")
                    for r in results:
                        with st.expander(r['title']):
                            st.write(r.get('snippet'))
                            st.link_button("Analizar Perfil", r['link'])
                
                with t2:
                    analysis = get_ai_recommendations(role, results, selected_lang, api_o)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("🔑 Keywords Sugeridas")
                        st.write(", ".join(analysis['keywords']))
                    with c2:
                        st.subheader("✍️ Titulares Inclusivos")
                        for t in analysis['titulares']:
                            st.code(t, language=None)
            else:
                st.warning("No encontramos resultados. Prueba con un término más amplio.")

# Footer Final
st.markdown(f"""
    <div class="footer">
    Parte del ecosistema de herramientas de <a href="https://colab.crawla.agency">Crawla Colab</a><br>
    Potenciando el talento diverso e inclusivo © 2026
    </div>
    """, unsafe_allow_html=True)
