"""SupeRR Selector Season 2 - interactive dashboard.  Run:  streamlit run superr_dashboard.py
Requires: streamlit, plotly, pandas, numpy"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SupeRR Selector - Who Delivers When It Matters?", page_icon="🏏", layout="wide", initial_sidebar_state="auto")

# JS: inject a <style> tag directly into parent document head — bypasses Streamlit CSS scoping
components.html("""
<script>
function patchSidebarToggle() {
  var doc = window.parent.document;

  // Inject persistent style tag into parent <head>
  if (!doc.getElementById('superrr-toggle-fix')) {
    var s = doc.createElement('style');
    s.id = 'superrr-toggle-fix';
    s.textContent = [
      '[data-testid="collapsedControl"]{background:#1E293B!important;border-radius:0 8px 8px 0!important;box-shadow:2px 2px 10px rgba(15,23,42,.3)!important;opacity:1!important;visibility:visible!important;display:flex!important;}',
      '[data-testid="collapsedControl"] button{background:transparent!important;color:#fff!important;}',
      '[data-testid="collapsedControl"] svg,[data-testid="collapsedControl"] button svg{color:#fff!important;fill:#fff!important;stroke:#fff!important;}',
      '[data-testid="stSidebarCollapseButton"] button,[data-testid="stSidebarHeader"] button{background:#334155!important;border-radius:6px!important;color:#fff!important;}',
      '[data-testid="stSidebarCollapseButton"] button svg,[data-testid="stSidebarHeader"] button svg{color:#fff!important;fill:#fff!important;}',
      '[data-testid="stSidebarCollapseButton"] button:hover,[data-testid="stSidebarHeader"] button:hover{background:#475569!important;}'
    ].join('');
    doc.head.appendChild(s);
  }

  // Also directly style any existing elements right now
  var selectors = [
    '[data-testid="collapsedControl"]',
    '[data-testid="collapsedControl"] button',
    '[data-testid="stSidebarCollapseButton"] button',
    '[data-testid="stSidebarHeader"] button'
  ];
  selectors.forEach(function(sel) {
    doc.querySelectorAll(sel).forEach(function(el) {
      el.style.setProperty('background-color', '#1E293B', 'important');
      el.style.setProperty('color', '#ffffff', 'important');
      el.style.setProperty('opacity', '1', 'important');
      el.style.setProperty('visibility', 'visible', 'important');
    });
    doc.querySelectorAll(sel + ' svg, ' + sel + 'svg').forEach(function(el) {
      el.style.setProperty('color', '#ffffff', 'important');
      el.style.setProperty('fill', '#ffffff', 'important');
    });
  });
}

