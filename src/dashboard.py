import streamlit as st
import pandas as pd
from pathlib import Path
from collector import collect_data
from analyzer import analyze_data

# NetPulse - Network QoS Analysis Dashboard
# Created by: RaoVrn
# Version: 1.0.0
# Description: Real-time network quality monitoring dashboard using data collected
#              from Android devices. Analyzes signal strength, network types,
#              and performance metrics for comprehensive network insights.

import plotly.express as px

# --- Theme Colors ---
THEME = {
    'primary': '#00ADB5',     # Cyan - Main accent color
    'secondary': '#FF5722',   # Orange - Secondary highlights
    'success': '#4CAF50',     # Green - Positive indicators
    'error': '#FF5252',       # Red - Warnings/Poor metrics
    'bg_dark': '#0E1117',     # Dark background - Main background
    'bg_medium': '#1E1E1E',   # Medium dark - Cards/Sections
    'text': '#FFFFFF',        # White - Primary text
    'subtext': '#A0AEC0',     # Gray - Secondary text
    'grid': '#2C2C2C'        # Dark gray - Grid lines
}

# Configure Streamlit page
st.set_page_config(
    page_title="NetPulse Network QoS Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': 'NetPulse: Real-time network quality monitoring and analysis dashboard.',
        'Report a bug': 'https://github.com/RaoVrn/NetPulse/issues',
        'Get help': 'https://github.com/RaoVrn/NetPulse/wiki'
    }
)

# --- Project Info ---
st.markdown(f"""
<div style='background-color:{THEME["bg_dark"]};padding:1.5rem;border-radius:12px;margin-bottom:1rem;'>
    <h1 style='color:{THEME["text"]};margin-bottom:0.5rem;font-size:2.2rem;'>📊 NetPulse Network QoS Dashboard</h1>
    <h4 style='color:{THEME["primary"]};margin-top:0.5rem;font-size:1.3rem;'>Analyze • Visualize • Optimize</h4>
    <p style='color:{THEME["subtext"]};font-size:1.1rem;line-height:1.6;margin-top:1rem;'>
        <b style='color:{THEME["text"]}'>NetPulse</b> is your advanced network monitoring companion. It automatically:
        <ul style='color:{THEME["subtext"]};margin-top:0.5rem;'>
            <li>Collects and merges network data across multiple sources</li>
            <li>Analyzes QoS metrics for actionable insights</li>
            <li>Visualizes network performance patterns</li>
            <li>Identifies areas for network optimization</li>
        </ul>
    </p>
</div>
""", unsafe_allow_html=True)


# --- Data Collection ---
data_dir = Path(__file__).parent.parent / 'data'
output_file = str(data_dir / 'network_data_output.csv')
collect_data(str(data_dir), output_file)
df = pd.read_csv(output_file)

# --- Normalize & Prepare Data ---
# Standardize column names that may vary between CSVs
df = df.rename(columns={
    "dBm": "Signal_dBm",
    "Signal": "Signal_dBm",
    "NetworkType": "Network_Type",
    "Download": "Download_Mbps",
    "Upload": "Upload_Mbps",
    "Latency": "Latency_ms"
})

# Ensure required columns exist with safe defaults
for col, default in {
    "Signal_dBm": -120,
    "Network_Type": "Unknown",
    "Location": "Unknown",
    "Download_Mbps": 0.0,
    "Upload_Mbps": 0.0,
    "Latency_ms": 0.0
}.items():
    if col not in df.columns:
        df[col] = default

# Parse timestamps if available
if "Timestamp" in df.columns:
    try:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    except Exception:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

# Compute signal quality classification on the full dataframe so sidebar can use it
df["Signal_Quality"] = df["Signal_dBm"].apply(
    lambda x: "Excellent" if x > -85 else ("Good" if x > -95 else "Poor")
)


# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/network.png", width=64)
    # Sidebar Header
    st.markdown(f"""
        <div style='text-align:center;margin-bottom:1rem;'>
            <h2 style='color:{THEME["primary"]};font-size:1.5rem;'>NetPulse Controls</h2>
        </div>
    """, unsafe_allow_html=True)

    # Documentation Section
    with st.expander("📖 Documentation", expanded=True):
        st.markdown(f"""
        <div style='color:{THEME["text"]};'>
            <h4 style='color:{THEME["primary"]};'>About NetPulse Data</h4>
            <p>This dashboard analyzes real network data collected from your Android device. The data includes:</p>
            <ul>
                <li><b>Signal Strength (dBm)</b>: Ranges from -50 (excellent) to -120 (poor)</li>
                <li><b>Network Type</b>: Mobile data types (4G, 5G, etc.)</li>
                <li><b>Download/Upload</b>: Speed tests in Mbps</li>
                <li><b>Latency</b>: Network response time in milliseconds</li>
            </ul>
            <h4 style='color:{THEME["primary"]};'>How to Use</h4>
            <ol>
                <li>Use filters below to analyze specific network types</li>
                <li>Monitor real-time network performance metrics</li>
                <li>Identify signal quality patterns by location</li>
                <li>Track network performance over time</li>
            </ol>
            <h4 style='color:{THEME["primary"]};'>Signal Quality Scale</h4>
            <ul>
                <li style='color:{THEME["success"]};'>Excellent: > -85 dBm</li>
                <li style='color:{THEME["primary"]};'>Good: -85 to -95 dBm</li>
                <li style='color:{THEME["error"]};'>Poor: < -95 dBm</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Filter Section
    st.markdown(f"""
        <div style='margin-top:1.5rem;'>
            <h3 style='color:{THEME["primary"]};font-size:1.3rem;'>🎯 Filters</h3>
        </div>
    """, unsafe_allow_html=True)
    
    network_types = df["Network_Type"].unique().tolist() if "Network_Type" in df.columns else []
    selected_network = st.multiselect(
        "Select Network Types",
        network_types,
        default=network_types,
        key="network_filter"
    )
    
    filtered_df = df.copy()  # Create a copy to avoid SettingWithCopyWarning
    if selected_network:
        filtered_df = filtered_df[filtered_df["Network_Type"].isin(selected_network)]
    
    # Data Statistics
    total_points = len(filtered_df)
    time_range = ""
    if "Timestamp" in filtered_df.columns and not filtered_df.empty:
        start_date = pd.to_datetime(filtered_df["Timestamp"]).min()
        end_date = pd.to_datetime(filtered_df["Timestamp"]).max()
        time_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    
    st.markdown(f"""
        <div style='background-color:{THEME["bg_medium"]};padding:1rem;border-radius:8px;margin-top:1rem;'>
            <h4 style='color:{THEME["text"]};font-size:1rem;margin:0;'>📊 Dataset Overview</h4>
            <p style='color:{THEME["primary"]};font-size:1.8rem;font-weight:bold;margin:0.5rem 0;'>{total_points:,}</p>
            <p style='color:{THEME["subtext"]};font-size:0.9rem;margin:0;'>Data Points Collected</p>
            <p style='color:{THEME["text"]};font-size:0.9rem;margin-top:0.5rem;'>{time_range}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Network Health Score
    # Ensure Signal_Quality exists in the filtered dataframe
    if "Signal_Quality" not in filtered_df.columns:
        filtered_df = filtered_df.copy()
        filtered_df.loc[:, "Signal_Quality"] = filtered_df["Signal_dBm"].apply(
            lambda x: "Excellent" if x > -85 else ("Good" if x > -95 else "Poor")
        )

    signal_quality = filtered_df["Signal_Quality"].value_counts(normalize=True)
    health_score = (
        (signal_quality.get("Excellent", 0) * 100) +
        (signal_quality.get("Good", 0) * 60) +
        (signal_quality.get("Poor", 0) * 20)
    )
    
    st.markdown(f"""
        <div style='background-color:{THEME["bg_medium"]};padding:1rem;border-radius:8px;margin-top:1rem;'>
            <h4 style='color:{THEME["text"]};font-size:1rem;margin:0;'>🏥 Network Health Score</h4>
            <p style='color:{THEME["primary"]};font-size:1.8rem;font-weight:bold;margin:0.5rem 0;'>{health_score:.1f}%</p>
            <p style='color:{THEME["subtext"]};font-size:0.9rem;margin:0;'>Based on signal quality distribution</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""---""")
    st.markdown("<b>About NetPulse:</b> NetPulse helps you monitor and improve your network experience by providing actionable insights into signal quality, speed, and latency across different locations and network types.", unsafe_allow_html=True)


# --- Data Analysis ---
summary = analyze_data(output_file)
filtered_summary = analyze_data(output_file)
avg_signal = filtered_df["Signal_dBm"].mean()
avg_download = filtered_df["Download_Mbps"].mean()
avg_upload = filtered_df["Upload_Mbps"].mean()
avg_latency = filtered_df["Latency_ms"].mean()

# Signal Quality Distribution
filtered_df["Signal_Quality"] = filtered_df["Signal_dBm"].apply(
    lambda x: "Excellent" if x > -85 else ("Good" if x > -95 else "Poor")
)
signal_quality_dist = filtered_df["Signal_Quality"].value_counts().sort_index()

# Best & Worst Location
# Ensure Signal_Quality column exists and handle missing values
if "Signal_dBm" in filtered_df.columns:
    filtered_df["Signal_Quality"] = pd.cut(
        filtered_df["Signal_dBm"],
        bins=[-120, -95, -85, 0],
        labels=["Poor", "Good", "Excellent"],
        include_lowest=True
    )
else:
    filtered_df["Signal_Quality"] = "Unknown"

# Best & Worst Location with fallback for NaN values
if "Signal_dBm" in filtered_df.columns and "Location" in filtered_df.columns:
    best_location = filtered_df.loc[filtered_df["Signal_dBm"].idxmax(skipna=True), "Location"] if not filtered_df["Signal_dBm"].isna().all() else "No Data"
    worst_location = filtered_df.loc[filtered_df["Signal_dBm"].idxmin(skipna=True), "Location"] if not filtered_df["Signal_dBm"].isna().all() else "No Data"
else:
    best_location = "No Data"
    worst_location = "No Data"



# --- Summary Metrics ---
st.markdown(f"""
    <div style='margin-top:2rem;'>
        <h2 style='color:{THEME["text"]};font-size:1.5rem;'>
            📈 Network Performance Metrics
        </h2>
    </div>
""", unsafe_allow_html=True)

metrics_cols = st.columns(4)
metric_styles = [
    {"icon": "📡", "color": THEME["primary"]},
    {"icon": "⬇️", "color": THEME["success"]},
    {"icon": "⬆️", "color": THEME["secondary"]},
    {"icon": "⚡", "color": THEME["error"]}
]

for col, (metric, value, style) in zip(metrics_cols, [
    ("Signal Strength", f"{avg_signal:.1f} dBm", metric_styles[0]),
    ("Download Speed", f"{avg_download:.1f} Mbps", metric_styles[1]),
    ("Upload Speed", f"{avg_upload:.1f} Mbps", metric_styles[2]),
    ("Latency", f"{avg_latency:.1f} ms", metric_styles[3])
]):
    with col:
        st.markdown(f"""
            <div style='background-color:{THEME["bg_medium"]};padding:1.2rem;border-radius:10px;text-align:center;'>
                <div style='font-size:2rem;margin-bottom:0.5rem;'>{style["icon"]}</div>
                <h3 style='color:{THEME["text"]};font-size:1.1rem;margin:0;'>{metric}</h3>
                <p style='color:{style["color"]};font-size:1.5rem;font-weight:bold;margin:0.5rem 0;'>{value}</p>
            </div>
        """, unsafe_allow_html=True)
st.markdown('---')


# --- Signal Quality Distribution ---
st.markdown(f"""
    <h3 style='color:{THEME["text"]};font-size:1.3rem;margin-top:2rem;'>
        📊 Signal Quality Distribution
    </h3>
""", unsafe_allow_html=True)

import plotly.express as px
fig_quality = px.bar(
    signal_quality_dist,
    x=signal_quality_dist.index,
    y=signal_quality_dist.values,
    color=signal_quality_dist.index,
    color_discrete_map={
        "Excellent": THEME["success"],
        "Good": THEME["primary"],
        "Poor": THEME["error"]
    },
    labels={"x": "Quality", "y": "Count"},
    template="plotly_dark"
)

fig_quality.update_layout(
    plot_bgcolor=THEME["bg_dark"],
    paper_bgcolor=THEME["bg_dark"],
    font_color=THEME["text"],
    showlegend=False,
    margin=dict(t=0, l=0, r=0, b=0),
    xaxis_title="Signal Quality",
    yaxis_title="Number of Readings",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor=THEME["bg_medium"])
)
st.plotly_chart(fig_quality, use_container_width=True)


