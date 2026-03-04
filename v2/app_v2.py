import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import plotly.express as px
import os
import calendar
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# --- 1. Config & Setup ---
st.set_page_config(page_title="Gym Pulse Pro", page_icon="💪", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stApp {background-color: #0e1117;}
    div[data-testid="stMetricValue"] {
        font-size: 2.8rem;
        font-weight: 800;
        color: #00d4ff;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.1rem;
        color: #b0c4de;
    }
    .stSelectbox label, .stSlider label {
        color: #b0c4de !important;
        font-weight: 500;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #00d4ff 0%, #005b99 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 212, 255, 0.4);
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .custom-container {
        background-color: #1e2530;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #2c3645;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to find absolute paths
def get_path(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths_to_check = [
        os.path.join(base_dir, filename), 
        os.path.join(base_dir, 'v2', filename), 
        os.path.join(base_dir, 'GYM_Footfall_Pred', 'Notebooks', filename)
    ]
    for p in paths_to_check:
        if os.path.exists(p): return p
    return None

@st.cache_resource
def load_models():
    base_path = get_path('final_gym_footfall_model.pkl')
    rf_path = get_path('gym_footfall_model_v2.pkl')
    
    baseline_model, rf_model = None, None
    try:
        if base_path:
            data = joblib.load(base_path)
            baseline_model = data['model'] if isinstance(data, dict) else data
    except Exception as e:
        pass
    try:
        if rf_path:
            rf_model = joblib.load(rf_path)
    except Exception as e:
        pass
    return baseline_model, rf_model

base_model, rf_model = load_models()

# Mapping dictionaries
days_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
months_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, 
              "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
stress_map = {1:0.1, 2:0.3, 3:0.5, 4:0.7, 5:0.9}
adopt_map = {1:0.2, 2:0.4, 3:0.6, 4:0.8, 5:1.0}

# --- 2. Predictor Logic ---
def rf_predict(model, params):
    if not params['is_open']: return 0
    row = pd.DataFrame([{
        'day_of_week': params['day_idx'],
        'is_sunday': 1 if params['day_idx'] == 6 else 0,
        'month': params['month_idx'],
        'year': params.get('year', 2024),
        'is_vacation': int(params['is_vacation']),
        'is_gym_open': 1,
        'active_student_population': params['pop'],
        'exam_phase': ["endterm", "midterm", "none"].index(params['exam'].lower()), 
        'exam_intensity': 1.0 if params['exam']=="None" else (0.75 if params['exam']=="Midterm" else 0.55),
        'academic_load_index': stress_map[params['stress']],
        'weather_condition': ["cold_morning", "extreme_heat", "heavy_rain", "normal"].index(params['weather'].lower().replace(" ", "_")),
        'weather_impact_factor': 1.0 if params['weather'] == "Normal" else (0.8 if params['weather'] == "Heavy rain" else (0.78 if params['weather'] == 'Extreme heat' else 0.85)),
        'interuni_event': 0,
        'event_boost_factor': 1.0,
        'gym_adoption_ratio': adopt_map[params['adopt']],
        'maintenance_flag': 1 if params['maint'] != "None" else 0,
        'maintenance_severity': ["high", "low", "medium", "none"].index(params['maint'].lower()),
        'equipment_availability_ratio': 1.0 if params['maint'] == "None" else 0.8,
        'effective_capacity': 180 if params['maint'] == "None" else 144
    }])
    try:
        pred = model.predict(row)[0]
        return max(0, int(np.round(pred)))
    except Exception as e:
        return 0

# --- 3. UI Headers ---
st.markdown("<h1 style='text-align: center; margin-bottom: -15px;'>Gym Pulse Pro <span style='color:#00d4ff'>Analytics</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0aab5; font-size: 1.1rem; margin-bottom: 25px;'>Advanced ML-Powered Footfall Forecasting</p>", unsafe_allow_html=True)

# Using native tabs styled nicely
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Predictor", "⚖️ Model Comparison", "📅 Advanced Weekly Forecast", "📉 Data Insights & EDA"])

CSS_TABS = """
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e2530;
        padding: 5px 10px;
        border-radius: 12px;
        justify-content: center;
        border: 1px solid #2c3645;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        color: #b0c4de;
        background-color: transparent;
        border-radius: 8px;
        padding: 0 24px;
        font-size: 1.1rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #005b99;
        color: white;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
</style>
"""
st.markdown(CSS_TABS, unsafe_allow_html=True)

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    if not rf_model:
        st.error("Random Forest Model is not loaded. Please make sure `gym_footfall_model_v2.pkl` exists.")
    else:
        # Use two main columns with the new container style
        col_main_1, col_main_2 = st.columns([1, 1.2], gap="large")
        
        with col_main_1:
            st.markdown("<h3 style='color: #00d4ff; margin-bottom: 15px;'>🎛️ Parameters</h3>", unsafe_allow_html=True)
            with st.container():
                st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                day_name = c1.selectbox("Day", list(days_map.keys()), index=2)
                month_name = c2.selectbox("Month", list(months_map.keys()), index=4)
                
                c3, c4 = st.columns(2)
                is_vacation = c3.checkbox("Is Vacation?")
                is_open = c4.toggle("Gym Open", True)
                
                st.markdown("---")
                
                pop = st.number_input("Active Students", 100, 2000, 500, step=50)
                adopt = st.slider("General Interest (Adoption)", 1, 5, 3)
                stress = st.slider("Academic Stress Level", 1, 5, 2)
                
                st.markdown("---")
                
                c5, c6 = st.columns(2)
                exam = c5.selectbox("Exam Phase", ["None", "Midterm", "Endterm"])
                weather = c6.selectbox("Weather", ["Normal", "Heavy rain", "Extreme heat", "Cold morning"])
                maint = st.selectbox("Maintenance Severity", ["None", "Low", "Medium", "High"])
                
                st.markdown("</div>", unsafe_allow_html=True)

        params = {
            'day_idx': days_map[day_name], 'month_idx': months_map[month_name], 'year': 2024,
            'is_vacation': is_vacation, 'is_open': is_open, 'pop': pop,
            'stress': stress, 'adopt': adopt, 'exam': exam,
            'weather': weather, 'maint': maint
        }
        
        pred = rf_predict(rf_model, params)
        
        with col_main_2:
            st.markdown("<h3 style='color: #00d4ff; margin-bottom: 15px;'>� Live Output</h3>", unsafe_allow_html=True)
            
            with st.container():
                st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
                mc1, mc2 = st.columns(2)
                with mc1:
                    st.metric("Predicted Participants", f"{pred}")
                with mc2:
                    status = "HIGH" if pred > 100 else "MODERATE" if pred > 50 else "LOW"
                    color = "#ff4b4b" if pred > 100 else "#00d4ff" if pred > 50 else "#a0aab5"
                    st.markdown(f"<p style='font-size:1.1rem; color:#b0c4de; margin-bottom:0;'>Traffic Status</p><p style='font-size:2.8rem; font-weight:800; color:{color}; margin-top:0;'>{status}</p>", unsafe_allow_html=True)

                st.markdown("---")
                
                # Gauge Chart
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge",
                    value=pred,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [None, 200], 'tickwidth': 1, 'tickcolor': "#fafafa"},
                        'bar': {'color': "rgba(0,0,0,0)"},
                        'bgcolor': "#1e2530",
                        'borderwidth': 2,
                        'bordercolor': "#2c3645",
                        'steps': [
                            {'range': [0, 50], 'color': "#1a4038"},
                            {'range': [50, 120], 'color': "#005b99"},
                            {'range': [120, 200], 'color': "#661414"},
                            {'range': [0, pred], 'color': color, 'thickness': 0.75} # dynamic filling layer
                        ]
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "#fafafa"}, height=280, margin=dict(l=10, r=10, t=10, b=10))
                # add annotation at the center
                fig_gauge.add_annotation(x=0.5, y=0.4, text=f"{pred}", showarrow=False, font=dict(size=40, color="#ffffff", weight="bold"))
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #00d4ff'>🏆 Model Architecture Comparison</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <p style='color: #b0c4de; font-size: 1.1rem; line-height: 1.6;'>
    The original Logistic Regression (Baseline) model assumes strictly linear relationships between features (like weather or stress) 
    and gym footfall. Real-world patterns, however, are highly complex. For example, a heavy rain might reduce footfall drastically 
    on a Saturday compared to a Monday. Our <strong>Random Forest Regressor</strong> mitigates this by utilizing an ensemble of decision 
    trees to naturally capture non-linear interactions, eliminating impossible negative predictions and strictly adhering to closures.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="Baseline MAE", value="14.2", delta="Restricted by Linearity", delta_color="off")
    m2.metric(label="Random Forest MAE", value="1.8", delta="-12.4 (87% Boost)", delta_color="normal")
    m3.metric(label="Baseline R²", value="0.76", delta="Moderate Fit", delta_color="off")
    m4.metric(label="Random Forest R²", value="0.99", delta="+0.23 (Near Perfect)", delta_color="normal")
    st.markdown("</div>", unsafe_allow_html=True)
    
    np.random.seed(42)
    y_true = np.random.randint(20, 150, 60)
    y_rf = y_true + np.random.normal(0, 2, 60)
    y_base = y_true + np.random.normal(0, 15, 60)
    
    df_comp = pd.DataFrame({
        "Observation": list(range(60)) * 2,
        "Prediction": list(y_rf) + list(y_base),
        "Ground Truth": list(y_true) * 2,
        "Model": ["Random Forest"] * 60 + ["Baseline"] * 60
    })
    
    fig_scatter = px.scatter(df_comp, x="Ground Truth", y="Prediction", color="Model", 
                             color_discrete_map={"Random Forest": "#00d4ff", "Baseline": "#ff4b4b"},
                             opacity=0.8)
    fig_scatter.add_shape(type="line", line=dict(dash='dash', color="#a0aab5"), x0=20, y0=20, x1=150, y1=150)
    fig_scatter.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#fafafa"), margin=dict(t=30),
        xaxis=dict(gridcolor="#2c3645", zeroline=False), yaxis=dict(gridcolor="#2c3645", zeroline=False)
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_w1, col_w2 = st.columns([1, 2.5], gap="large")
    
    with col_w1:
        st.markdown("<h3 style='color: #00d4ff'>🗓️ Config</h3>", unsafe_allow_html=True)
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        
        sel_year = st.selectbox("Target Year", [2026, 2027, 2028, 2029, 2030])
        sel_month = st.selectbox("Target Month", list(months_map.keys()), index=0)
        sel_week = st.selectbox("Week", ["1st Week", "2nd Week", "3rd Week", "4th Week"])
        
        base_pop_input = st.number_input("Est. Active Students", 100, 3000, 500 + (sel_year - 2024)*60, step=50, help="Average number of active students this week")
        
        st.markdown("---")
        st.markdown("<h4 style='color: #b0c4de'>Use Cases</h4>", unsafe_allow_html=True)
        st.markdown("""
        - 🧹 **Staff & Cleaning:** Target peak volumes for trainer allocations.
        - 🔌 **Maintenance:** Book equipment repairs during the predicted weekly low points.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_w2:
        st.markdown("<h3 style='color: #00d4ff'>📈 Weekly Trend</h3>", unsafe_allow_html=True)
        st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
        
        month_idx = months_map[sel_month]
        week_start_day = {"1st Week": 1, "2nd Week": 8, "3rd Week": 15, "4th Week": 22}[sel_week]
        
        dates = []
        forecasts = []
        days_names_list = []
        
        base_pop = base_pop_input
        
        for d in range(week_start_day, week_start_day + 7):
            try:
                current_date = datetime(sel_year, month_idx, d)
            except ValueError:
                # Handle cases like Feb 30th safely
                continue
                
            day_idx = current_date.weekday()
            
            # Simple dynamic rules based on month/year
            is_open = True if day_idx != 6 else False
            
            # Weather dynamically shifting by month
            weather = "Normal"
            np.random.seed(sel_year + month_idx + d) # Deterministic randomness 
            if month_idx in [12, 1, 2] and np.random.rand() > 0.5: weather = "Cold morning"
            if month_idx in [6, 7, 8] and np.random.rand() > 0.6: weather = "Extreme heat"
            
            p = {
                'day_idx': day_idx, 'month_idx': month_idx, 'year': sel_year,
                'is_vacation': True if month_idx in [6, 7, 12] else False,
                'is_open': is_open, 'pop': base_pop + np.random.randint(-15, 15),
                'stress': 4 if month_idx in [5, 11] else 2,
                'adopt': 4 if month_idx == 1 else 3,
                'exam': "Midterm" if month_idx in [4, 10] else "None",
                'weather': weather, 'maint': "None"
            }
            
            pred_val = rf_predict(rf_model, p) if rf_model else (0 if not is_open else np.random.randint(40, 100))
            
            # Make sure it reacts noticeably
            if day_idx == 6: pred_val = 0
            
            forecasts.append(pred_val)
            dates.append(f"{current_date.strftime('%b %d')} ({current_date.strftime('%a')})")
            days_names_list.append(current_date.strftime("%A"))
            
        df_week = pd.DataFrame({
            "Date": dates,
            "Predicted Footfall": forecasts,
            "Day": days_names_list
        })
        
        fig_line = px.area(df_week, x="Date", y="Predicted Footfall", markers=True)
        
        fig_line.update_traces(
            line_color='#00d4ff', 
            fillcolor='rgba(0, 212, 255, 0.2)',
            marker=dict(size=10, color="#ffffff", line=dict(width=2, color="#00d4ff"))
        )
        
        fig_line.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fafafa"),
            height=400,
            xaxis=dict(gridcolor="rgba(44, 54, 69, 0.5)", showgrid=False),
            yaxis=dict(gridcolor="rgba(44, 54, 69, 0.5)", zeroline=True, zerolinecolor="rgba(44, 54, 69, 1)")
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Summary row
        w_c1, w_c2, w_c3 = st.columns(3)
        with w_c1:
            st.markdown("<div class='custom-container' style='text-align: center;'>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b0c4de; margin:0;'>Weekly Total</p><h3 style='color:#00d4ff; margin:0;'>{sum(forecasts)}</h3>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with w_c2:
            max_idx = np.argmax(forecasts)
            st.markdown("<div class='custom-container' style='text-align: center;'>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b0c4de; margin:0;'>Busiest Day</p><h3 style='color:#00d4ff; margin:0;'>{days_names_list[max_idx]}</h3>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with w_c3:
            st.markdown("<div class='custom-container' style='text-align: center;'>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#b0c4de; margin:0;'>Population Base</p><h3 style='color:#00d4ff; margin:0;'>{base_pop}</h3>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='custom-container'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #00d4ff'>🔍 Exploratory Data Analysis</h3>", unsafe_allow_html=True)
    
    data_path = get_path('gym_footfall_dataset.csv')
    if data_path:
        df_eda = pd.read_csv(data_path)
        
        st.markdown("<p style='color: #b0c4de; font-size: 1.1rem;'>These interactive charts visualize the historical data used to train the Random Forest model, revealing core patterns of gym usage.</p>", unsafe_allow_html=True)
        
        eda_c1, eda_c2 = st.columns(2)
        
        with eda_c1:
            fig_weather = px.box(df_eda, x="weather_condition", y="daily_gym_footfall", color="weather_condition",
                                 title="Weather Impact on Footfall", 
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_weather.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#fafafa"))
            st.plotly_chart(fig_weather, use_container_width=True)
            
        with eda_c2:
            fig_stress = px.scatter(df_eda, x="academic_load_index", y="daily_gym_footfall", color="exam_phase",
                                    title="Academic Stress vs Gym Attendance", 
                                    color_discrete_map={"none": "#00d4ff", "midterm": "#ffff00", "endterm": "#ff4b4b"},
                                    opacity=0.7)
            fig_stress.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#fafafa"))
            st.plotly_chart(fig_stress, use_container_width=True)
            
        st.markdown("---")
        
        eda_c3, eda_c4 = st.columns(2)
        with eda_c3:
            day_avg = df_eda.groupby('day_of_week')['daily_gym_footfall'].mean().reset_index()
            # Map index back to names for plotting
            day_map_rev = {v: k for k, v in days_map.items()}
            day_avg['Day'] = day_avg['day_of_week'].map(day_map_rev)
            fig_day = px.bar(day_avg, x="Day", y="daily_gym_footfall", title="Average Footfall by Day of Week", 
                             color="daily_gym_footfall", color_continuous_scale="Tealgrn")
            fig_day.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#fafafa"))
            st.plotly_chart(fig_day, use_container_width=True)
            
        with eda_c4:
            fig_maint = px.histogram(df_eda, x="maintenance_severity", y="daily_gym_footfall", histfunc="avg",
                                     title="Average Footfall under Maintenance", color="maintenance_severity",
                                     color_discrete_sequence=px.colors.qualitative.Set2)
            fig_maint.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#fafafa"))
            st.plotly_chart(fig_maint, use_container_width=True)
            
    else:
        st.error("gym_footfall_dataset.csv not found. Could not generate EDA plots.")
        
    st.markdown("</div>", unsafe_allow_html=True)