// Run immediately, then watch for Streamlit re-renders
patchSidebarToggle();
var obs = new MutationObserver(patchSidebarToggle);
obs.observe(window.parent.document.body, { childList: true, subtree: true });
</script>
""", height=0)

BLUE, GREEN, ORANGE, RED, INDIGO, TEAL, GREY = "#2563EB", "#059669", "#D97706", "#E11D48", "#6366F1", "#0D9488", "#64748B"
LAYERS = ["L1 Pressure vs usual", "L2 Behavioural", "L3 Stakes wins vs expected", "L4 Selection trust", "L5 Evidence depth", "L6 Stakes-weighted awards"]
BASE_W = [0.22, 0.32, 0.16, 0.08, 0.12, 0.10]
LCOL = [BLUE, GREEN, ORANGE, INDIGO, TEAL, RED]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box !important; }

html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* ── Root layout fix ─────────────────────────────────────────────────────── */
html, body { overflow-x: hidden !important; }

.stApp {
  background-color: #F8FAFC !important;
  color: #0F172A !important;
  overflow: hidden !important;
  width: 100vw !important;
}

/* The app view container is a flex row: sidebar | main.
   Tell it not to exceed the viewport. */
[data-testid="stAppViewContainer"] {
  background-color: #F8FAFC !important;
  display: flex !important;
  flex-direction: row !important;
  width: 100vw !important;
  overflow: hidden !important;
}

/* Main section: flex-grow so it fills remaining space after the 240px sidebar.
   min-width: 0 is critical — without it flex items refuse to shrink. */
[data-testid="stAppViewContainer"] > section.main {
  flex: 1 1 0 !important;
  min-width: 0 !important;
  max-width: calc(100vw - 240px) !important;
  overflow-x: hidden !important;
}

.main .block-container {
  padding: 1rem 1.5rem 2rem 1.5rem !important;
  max-width: 100% !important;
  width: 100% !important;
  overflow-x: hidden !important;
  box-sizing: border-box !important;
}

/* Every column, chart and table must stay inside its container */
[data-testid="stColumn"],
[data-testid="stHorizontalBlock"],
[data-testid="stPlotlyChart"],
[data-testid="stDataFrame"] {
  min-width: 0 !important;
  max-width: 100% !important;
  overflow-x: hidden !important;
  box-sizing: border-box !important;
}

[data-testid="stHeader"] { background: transparent !important; }

/* Sidebar — distinct from app background with shadow separator */
[data-testid="stSidebar"] {
  background-color: #1E293B !important;
  border-right: none;
  box-shadow: 4px 0 20px rgba(15, 23, 42, 0.18);
}
[data-testid="stSidebar"] > div:first-child {
  background-color: #1E293B !important;
}
/* Sidebar heading */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: #FFFFFF !important;
}
/* Sidebar body text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] [data-testid="stCaption"],
[data-testid="stSidebar"] .stCaption {
  color: #CBD5E1 !important;
}
/* Sidebar slider + radio labels */
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] [data-baseweb="radio"] label {
  color: #E2E8F0 !important;
  font-weight: 500;
}
/* ── Sidebar toggle — visible on white background ── */
[data-testid="collapsedControl"] {
  background-color: #1E293B !important;
  border-radius: 0 8px 8px 0 !important;
  box-shadow: 2px 2px 8px rgba(15,23,42,0.2) !important;
}
[data-testid="collapsedControl"] button { background: transparent !important; color: #FFFFFF !important; }
[data-testid="collapsedControl"] svg,
[data-testid="collapsedControl"] button svg { color: #FFFFFF !important; fill: #FFFFFF !important; }
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarHeader"] button { background-color: #334155 !important; border-radius: 6px !important; color: #FFFFFF !important; }
[data-testid="stSidebarCollapseButton"] button svg,
[data-testid="stSidebarHeader"] button svg { color: #FFFFFF !important; fill: #FFFFFF !important; }
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarHeader"] button:hover { background-color: #475569 !important; }

/* Sidebar divider */
[data-testid="stSidebar"] hr {
  border-color: #334155 !important;
}
/* Sidebar selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] {
  background-color: #0F172A !important;
  border-color: #334155 !important;
  color: #E2E8F0 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * {
  color: #E2E8F0 !important;
  background-color: #0F172A !important;
}
/* Sidebar markdown bold */
[data-testid="stSidebar"] strong {
  color: #FFFFFF !important;
  font-weight: 700;
}
/* Sidebar slider track colour */
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [role="slider"] {
  background-color: #2563EB !important;
}
[data-testid="stSidebar"] .stSlider div[data-testid="stThumbValue"] {
  color: #FFFFFF !important;
}
/* Radio active dot */
[data-testid="stSidebar"] [data-baseweb="radio"] [data-checked="true"] ~ div {
  background-color: #2563EB !important;
}

h1, h2, h3, .stMarkdown, .stCaption, label, p { color: #0F172A; }
h1 { font-weight: 700; letter-spacing: -0.03em; }
h2, h3 { font-weight: 600; letter-spacing: -0.02em; }

/* Hero banner */
.hero {
  padding: 22px 26px; border-radius: 18px;
  background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 55%, #2563EB 100%);
  color: #FFFFFF; margin-bottom: 16px;
  box-shadow: 0 8px 20px -4px rgba(37,99,235,0.22);
}
.hero h1 { color: #FFFFFF !important; margin: 0; font-size: 1.8rem; }
.hero p  { margin: 6px 0 0 0; opacity: 0.9; font-size: 0.92rem; color: #E2E8F0 !important; }

/* KPI cards — compact so 5 fit */
.card {
  background: #FFFFFF; border-radius: 12px; padding: 10px 12px;
  box-shadow: 0 1px 6px rgba(15,23,42,0.05); border: 1px solid #E2E8F0;
  margin-bottom: 10px; width: 100%;
}
.kpi  { font-size: 1.35rem; font-weight: 700; color: #0F172A; line-height: 1.2; }
.kpil { font-size: 0.65rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; margin-bottom: 2px; }

/* Note callout */
.note {
  background: #F8FAFC; border-left: 4px solid #2563EB; padding: 12px 16px;
  border-radius: 8px; font-size: 0.86rem; color: #334155;
  border: 1px solid #E2E8F0; margin: 12px 0; line-height: 1.5;
}

/* Tab bar: scrollable, hidden scrollbar */
.stTabs [data-baseweb="tab-list"] {
  gap: 3px; background: #E2E8F0; padding: 4px; border-radius: 10px;
  overflow-x: auto; flex-wrap: nowrap;
  scrollbar-width: none; -ms-overflow-style: none;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
  border-radius: 7px; padding: 5px 10px; height: auto;
  color: #64748B !important; font-weight: 500; font-size: 0.8rem;
  white-space: nowrap; flex-shrink: 0;
}
.stTabs [aria-selected="true"] {
  background: #FFFFFF !important; color: #0F172A !important;
  font-weight: 600; box-shadow: 0 1px 6px rgba(15,23,42,0.08);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* Plotly chart wrapper — no padding, just border + shadow */
[data-testid="stPlotlyChart"] {
  background: #FFFFFF; border-radius: 14px;
  border: 1px solid #E2E8F0; box-shadow: 0 1px 8px rgba(15,23,42,0.04);
  margin-bottom: 14px; width: 100% !important; overflow: hidden;
}

/* Columns: never overflow their container */
[data-testid="stHorizontalBlock"] { gap: 0.75rem !important; min-width: 0; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-width: 0 !important; }

/* Dataframes scroll internally */
[data-testid="stDataFrame"] { width: 100% !important; }
</style>""", unsafe_allow_html=True)

