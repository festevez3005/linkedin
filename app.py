import streamlit as st
import requests
import openai
import pandas as pd

# Configuración de la interfaz
st.set_page_config(
    page_title="LinkedIn Ecosystem Optimizer",
    page_icon="🚀",
    layout="wide"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; background-color: #0077b5; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA ---

def get_google_linkedin_data(query, api_key):
    """Consulta a Serper.dev para ver quién domina el SEO de LinkedIn"""
    url = "https://google.serper.dev/search"
    # El 'dork' busca específicamente perfiles personales
    payload = {
        "q": f'site:linkedin.com/in "{query}"',
        "num": 6
    }
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json().get('organic', [])
    except Exception as e:
        st.error(f"Error en búsqueda: {e}")
        return []

def get_ai_analysis(query, profiles_data, api_key):
    """Usa OpenAI para generar keywords y sugerencias de titulares"""
    client = openai.OpenAI(api_key=api_key)
    
    # Preparamos un resumen de los snippets de Google para la IA
    benchmarking = "\n".join([f"- {p.get('title')}: {p.get('snippet')}" for p in profiles_data])
    
    prompt = f"""
    Como experto en SEO de LinkedIn y Marca Personal:
    1. Analiza estos resultados actuales de Google para '{query}':
    {benchmarking}
    
    2. Genera una lista de 12 palabras clave (Keywords) semánticas esenciales.
    3. Propón 3 opciones de 'Titular' (Headline) que mezclen SEO y atracción.
    
    Responde en formato JSON con las llaves: 'keywords' (lista) y 'titulares' (lista).
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error en IA: {e}")
        return None

# --- INTERFAZ DE USUARIO ---

st.title("🚀 LinkedIn Ecosystem Optimizer")
st.subheader("Optimiza tu perfil basándote en datos reales de Google")

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    st.info("Estas claves se pueden configurar de forma interna para que el alumno no las vea.")
    # Si usas st.secrets, puedes comentar estas líneas:
    user_openai_key = st.text_input("OpenAI API Key", type="password")
    user_serper_key = st.text_input("Serper API Key (Google)", type="password")
    
    st.divider()
    st.markdown("### ¿Cómo funciona?")
    st.write("1. Buscamos qué perfiles premia Google para tu cargo.")
    st.write("2. Analizamos sus palabras clave.")
    st.write("3. La IA te sugiere cómo ganarlos.")

# Input principal
col_in1, col_in2 = st.columns([2, 1])
with col_in1:
    target_role = st.text_input("¿Qué cargo o rol quieres posicionar?", placeholder="Ej: Especialista en Marketing Digital")

if st.button("Ejecutar Análisis de Ecosistema"):
    # Validación de llaves (usando inputs o secretos de Streamlit)
    api_o = user_openai_key or st.secrets.get("OPENAI_API_KEY")
    api_s = user_serper_key or st.secrets.get("SERPER_API_KEY")

    if not api_o or not api_s:
        st.warning("Faltan las API Keys para continuar.")
    else:
        with st.spinner("Analizando el mercado digital..."):
            # 1. Obtener datos de Google
            profiles = get_google_linkedin_data(target_role, api_s)
            
            if profiles:
                # 2. Análisis de IA
                analysis = get_ai_analysis(target_role, profiles, api_o)
                
                # 3. Mostrar Resultados
                tab1, tab2 = st.tabs(["📊 Competencia en Google", "💡 Optimización IA"])
                
                with tab1:
                    st.write("Estos son los perfiles que aparecen primero en motores de búsqueda:")
                    for p in profiles:
                        with st.container():
                            st.markdown(f"**[{p['title']}]({p['link']})**")
                            st.caption(p.get('snippet', 'Sin descripción'))
                            st.divider()
                
                with tab2:
                    if analysis:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.success("✅ Palabras Clave Recomendadas")
                            st.write(", ".join(analysis['keywords']))
                            st.info("Tip: Incluye estas palabras en tu sección 'Acerca de'.")
                        
                        with c2:
                            st.success("✍️ Sugerencias de Titular (Headline)")
                            for t in analysis['titulares']:
                                st.code(t, language=None)
            else:
                st.error("No se encontraron resultados. Intenta con un cargo más genérico.")
