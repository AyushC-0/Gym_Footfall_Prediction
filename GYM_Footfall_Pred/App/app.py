import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px

# --- 1. Config & Setup ---
st.set_page_config(page_title="Gym Pulse", page_icon="💪", layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>.main {background-color:#f8f9fa;} div.stButton>button:first-child {background-color:#007bff;color:white;width:100%;} div[data-testid='stMetricValue'] {font-size:32px;}</style>", unsafe_allow_html=True)

FEATURE_NAMES = [
    'day_of_week', 'is_sunday', 'month', 'year', 'is_vacation', 'is_gym_open', 'active_student_population', 
    'academic_load_index', 'interuni_event', 'event_boost_factor', 'gym_adoption_ratio', 'equipment_availability_ratio', 
    'exam_phase_midterm', 'exam_phase_none', 'weather_condition_extreme_heat', 'weather_condition_heavy_rain', 
    'weather_condition_normal', 'maintenance_severity_low', 'maintenance_severity_medium', 'maintenance_severity_none'
]

@st.cache_resource
def load_model():
    try:
        data = joblib.load('final_gym_footfall_model.pkl')
        return data['model'] if isinstance(data, dict) else data
    except: return None

model = load_model()
if not model: st.error("⚠️ Model file 'final_gym_footfall_model.pkl' not found."); st.stop()

# --- 2. Sidebar Controls ---
st.sidebar.title("⚙️ Settings")
c1, c2 = st.sidebar.columns(2)
day_name = c1.selectbox("Day", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], index=2)
month_name = c2.selectbox("Month", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], index=4)
is_vacation, is_open = st.sidebar.checkbox("Is Vacation?"), st.sidebar.toggle("Gym Open", True)

st.sidebar.markdown("---")
adopt = st.sidebar.slider("Interest (1-5)", 1, 5, 3)
stress = st.sidebar.slider("Stress (1-5)", 1, 5, 2)
exam = st.sidebar.selectbox("Exam Phase", ["None", "Midterm", "Endterm"])
pop = st.sidebar.number_input("Students", 100, 2000, 500, step=50)

st.sidebar.markdown("---")
weather = st.sidebar.selectbox("Weather", ["Normal", "Heavy Rain", "Extreme Heat"])
maint = st.sidebar.selectbox("Maintenance", ["None", "Low", "Medium"])

# --- 3. Prediction Logic ---
def predict(day_idx, month_idx, params):
    if not params['open']: return 0
    row = {
        'day_of_week': day_idx, 'is_sunday': int(day_idx==6), 'month': month_idx, 'year': 2024,
        'is_vacation': int(params['vacation']), 'is_gym_open': 1, 'active_student_population': params['pop'],
        'academic_load_index': {1:0.1, 2:0.3, 3:0.5, 4:0.7, 5:0.9}[params['stress']],
        'interuni_event': 0, 'event_boost_factor': 1.0,
        'gym_adoption_ratio': {1:0.2, 2:0.4, 3:0.6, 4:0.8, 5:1.0}[params['adopt']],
        'equipment_availability_ratio': 1.0,
        'exam_phase_midterm': int(params['exam']=="Midterm"), 'exam_phase_none': int(params['exam']=="None"),
        'weather_condition_extreme_heat': int(params['weather']=="Extreme Heat"),
        'weather_condition_heavy_rain': int(params['weather']=="Heavy Rain"),
        'weather_condition_normal': int(params['weather']=="Normal"),
        'maintenance_severity_low': int(params['maint']=="Low"),
        'maintenance_severity_medium': int(params['maint']=="Medium"),
        'maintenance_severity_none': int(params['maint']=="None")
    }
    return max(0, int(model.predict(pd.DataFrame([row])[FEATURE_NAMES])[0]))

# --- 4. Data Processing ---
days_map = {d:i for i,d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])}
months_map = {m:i+1 for i,m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
params = {'vacation':is_vacation, 'open':is_open, 'pop':pop, 'stress':stress, 'adopt':adopt, 'exam':exam, 'weather':weather, 'maint':maint}

# Calculate current & weekly
pred = predict(days_map[day_name], months_map[month_name], params)
forecast_df = pd.DataFrame([{"Day": d, "Footfall": predict(i, months_map[month_name], params)} 
                            for i, d in enumerate(days_map.keys())])

# --- 5. Dashboard UI ---
st.title("💪 Gym Pulse Dashboard")
c1, c2, c3 = st.columns([1, 1, 2])

# Top Row: Metrics & Gauge
color = "red" if pred > 100 else "orange" if pred > 50 else "green"
c1.markdown("### 🏃 Prediction")
c1.metric("Expected Students", pred)
c1.caption(f"Status: :{color}[**{'High' if pred>100 else 'Moderate' if pred>50 else 'Low'} Traffic**]")

c2.markdown("### 🌡️ Conditions")
c2.metric("Academic Stress", f"{stress}/5")
c2.metric("Weather", weather)

fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=pred, domain={'x': [0, 1], 'y': [0, 1]},
    gauge={'axis': {'range': [None, 200]}, 'bar': {'color': "#007bff"},
           'steps': [{'range': [0, 50], 'color': "#d4edda"}, {'range': [50, 100], 'color': "#fff3cd"}, {'range': [100, 200], 'color': "#f8d7da"}]}))
c3.plotly_chart(fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20)), use_container_width=True)

st.markdown("---")

# Bottom Row: Graphs
g1, g2 = st.columns([2, 1])

# Weekly Forecast Plot
fig_line = px.area(forecast_df, x="Day", y="Footfall", markers=True).update_traces(line_color='#007bff', fillcolor='rgba(0,123,255,0.2)')
fig_line.add_vline(x=day_name, line_dash="dot", line_color="red")
fig_line.add_annotation(x=day_name, y=1.05, yref="paper", text="Selected", showarrow=False, font=dict(color="red"))
g1.subheader("📅 Weekly Forecast"); g1.plotly_chart(fig_line.update_layout(xaxis_title=None, yaxis_title=None, height=350), use_container_width=True)

# Explainability Plot
impacts = pd.DataFrame([
    {"Factor": "Adoption", "Value": (adopt-1)*15}, {"Factor": "No Exams", "Value": 20 if exam=="None" else 0},
    {"Factor": "Midterms", "Value": 10 if exam=="Midterm" else 0}, {"Factor": "Stress", "Value": -1*stress*5},
    {"Factor": "Bad Weather", "Value": -10 if weather!="Normal" else 0}, {"Factor": "Base", "Value": 20}
])
fig_bar = px.bar(impacts[impacts['Value']!=0], x="Value", y="Factor", orientation='h', color="Value", color_continuous_scale="RdBu")
g2.subheader("🔍 Impacts"); g2.plotly_chart(fig_bar.update_layout(showlegend=False, height=350, yaxis={'categoryorder':'total ascending'}), use_container_width=True)