# ------------------------------------------------------------------ data
BAT = pd.DataFrame([
 # name, L1..L6, consensus score, expRk, top3, lo, hi, Bp, runs, outs, SR, A, U, Point, Score, Comp, apps, yrs, trust, high, w, exp, mom
 ("Virat Kohli",96,92,65,96,100,100,84.0,1.51,95,1,3,468,761,19,162.6,23.2,-10.4,10.5,1.2,80,92,5,96,23,14,11.9,10),
 ("Shikhar Dhawan",100,96,70,71,64,21,72.2,3.39,58,1,6,115,182,3,158.3,25.2,11.6,13.4,2.7,97,30,3,71,3,2,1.3,2),
 ("Ravindra Jadeja",73,89,78,85,81,42,71.5,3.46,55,2,5,665,893,27,134.3,19.1,0.6,8.9,0.4,29,76,5,85,20,12,8.6,6),
 ("Rohit Sharma",72,74,77,90,82,54,69.0,4.02,44,2,7,239,398,11,166.5,18.9,14.4,8.8,-7.7,np.nan,91,5,90,21,13,9.6,5),
 ("Mahendra Singh Dhoni",57,100,78,81,68,20,66.3,4.56,26,2,7,330,447,14,135.5,28.0,5.7,13.4,4.8,18,58,4,81,15,9,6.4,1),
 ("Dinesh Karthik",60,89,48,96,78,34,63.8,5.09,17,3,7,564,904,31,160.3,34.7,-31.6,9.6,1.9,24,68,3,96,18,9,9.2,4),
 ("Rashid Khan",18,69,53,96,76,67,53.5,7.08,2,5,9,421,613,35,145.6,-3.3,4.9,1.2,-6.4,17,122,5,96,29,15,14.5,10),
 ("Abdul Samad",55,56,64,67,76,0,50.9,7.47,1,6,9,349,531,22,152.1,10.9,-15.9,-2.2,-12.2,33,48,5,67,10,5,4.0,0),
 ("Basil Hameed",44,52,45,92,32,0,41.7,8.62,0,7,10,109,112,5,102.8,3.1,0.0,-3.2,-13.4,0,12,4,92,3,1,1.2,0),
 ("Faf du Plessis",0,0,19,92,90,48,28.1,9.80,0,9,10,204,302,15,148.0,-25.5,-29.0,-23.3,-34.0,95,55,4,92,17,5,8.2,5),
], columns=["Player","L1","L2","L3","L4","L5","L6","Consensus","ExpRank","Top3","RkLo","RkHi","PressureBalls","Runs","Outs","SR","A","U","Point","L2Score","Comparable","Apps","Seasons","Trust","HighStakes","StakesWins","StakesExp","MoM"])
BAT["BallsPerOut"] = (BAT.PressureBalls / BAT.Outs).round(1)

BOWL = pd.DataFrame([
 ("Rashid Khan",100,100,53,96,100,100,90.6,1.00,100,1,1,1347,94,38.1,17.8,23.6,15.7,61,122,5,96,29,15,14.5,10),
 ("Ravindra Jadeja",42,39,78,85,80,63,60.4,2.63,85,2,4,619,30,1.2,11.9,-2.4,-10.3,53,76,5,85,20,12,8.6,6),
 ("Haider Ali (UAE)",53,49,64,100,34,0,52.3,3.82,47,2,6,81,6,13.4,8.9,8.2,-0.1,7,12,2,100,4,2,1.4,0),
 ("Dwayne Bravo",49,48,73,71,42,0,50.5,4.07,40,2,6,112,9,21.2,-9.2,7.5,1.1,48,10,1,71,1,1,0.4,0),
 ("Piyush Chawla",33,12,97,90,53,0,44.8,4.94,17,3,7,170,11,2.3,-17.4,-8.1,-17.6,52,27,2,90,6,5,2.7,0),
 ("Ishant Sharma",0,4,91,40,38,89,37.7,5.95,7,4,8,127,7,-11.8,0.0,-11.6,-23.6,0,24,3,40,2,2,0.8,2),
 ("Amit Mishra",31,35,31,29,27,0,33.4,6.50,3,5,8,63,4,5.4,-2.7,1.9,-5.9,10,8,2,29,1,0,0.5,0),
 ("Basil Hameed",9,0,45,92,36,0,28.6,7.09,1,5,8,65,2,-16.7,-3.7,-13.2,-19.5,28,12,4,92,3,1,1.2,0),
], columns=["Player","L1","L2","L3","L4","L5","L6","Consensus","ExpRank","Top3","RkLo","RkHi","PressureBalls","Wickets","A","U","Point","L2Score","Comparable","Apps","Seasons","Trust","HighStakes","StakesWins","StakesExp","MoM"])
PROV = [("Pradeep Sangwan", 3, 1, 9, "54 ordinary balls, 3 wickets; no pressure deliveries"),
        ("Muhammad Farooq", 6, 2, 40, "18 ordinary balls, 1 wicket; no pressure deliveries")]
BAT_H2H = [("Kohli > Dhawan",84),("Dhawan > Jadeja",53),("Jadeja > Rohit",57),("Rohit > Dhoni",59),("Dhoni > Karthik",59),("Karthik > Rashid",83),("Rashid > Samad",59),("Samad > Hameed",76),("Hameed > Faf",85)]
BOWL_H2H = [("Rashid > Jadeja",100),("Jadeja > Haider Ali",74),("Haider Ali > Bravo",55),("Bravo > Chawla",66),("Chawla > Ishant",69),("Ishant > Mishra",61),("Mishra > Hameed",63)]
SCEN = pd.DataFrame({"Scenario":["Base","Equal weights","Pressure-model heavy","Stakes-heavy (L3+L6=40%)","No stakes layers","Draft model only","Behavioural model only"],
 "Tau batting":[1,.82,.91,.91,.87,.82,.73],"Tau bowling":[1,.86,.93,.93,.86,.71,.71],
 "Top 3 batting":["Kohli, Dhawan, Jadeja","Kohli, Rohit, Jadeja","Kohli, Dhawan, Jadeja","Kohli, Jadeja, Rohit","Kohli, Dhawan, Jadeja","Dhawan, Kohli, Jadeja","Dhoni, Dhawan, Kohli"],
 "Top 3 bowling":["Rashid, Jadeja, Haider Ali","Rashid, Jadeja, Haider Ali","Rashid, Jadeja, Haider Ali","Rashid, Jadeja, Haider Ali","Rashid, Jadeja, Haider Ali","Rashid, Haider Ali, Bravo","Rashid, Haider Ali, Bravo"]})