# --- Best & Worst Location ---
st.markdown(f"""
    <h3 style='color:{THEME["text"]};font-size:1.3rem;margin-top:2rem;'>
        📍 Location Analysis
    </h3>
""", unsafe_allow_html=True)

col_loc1, col_loc2 = st.columns(2)

with col_loc1:
    st.markdown(f"""
        <div style='background-color:{THEME["bg_medium"]};padding:1.2rem;border-radius:10px;border-left:4px solid {THEME["success"]};'>
            <h4 style='color:{THEME["text"]};margin:0;'>🎯 Best Signal Location</h4>
            <p style='color:{THEME["success"]};font-size:1.2rem;margin:0.5rem 0;'>{best_location}</p>
        </div>
    """, unsafe_allow_html=True)

with col_loc2:
    st.markdown(f"""
        <div style='background-color:{THEME["bg_medium"]};padding:1.2rem;border-radius:10px;border-left:4px solid {THEME["error"]};'>
            <h4 style='color:{THEME["text"]};margin:0;'>⚠️ Poor Signal Location</h4>
            <p style='color:{THEME["error"]};font-size:1.2rem;margin:0.5rem 0;'>{worst_location}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- Visualizations ---
st.markdown(f"""
    <h3 style='color:{THEME["text"]};font-size:1.3rem;'>
        📡 Network Type Analysis
    </h3>
""", unsafe_allow_html=True)

# Prepare data
avg_signal_by_net = filtered_df.groupby("Network_Type")["Signal_dBm"].agg([
    ("mean", "mean"),
    ("count", "count")
]).reset_index()

# Create enhanced bar chart
fig_avg_signal = px.bar(
    avg_signal_by_net,
    x="Network_Type",
    y="mean",
    color="Network_Type",
    text="mean",
    color_discrete_sequence=[THEME["primary"], THEME["secondary"], THEME["success"]],
    labels={
        "mean": "Average Signal (dBm)",
        "Network_Type": "Network Type"
    },
    template="plotly_dark"
)
fig_avg_signal.update_layout(
    plot_bgcolor=THEME['bg_dark'],
    paper_bgcolor=THEME['bg_dark'],
    font_color=THEME['text'],
    showlegend=True,
    margin=dict(t=20, l=0, r=0, b=0),
    xaxis_title="Network Type",
    yaxis_title="Average Signal (dBm)",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor=THEME['grid']),
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor=THEME['bg_medium']
    )
)
st.plotly_chart(fig_avg_signal, use_container_width=True)

st.markdown(f"""
    <h3 style='color:{THEME["text"]};font-size:1.3rem;margin-top:2rem;'>
        📊 Signal Quality Distribution
    </h3>
    <p style='color:{THEME["subtext"]};'>Distribution of signal strength quality categories across collected data points.</p>
""", unsafe_allow_html=True)

signal_strength_dist = filtered_df["Signal_Quality"].value_counts().reset_index()
signal_strength_dist.columns = ["Quality", "Count"]

# Add percentage calculation
total_count = signal_strength_dist["Count"].sum()
signal_strength_dist["Percentage"] = (signal_strength_dist["Count"] / total_count * 100).round(1)

fig_strength = px.bar(
    signal_strength_dist,
    x="Quality",
    y="Count",
    color="Quality",
    text="Percentage",
    color_discrete_map={
        "Excellent": THEME["success"],
        "Good": THEME["primary"],
        "Poor": THEME["error"]
    },
    labels={
        "Count": "Number of Readings",
        "Quality": "Signal Quality",
        "Percentage": "Percentage (%)"
    },
    template="plotly_dark"
)
# Customize the bar chart
fig_strength.update_layout(
    plot_bgcolor=THEME["bg_dark"],
    paper_bgcolor=THEME["bg_dark"],
    font_color=THEME["text"],
    showlegend=False,
    margin=dict(t=20, l=0, r=0, b=0),
    xaxis=dict(showgrid=False, title="Signal Quality"),
    yaxis=dict(showgrid=True, gridcolor=THEME["bg_medium"], title="Number of Readings")
)

# Add percentage labels on top of bars
fig_strength.update_traces(
    texttemplate='%{text}%',
    textposition='outside'
)

st.plotly_chart(fig_strength, use_container_width=True)

# Time analysis section
st.markdown(f"""
    <div style='margin-top:2rem;border-top:1px solid {THEME["bg_medium"]};padding-top:2rem;'>
        <h3 style='color:{THEME["text"]};font-size:1.3rem;'>
            📈 Network Performance Timeline
        </h3>
        <p style='color:{THEME["subtext"]};'>Temporal analysis of signal strength variations across different network types.</p>
    </div>
""", unsafe_allow_html=True)

if "Timestamp" in filtered_df.columns:
    # Process time data
    filtered_df["Timestamp"] = pd.to_datetime(filtered_df["Timestamp"])
    time_df = filtered_df.sort_values("Timestamp")
    
    # Create enhanced time series plot with network type coloring
    fig_time = px.line(
        time_df,
        x="Timestamp",
        y="Signal_dBm",
        color="Network_Type",
        color_discrete_sequence=[THEME["primary"], THEME["secondary"], THEME["success"], THEME["error"]],
        labels={
            "Signal_dBm": "Signal Strength (dBm)",
            "Timestamp": "Time",
            "Network_Type": "Network Type"
        },
        template="plotly_dark"
    )
    
    # Add range selector and improve layout
    fig_time.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all", label="All")
            ]),
            bgcolor=THEME["bg_medium"],
            font=dict(color=THEME["text"])
        )
    )
    fig_time.update_layout(xaxis_title="Time", yaxis_title="Signal (dBm)", plot_bgcolor=THEME['bg_dark'], paper_bgcolor=THEME['bg_dark'], font_color=THEME['text'])
    st.plotly_chart(fig_time, use_container_width=True)
else:
    st.info("No timestamp data available for time series plot.")
st.markdown('---')


# --- Raw Data Expander ---
with st.expander('Show Raw Data'):
    st.dataframe(filtered_df, use_container_width=True)

# --- Custom Styling ---
st.markdown(f"""
<style>
    .stMetric {{text-align: center;}}
    .stExpander {{background-color: {THEME['bg_medium']};}}
    div[data-testid="stSidebar"] > div:first-child {{background-color: {THEME['bg_dark']};}}
    .block-container {{background-color: {THEME['bg_dark']};}}
    h1, h2, h3, h4 {{font-family: 'Segoe UI', 'Arial', sans-serif;}}
    /* Tweak header and text colors */
    .css-1v0mbdj.etr89bj1 {{color: {THEME['text']};}}
</style>
""", unsafe_allow_html=True)