TIERS = pd.DataFrame({"Tier":["Low","Medium","High"],"Team-matches":[561,561,562],"Mean MSI":[.045,.121,.256],"Elo expected %":[53.6,51.3,45.2],"Observed win %":[53.8,51.5,44.7],"Close finish %":[16.4,13.4,12.3]})
YEARS = pd.DataFrame({"Year":[2022,2023,2024,2025,2026],"Matches":[180,140,200,217,146]})
MATCHUPS = pd.DataFrame([("Kohli","Rashid Khan",11),("Jadeja","Rashid Khan",10),("Dhoni","Rashid Khan",8),("Rohit","Rashid Khan",8),("Rohit","Jadeja",8),("Kohli","Jadeja",8)],columns=["Batter","Bowler","Co-appearances"])
REC = {"Mahendra Singh Dhoni":(29,39,-6.2,-11.8,-19.2),"Shikhar Dhawan":(30,0,-10.5,0,-17.3),"Dinesh Karthik":(65,38,2.2,-9.6,-29.0),"Virat Kohli":(75,0,15.1,0,-16.8),"Ravindra Jadeja":(110,35,-.3,-11.1,-11.6),"Rashid Khan":(57,45,46.3,.8,-26.7),"Rohit Sharma":(36,23,-6.5,1.6,-39.3),"Abdul Samad":(44,33,-32.9,28.4,-31.5),"Basil Hameed":(0,0,0,0,-48.8),"Faf du Plessis":(40,0,1.2,0,-35.5)}

PLAYER_AVATARS = {
    "Virat Kohli": "https://commons.wikimedia.org/wiki/Special:FilePath/Virat_Kohli_portrait.jpg?width=480",
    "Rohit Sharma": "https://commons.wikimedia.org/wiki/Special:FilePath/Rohit_Gurunath_Sharma.jpg?width=480",
    "Mahendra Singh Dhoni": "https://commons.wikimedia.org/wiki/Special:FilePath/MS_Dhoni.jpg?width=480",
    "Ravindra Jadeja": "https://commons.wikimedia.org/wiki/Special:FilePath/Ravindra_Jadeja.jpg?width=480",
    "Rashid Khan": "https://commons.wikimedia.org/wiki/Special:FilePath/Rashid_Khan.jpg?width=480",
    "Shikhar Dhawan": "https://commons.wikimedia.org/wiki/Special:FilePath/Shikhar_Dhawan.jpg?width=480",
    "Dinesh Karthik": "https://commons.wikimedia.org/wiki/Special:FilePath/Dinesh_Karthik.jpg?width=480",
    "Faf du Plessis": "https://commons.wikimedia.org/wiki/Special:FilePath/Faf_du_Plessis_2019_Boxing_Day.jpg?width=480",
    "Dwayne Bravo": "https://commons.wikimedia.org/wiki/Special:FilePath/Dwayne_Bravo.jpg?width=480",
    "Ishant Sharma": "https://commons.wikimedia.org/wiki/Special:FilePath/Ishant_Sharma.jpg?width=480",
    "Amit Mishra": "https://commons.wikimedia.org/wiki/Special:FilePath/Amit_Mishra.jpg?width=480",
    "Piyush Chawla": "https://commons.wikimedia.org/wiki/Special:FilePath/Piyush_Chawla.jpg?width=480",
    "Abdul Samad": "https://ui-avatars.com/api/?name=Abdul+Samad&background=1A365D&color=fff&size=256&bold=true",
    "Basil Hameed": "https://ui-avatars.com/api/?name=Basil+Hameed&background=087E8B&color=fff&size=256&bold=true",
    "Haider Ali (UAE)": "https://ui-avatars.com/api/?name=Haider+Ali&background=C08A2D&color=fff&size=256&bold=true",
    "Haider Ali (UAE, ID 28756)": "https://ui-avatars.com/api/?name=Haider+Ali&background=C08A2D&color=fff&size=256&bold=true",
    "Pradeep Sangwan": "https://ui-avatars.com/api/?name=Pradeep+Sangwan&background=6E6E73&color=fff&size=256&bold=true",
    "Muhammad Farooq": "https://ui-avatars.com/api/?name=Muhammad+Farooq&background=6E6E73&color=fff&size=256&bold=true",
    "Wriddhiman Saha": "https://commons.wikimedia.org/wiki/Special:FilePath/Wriddhiman_Saha.jpg?width=480",
}

DEFAULT_AVATAR = "https://ui-avatars.com/api/?name=Player&background=1D1D1F&color=fff&size=256&bold=true"



def plot(fig, **kw):
    try:
        st.plotly_chart(fig, use_container_width=True, **kw)
    except TypeError:
        st.plotly_chart(fig, width="stretch", **kw)

def table(df_, **kw):
    data = df_.data.copy() if hasattr(df_, "data") else df_.copy()
    for col in data.select_dtypes(include="number").columns:
        if str(data[col].dtype).startswith("float"):
            data[col] = data[col].round(2)
    try:
        st.dataframe(data, use_container_width=True, **kw)
    except TypeError:
        st.dataframe(data, width="stretch", **kw)

def style(fig, h=420):
    fig.update_layout(
        height=h,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color="#1E293B", size=11),
        margin=dict(l=10, r=20, t=50, b=80),
        legend=dict(orientation="h", y=-0.25, font=dict(size=10, color="#475569"), itemwidth=30),
        hoverlabel=dict(bgcolor="#0F172A", font_size=12, font_color="#FFFFFF", bordercolor="#0F172A")
    )
    fig.update_xaxes(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0", zeroline=False, tickfont=dict(color="#64748B", size=10), automargin=True)
    fig.update_yaxes(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0", zeroline=False, tickfont=dict(color="#64748B", size=10), automargin=True)
    return fig

def kpi(col, label, value):
    col.markdown(f'<div class="card"><div class="kpil">{label}</div><div class="kpi">{value}</div></div>', unsafe_allow_html=True)

def reweight(df, w):
    w = np.array(w, dtype=float); w = w / w.sum() if w.sum() > 0 else np.array(BASE_W)
    out = df.copy(); out["LiveScore"] = (df[["L1","L2","L3","L4","L5","L6"]].values * w).sum(axis=1).round(1)
    out = out.sort_values("LiveScore", ascending=False).reset_index(drop=True); out["LiveRank"] = out.index + 1
    return out

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("### Controls")
    disc = st.radio("Discipline", ["Batters", "Bowlers"], horizontal=True)
    st.markdown("**Layer weights**")
    st.caption("Drag to re-rank live. Weights are normalised.")
    preset = st.selectbox("Preset", ["Base (published)", "Equal weights", "Pressure-model heavy", "Stakes-heavy", "No stakes layers", "Custom"])
    PRE = {"Base (published)": BASE_W, "Equal weights": [1/6]*6, "Pressure-model heavy": [.30,.40,.10,.05,.10,.05],
           "Stakes-heavy": [.15,.20,.20,.05,.10,.30], "No stakes layers": [.25,.40,0,.10,.25,0]}
    start = PRE.get(preset, BASE_W)
    wts = []
    for i, nm in enumerate(LAYERS):
        wts.append(st.slider(nm, 0.0, 1.0, float(round(start[i], 3)), 0.01, key=f"w{i}_{preset}"))
    st.markdown("---")
    st.caption("Data window 22 Jan 2022 - 1 Nov 2026. Candidate pool: 20 dropdown players.")

df = BAT if disc == "Batters" else BOWL
live = reweight(df, wts)

st.markdown('<div class="hero"><h1>Who Delivers When It Matters?</h1><p>SupeRR Selector Season 2 &middot; Pressure beyond the scoreboard &middot; six-layer, stakes-aware ranking of the 20 dropdown players</p></div>', unsafe_allow_html=True)

# KPI row — pure HTML flexbox so it never overflows
st.markdown("""
<div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:14px;">
  <div class="card" style="flex:1; min-width:120px;"><div class="kpil">Matches in pack</div><div class="kpi">883</div></div>
  <div class="card" style="flex:1; min-width:120px;"><div class="kpil">Legal balls analysed</div><div class="kpi">178,850</div></div>
  <div class="card" style="flex:1; min-width:140px;"><div class="kpil">Pressure balls</div><div class="kpi">67,828 <span style="font-size:1rem;font-weight:600;color:#64748B;">(37.9%)</span></div></div>
  <div class="card" style="flex:1; min-width:110px;"><div class="kpil">Simulations</div><div class="kpi">20,000</div></div>
  <div class="card" style="flex:1; min-width:90px;"><div class="kpil">Candidates</div><div class="kpi">20</div></div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["Rankings", "Player profile", "Pressure model", "Stakes pressure", "Robustness", "Matchups", "Data and method"])

# ------------------------------------------------------------------ Rankings
with tabs[0]:
    a, b = st.columns([1.15, 1])
    with a:
        st.subheader(f"Top {len(df)} {disc.lower()} - live weighted score")
        fig = go.Figure()
        d = live.iloc[::-1]
        for i, col in enumerate(["L1","L2","L3","L4","L5","L6"]):
            wn = np.array(wts, float); wn = wn / wn.sum() if wn.sum() > 0 else np.array(BASE_W)
            fig.add_bar(y=d.Player, x=d[col] * wn[i], orientation="h", name=LAYERS[i], marker_color=LCOL[i],
                        hovertemplate="%{y}<br>" + LAYERS[i] + ": %{x:.1f} pts<extra></extra>")
        fig.update_layout(barmode="stack", title="Contribution of each layer to the live score")
        plot(style(fig, 460))
    with b:
        st.subheader("Published consensus vs live order")
        t = live[["LiveRank","Player","LiveScore"]].merge(df[["Player","Consensus","ExpRank","Top3"]], on="Player")
        t["Published rank"] = t["Player"].map({p: i+1 for i, p in enumerate(df.sort_values("ExpRank").Player)})
        t["Move"] = t["Published rank"] - t["LiveRank"]
        t = t.rename(columns={"LiveRank":"Live rank","LiveScore":"Live score","Consensus":"Consensus score","ExpRank":"Exp. rank","Top3":"Top-3 %"})
        table(t[["Live rank","Player","Live score","Published rank","Move","Consensus score","Exp. rank","Top-3 %"]].style.format({"Live score":"{:.1f}","Consensus score":"{:.1f}","Exp. rank":"{:.2f}"}).background_gradient(subset=["Live score"], cmap="Blues"), hide_index=True, height=400)
        st.caption("The published order comes from 20,000 simulations that vary the weights; the live score is a single weighted average, so small differences are expected.")
    st.subheader("Published consensus: expected rank and 10th-90th percentile range")
    s = df.sort_values("ExpRank")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.ExpRank, y=s.Player, mode="markers", marker=dict(size=12, color=BLUE, line=dict(width=2, color="#FFFFFF")),
        error_x=dict(type="data", symmetric=False, array=s.RkHi - s.ExpRank, arrayminus=s.ExpRank - s.RkLo, color="#93C5FD", thickness=2.5, width=4),
        hovertemplate="%{y}<br>Expected rank %{x:.2f}<extra></extra>"))
    fig.update_yaxes(autorange="reversed"); fig.update_xaxes(title="Rank (1 = best)", dtick=1)
    plot(style(fig, 380))
    if disc == "Bowlers":
        st.markdown('<div class="note"><b>Provisional ranks 9-10.</b> Only eight dropdown bowlers have pressure deliveries. '
                    + "; ".join(f"<b>{n}</b>: {note}" for n, _, _, _, note in PROV) + ". They complete the ten slots on ordinary evidence only. "
                    "<b>Haider Ali</b> refers to the UAE spinner (ID 28756), not the Pakistan batter (ID 7338).</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------ Profile
with tabs[1]:
    # Custom selector layout with player image preview
    sel_cols = st.columns([2, 1])
    with sel_cols[0]:
        sel = st.selectbox("Choose a player", list(df.Player), key=f"prof_{disc}")
    
    avatar_url = PLAYER_AVATARS.get(sel, DEFAULT_AVATAR)
    r = df[df.Player == sel].iloc[0]

    # Player Header banner with photo, name & key summary
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 24px; background: white; padding: 20px 24px; border-radius: 16px; box-shadow: 0 2px 10px rgba(15,23,42,0.04); margin-bottom: 20px; border: 1px solid #E2E8F0;">
        <img src="{avatar_url}" style="width: 82px; height: 82px; border-radius: 50%; object-fit: cover; border: 3px solid #2563EB; box-shadow: 0 4px 14px rgba(37,99,235,0.2);" onerror="this.src='{DEFAULT_AVATAR}'" />
        <div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;">{sel}</div>
            <div style="font-size: 0.95rem; color: #64748B;">
                <span style="display: inline-block; background: #EFF6FF; color: #2563EB; border: 1px solid #DBEAFE; padding: 2px 10px; border-radius: 12px; font-weight: 600; margin-right: 8px;">{disc[:-1]}</span>
                Expected Rank: <b style="color:#0F172A;">#{r.ExpRank:.2f}</b> &nbsp;&bull;&nbsp; 
                Consensus Score: <b style="color:#0F172A;">{r.Consensus:.1f}</b> &nbsp;&bull;&nbsp; 
                Pressure Balls: <b style="color:#0F172A;">{int(r.PressureBalls):,}</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 1])
    with left:
        vals = [r.L1, r.L2, r.L3, r.L4, r.L5, r.L6]
        theta = ["L1 Pressure", "L2 Behavioural", "L3 Stakes", "L4 Trust", "L5 Evidence", "L6 Awards"]
        fig = go.Figure(go.Scatterpolar(r=vals + [vals[0]], theta=theta + [theta[0]], fill="toself", line_color=BLUE, fillcolor="rgba(37, 99, 235, 0.16)"))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100], gridcolor="#E2E8F0", tickfont=dict(color="#64748B", size=10)), angularaxis=dict(gridcolor="#E2E8F0", tickfont=dict(color="#1E293B", size=11)), bgcolor="#FFFFFF"),
                          title=f"{sel}: six layer scores (0-100)", showlegend=False)
        fig = style(fig, 440)
        fig.update_layout(margin=dict(t=70, l=90, r=90, b=50))
        plot(fig)
    with right:
        k = st.columns(3)
        kpi(k[0], "Consensus score", f"{r.Consensus:.1f}"); kpi(k[1], "Expected rank", f"{r.ExpRank:.2f}"); kpi(k[2], "Top-3 share", f"{int(r.Top3)}%")
        k = st.columns(3)
        kpi(k[0], "Pressure balls", f"{int(r.PressureBalls):,}"); kpi(k[1], "Appearances", f"{int(r.Apps)}"); kpi(k[2], "Selection trust", f"{int(r.Trust)}%")
        k = st.columns(3)
        kpi(k[0], "High-stakes wins", f"{int(r.StakesWins)} / {int(r.HighStakes)}"); kpi(k[1], "Elo expected", f"{r.StakesExp:.1f}"); kpi(k[2], "Player of the match", f"{int(r.MoM)}")
        if disc == "Batters":
            st.write(f"**{int(r.Runs)} runs, {int(r.Outs)} dismissals, SR {r.SR}, {r.BallsPerOut} balls per dismissal** under pressure.")
            cm = "not in the saved table" if pd.isna(r.Comparable) else f"{int(r.Comparable)}%"
            st.write(f"Comparable ordinary context: **{cm}**. Rank range {int(r.RkLo)}-{int(r.RkHi)} in simulations.")
        else:
            st.write(f"**{int(r.Wickets)} wickets** in {int(r.PressureBalls)} pressure balls. Comparable ordinary context: **{int(r.Comparable)}%**. Rank range {int(r.RkLo)}-{int(r.RkHi)}.")
    if disc == "Batters":
        rc = REC[sel]
        st.subheader("Behavioural diagnostics")
        m = st.columns(5)
        for col, lab, v in zip(m, ["Recovery balls", "Reset balls", "Recovery", "Reset", "Tail"], rc):
            kpi(col, lab, f"{v:g}")

# ------------------------------------------------------------------ Pressure model
with tabs[2]:
    st.subheader("A and U: absolute pressure value and uplift over own ordinary level")
    d = df.sort_values("ExpRank")
    fig = go.Figure()
    fig.add_bar(y=d.Player[::-1], x=d.A[::-1], name="A: absolute value per 100 balls", marker_color=BLUE, orientation="h")
    fig.add_bar(y=d.Player[::-1], x=d.U[::-1], name="U: uplift", marker_color=ORANGE, orientation="h")
    fig.update_layout(barmode="group"); plot(style(fig, 480))
    a, b = st.columns(2)
    with a:
        fig = go.Figure(go.Scatter(x=d.PressureBalls, y=d.L2Score, mode="markers+text", text=d.Player.str.split().str[-1], textposition="top center",
            marker=dict(size=np.clip(d.Comparable.fillna(20) / 3 + 8, 8, 40), color=d.A, colorscale="Blues", showscale=True, colorbar=dict(title="A", tickfont=dict(color="#64748B")), line=dict(width=1.5, color="#1E293B")),
            hovertemplate="%{text}<br>Pressure balls %{x}<br>L2 score %{y:.1f}<extra></extra>"))
        fig.update_layout(title="Evidence vs score (bubble = comparable share)", xaxis_title="Pressure balls", yaxis_title="Conservative L2 score")
        plot(style(fig, 420))
    with b:
        if disc == "Batters":
            rr = pd.DataFrame(REC, index=["Rec balls","Reset balls","Recovery","Reset","Tail"]).T.reset_index().rename(columns={"index":"Player"})
            comp = pd.DataFrame({"Player": rr.Player, "0.55 A": .55*BAT.set_index("Player").loc[rr.Player,"A"].values, "0.20 U": .20*BAT.set_index("Player").loc[rr.Player,"U"].values,
                "0.10 Recovery": .10*rr.Recovery, "0.05 Reset": .05*rr.Reset, "0.10 Tail": .10*rr.Tail})
            fig = go.Figure()
            for cn, cl in zip(comp.columns[1:], [BLUE, ORANGE, INDIGO, GREEN, RED]):
                fig.add_bar(y=comp.Player[::-1], x=comp[cn][::-1], name=cn, marker_color=cl, orientation="h")
            fig.update_layout(barmode="relative", title="What each behavioural point estimate is made of")
            plot(style(fig, 480))
        else:
            fig = go.Figure(go.Bar(y=d.Player[::-1], x=d.L2Score[::-1], orientation="h", marker_color=[GREEN if v > 0 else RED for v in d.L2Score[::-1]]))
            fig.update_layout(title="Conservative L2 score"); plot(style(fig, 420))
    st.markdown('<div class="note">Comparable share is how much of a player\'s pressure play has a fair ordinary comparison. Low values (Dhoni 18%, Karthik 24%, Haider Ali 7%) mean the uplift figure is least reliable for them.</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------ Stakes
with tabs[3]:
    st.subheader("Criterion 4: Stakes Pressure")
    st.latex(r"\mathrm{MSI}=0.35\,K+0.25\,T+0.15\,S+0.15\,O+0.10\,D")
    st.caption("K knockout depth, T table or series squeeze, S losing streak, O strong opponent, D depleted squad. High = top third (MSI >= 0.163), Low = bottom third (< 0.082).")
    a, b, c3 = st.columns(3)
    with a:
        fig = go.Figure(go.Bar(x=TIERS.Tier, y=TIERS["Mean MSI"], marker_color=[GREY, TEAL, BLUE])); fig.update_layout(title="Mean Match Stakes Index")
        plot(style(fig, 330))
    with b:
        fig = go.Figure(); fig.add_bar(x=TIERS.Tier, y=TIERS["Elo expected %"], name="Elo expected", marker_color=INDIGO); fig.add_bar(x=TIERS.Tier, y=TIERS["Observed win %"], name="Observed", marker_color=ORANGE)
        fig.update_layout(barmode="group", title="Win rate (%)"); fig.update_yaxes(range=[40, 56]); plot(style(fig, 330))
    with c3:
        fig = go.Figure(go.Bar(x=TIERS.Tier, y=TIERS["Close finish %"], marker_color=[GREY, TEAL, BLUE])); fig.update_layout(title="Close finishes (%)")
        plot(style(fig, 330))
    st.markdown('<div class="note">High-stakes matches are not closer finishes (12.3% vs 16.4% in Low): Stakes Pressure measures what is riding on the match, not how tight the finish was. Elo Brier score 0.243 vs 0.250 for a coin flip.</div>', unsafe_allow_html=True)
    st.subheader("Team wins in High-stakes matches vs Elo expectation")
    pool = st.radio("List", ["Batters", "Bowlers"], horizontal=True, key="sw")
    sd = (BAT if pool == "Batters" else BOWL).copy(); sd["Diff"] = sd.StakesWins - sd.StakesExp
    fig = go.Figure()
    fig.add_bar(y=sd.Player[::-1], x=sd.StakesWins[::-1], name="Team wins", marker_color=BLUE, orientation="h")
    fig.add_bar(y=sd.Player[::-1], x=sd.StakesExp[::-1], name="Expected wins", marker_color=ORANGE, orientation="h")
    fig.update_layout(barmode="group"); plot(style(fig, 480))
    table(sd[["Player","HighStakes","StakesWins","StakesExp","Diff","MoM"]].rename(columns={"HighStakes":"High-stakes matches","StakesWins":"Wins","StakesExp":"Expected","Diff":"Wins - expected","MoM":"POTM"}).style.format({"Expected":"{:.1f}","Wins - expected":"{:+.1f}"}).background_gradient(subset=["Wins - expected"], cmap="RdYlGn"), hide_index=True)

# ------------------------------------------------------------------ Robustness
with tabs[4]:
    st.subheader("Seven weighting scenarios")
    fig = go.Figure()
    fig.add_bar(y=SCEN.Scenario[::-1], x=SCEN["Tau batting"][::-1], name="Batting", marker_color=BLUE, orientation="h")
    fig.add_bar(y=SCEN.Scenario[::-1], x=SCEN["Tau bowling"][::-1], name="Bowling", marker_color=ORANGE, orientation="h")
    fig.update_layout(barmode="group", xaxis_title="Kendall tau vs base order"); fig.update_xaxes(range=[.5, 1.05]); plot(style(fig, 420))
    table(SCEN, hide_index=True)
    st.subheader("How secure is each adjacent pair?")
    h = BAT_H2H if disc == "Batters" else BOWL_H2H
    hd = pd.DataFrame(h, columns=["Pair", "Higher ahead %"])
    fig = go.Figure(go.Bar(y=hd.Pair[::-1], x=hd["Higher ahead %"][::-1], orientation="h", marker_color=[RED if 45 <= v <= 60 else GREEN for v in hd["Higher ahead %"][::-1]], text=[f"{v}%" for v in hd["Higher ahead %"][::-1]], textposition="outside"))
    fig.add_vline(x=50, line_dash="dash", line_color=GREY); fig.update_xaxes(range=[0, 110]); fig.update_layout(title="Red = near toss-up (45-60%)")
    plot(style(fig, 380))

# ------------------------------------------------------------------ Matchups
with tabs[5]:
    st.subheader("Batter-bowler co-appearances")
    fig = go.Figure(go.Bar(y=(MATCHUPS.Batter + " vs " + MATCHUPS.Bowler)[::-1], x=MATCHUPS["Co-appearances"][::-1], orientation="h", marker_color=TEAL))
    fig.update_layout(xaxis_title="Opposing-team matches both played in (not balls faced)"); plot(style(fig, 360))
    st.markdown('<div class="note">No claim is made that bowlers err more against well-known batters. A valid test needs delivery-level error data and a difference-in-differences design matched on phase, required rate and wickets.</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------ Data & method
with tabs[6]:
    a, b = st.columns(2)
    with a:
        fig = go.Figure(go.Bar(x=YEARS.Year.astype(str), y=YEARS.Matches, marker_color=TEAL, text=YEARS.Matches, textposition="outside")); fig.update_layout(title="Match records per year (883)")
        plot(style(fig, 340))
    with b:
        fig = go.Figure(go.Funnel(y=["Match records", "With delivery data", "Retained after filters"], x=[883, 867, 781], marker=dict(color=[BLUE, INDIGO, TEAL])))
        fig.update_layout(title="Match funnel"); plot(style(fig, 340))
    ap = pd.concat([BAT[["Player","Apps"]], BOWL[["Player","Apps"]]]).drop_duplicates("Player")
    ap = pd.concat([ap, pd.DataFrame({"Player": [p[0] for p in PROV], "Apps": [p[1] for p in PROV]})]).sort_values("Apps")
    fig = go.Figure(go.Bar(y=ap.Player, x=ap.Apps, orientation="h", marker_color=[ORANGE if p in ("Virat Kohli","Mahendra Singh Dhoni","Faf du Plessis") else BLUE for p in ap.Player]))
    fig.update_layout(title="Appearances in the window (context only, not scored)"); plot(style(fig, 520))
    st.markdown("""
**Pressure criteria.** (1) Second-innings chase: required rate 6-18 with at most 36 balls left, or at least 10 after the powerplay, or 4+ wickets down inside 24 balls. (2) First-innings leverage: at most 24 balls left or 4+ wickets down before ball 90. (3) Knockout status. (4) Stakes Pressure: the Match Stakes Index above.

**Layers.** L1 pressure-versus-usual model; L2 behavioural model (recovery, reset, tail, bootstrap); L3 stakes wins above Elo expectation; L4 selection trust; L5 evidence depth; L6 stakes-weighted awards. Base weights 0.22 / 0.32 / 0.16 / 0.08 / 0.12 / 0.10, 20,000 Dirichlet simulations.

**Limits.** Layers 1 and 2 reuse saved results from the ball-by-ball run. Stakes layers use team results and carry 26% of the weight. Wriddhiman Saha is not ranked. Rohit Sharma's comparable share is not in the saved table.
""")
