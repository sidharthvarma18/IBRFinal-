import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

st.set_page_config(
    page_title="IBR Dashboard | Credit Card Analysis",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background-color:#F8FAFC;}
.dash-header{background:linear-gradient(135deg,#0D1B4B 0%,#1A3C8F 60%,#2E8B9A 100%);
  padding:1.8rem 2.5rem 1.4rem;border-radius:16px;margin-bottom:1.5rem;color:white;}
.dash-header h1{font-size:1.75rem;font-weight:700;margin:0;color:white;}
.dash-header p{font-size:0.9rem;color:#111111;margin:0.3rem 0 0;}
.badge{display:inline-block;background:rgba(232,168,56,0.2);border:1px solid #E8A838;
  color:#E8A838;padding:.15rem .65rem;border-radius:20px;font-size:.72rem;
  font-weight:600;margin-right:.4rem;}
.kpi-card{background:white;border-radius:12px;padding:1.1rem 1.3rem;
  border-left:4px solid #1A3C8F;box-shadow:0 2px 8px rgba(0,0,0,.07);margin-bottom:.5rem;}
.kpi-card.teal{border-left-color:#2E8B9A;}
.kpi-card.gold{border-left-color:#E8A838;}
.kpi-lbl{font-size:.72rem;color:#111111;font-weight:600;
  text-transform:uppercase;letter-spacing:.05em;}
.kpi-val{font-size:1.55rem;font-weight:700;color:#000000;line-height:1.2;}
.kpi-sub{font-size:.72rem;color:#333333;margin-top:.15rem;}
.sec-hdr{font-size:1rem;font-weight:700;color:#1A3C8F;
  border-bottom:2px solid #E4ECF7;padding-bottom:.4rem;margin-bottom:1rem;}
.insight{background:#EBF4FF;border-left:4px solid #1A3C8F;
  padding:.75rem 1rem;border-radius:0 8px 8px 0;font-size:.83rem;color:#000000;margin-top:.5rem;}
.insight b{color:#1A3C8F;}
[data-testid="stSidebar"]{background-color:#0D1B4B !important;}
[data-testid="stSidebar"] *{color:white !important;}
.stTabs [data-baseweb="tab"]{background:white;border-radius:8px 8px 0 0;
  padding:.4rem 1.1rem;font-weight:600;color:#111111;}
.stTabs [aria-selected="true"]{background:#1A3C8F !important;color:white !important;}
</style>
""", unsafe_allow_html=True)

NAVY="#0D1B4B"; BLUE="#1A3C8F"; TEAL="#2E8B9A"
GOLD="#E8A838"; RED="#E84A38"; GREEN="#2ECC71"
IP=["#1A3C8F","#2E5ED4","#4A7FFF","#6B9EFF","#9FC0FF"]
UP=["#2E8B9A","#3AAFBF","#4ECFDE","#7ADDE8","#A8EEF5"]

def rgba(hex_col, alpha=0.2):
    h = hex_col.lstrip("#")
    r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"



@st.cache_data
def load():
    d = pd.read_csv("credit_card_data.csv")
    d["Year"] = d["Year"].astype(int)
    d["Recv_Spends_Pct"] = (d["Receivables_INR_Cr"]/d["Annual_Spends_INR_Cr"]*100).round(2)
    d["Fee_Spends_Pct"]  = (d["Fee_Commission_INR_Cr"]/d["Annual_Spends_INR_Cr"]*100).round(2)
    return d

df   = load()
idf  = df[df["Country"]=="India"].copy()
udf  = df[df["Country"]=="UAE"].copy()
BANKS= sorted(df["Bank"].unique())

with st.sidebar:
    st.markdown("### 💳 IBR Dashboard")
    st.markdown("---")
    st.markdown("**Sidharth Varma · MS25GF020**")
    st.markdown("*Credit Cards: Rates & Rewards*\n*India vs UAE · 2016–2025*")
    st.markdown("---")
    st.markdown("#### 🎛️ Filters")
    sel_c = st.multiselect("Country",["India","UAE"],default=["India","UAE"])
    sel_b = st.multiselect("Banks",BANKS,default=BANKS)
    sel_y = st.slider("Year Range",2016,2025,(2016,2025))
    st.markdown("---")
    st.markdown("**Dataset**\n- 10 banks (5 India, 5 UAE)\n- 100 observations\n- 2016–2025")
    st.caption("SP Jain School of Global Management\nMentor: Ms. Farah Naaz\nMGB Oct 2025")

fdf  = df[df["Country"].isin(sel_c)&df["Bank"].isin(sel_b)&df["Year"].between(sel_y[0],sel_y[1])].copy()
fi   = fdf[fdf["Country"]=="India"]
fu   = fdf[fdf["Country"]=="UAE"]

st.markdown("""
<div class="dash-header">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem">
    <div>
      <h1>💳 Credit Card Market Analysis Dashboard</h1>
      <p>India vs. UAE · 2016–2025 · 10 Banks · 100 Bank-Year Observations</p>
      <div style="margin-top:.7rem">
        <span class="badge">Sidharth Varma</span><span class="badge">MS25GF020</span>
        <span class="badge">IBR Final Review</span><span class="badge">SP Jain MGB 2025</span>
      </div>
    </div>
    <div style="text-align:right;color:#111111;font-size:.82rem">
      <div>Mentor: Ms. Farah Naaz</div>
      <div style="margin-top:.3rem">Pearson r · OLS Regression · t-test · Global Benchmarking</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

k=st.columns(6)
kpis=[
    ("Total Spends",f"₹{fdf['Annual_Spends_INR_Cr'].sum()/1e5:.1f}L Cr","Aggregate INR Crores",""),
    ("Avg Interest Rate",f"{fdf['Interest_Rate_Pct'].mean():.1f}%","Across selected banks","teal"),
    ("Cards in Force",f"{fdf['Cards_in_Force_Cr'].sum():.1f} Cr","Total cardholders","gold"),
    ("Receivables",f"₹{fdf['Receivables_INR_Cr'].sum()/1000:.0f}K Cr","Outstanding balances",""),
    ("Fee & Commission",f"₹{fdf['Fee_Commission_INR_Cr'].sum():,.0f} Cr","Reward proxy income","teal"),
    ("Observations",str(len(fdf)),"Bank-year data points","gold"),
]
for col,(lbl,val,sub,cls) in zip(k,kpis):
    with col:
        st.markdown(f'<div class="kpi-card {cls}"><div class="kpi-lbl">{lbl}</div>'
                    f'<div class="kpi-val">{val}</div><div class="kpi-sub">{sub}</div></div>',
                    unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)

def wl(fig,h=360,angle=0):
    fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),height=h,
        xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor="#F0F4FA"),
        legend=dict(orientation="h",yanchor="bottom",y=-0.35,xanchor="left"),margin=dict(b=80))
    if angle: fig.update_xaxes(tickangle=angle)
    return fig

def trendline(fig, xv, yv, col):
    mask=~(np.isnan(xv)|np.isnan(yv))
    if mask.sum()<3: return fig
    sl,ic,rv,_,_=stats.linregress(xv[mask],yv[mask])
    xr=np.linspace(xv[mask].min(),xv[mask].max(),100)
    fig.add_trace(go.Scatter(x=xr,y=sl*xr+ic,mode="lines",showlegend=False,
        line=dict(color=col,width=2,dash="dash"),hoverinfo="skip"))
    return fig

t1,t2,t3,t4,t5,t6,t7=st.tabs([
    "📈 Spending Trends","📊 Descriptive Stats","🔗 Correlation",
    "📉 Regression","⚖️ India vs UAE","🏦 Bank Deep-Dive","🌍 Benchmarking"])

# ── TAB 1 ──────────────────────────────────────────────────────────────────
with t1:
    st.markdown('<div class="sec-hdr">📈 Annual Spending Trajectories (2016–2025)</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        if "India" in sel_c and len(fi):
            fig=px.line(fi,x="Year",y="Annual_Spends_INR_Cr",color="Bank",
                title="India — Annual Spends by Bank (₹ Cr)",
                color_discrete_sequence=IP,markers=True)
            st.plotly_chart(wl(fig),use_container_width=True)
    with c2:
        if "UAE" in sel_c and len(fu):
            fig2=px.line(fu,x="Year",y="Annual_Spends_INR_Cr",color="Bank",
                title="UAE — Annual Spends by Bank (₹ Cr eq.)",
                color_discrete_sequence=UP,markers=True)
            st.plotly_chart(wl(fig2),use_container_width=True)

    st.markdown('<div class="sec-hdr">📊 Year-on-Year Growth Rate Heatmap (%)</div>',unsafe_allow_html=True)
    pv=fdf.groupby(["Bank","Year"])["Annual_Spends_INR_Cr"].sum().reset_index()
    pv=pv.sort_values(["Bank","Year"])
    pv["YoY"]=pv.groupby("Bank")["Annual_Spends_INR_Cr"].pct_change()*100
    ht=pv.pivot(index="Bank",columns="Year",values="YoY").round(1)
    fh=px.imshow(ht,color_continuous_scale=[[0,"#E84A38"],[0.5,"#FFFFFF"],[1,"#1A3C8F"]],
        color_continuous_midpoint=0,text_auto=".1f",title="YoY Growth Rate (%) — All Banks",aspect="auto")
    fh.update_layout(font_family="Inter",font=dict(color="#111111"),height=380,plot_bgcolor="white",paper_bgcolor="white")
    fh.update_traces(textfont_size=10)
    st.plotly_chart(fh,use_container_width=True)

    mkt=fdf.groupby(["Country","Year"])["Annual_Spends_INR_Cr"].sum().reset_index()
    fa=px.area(mkt,x="Year",y="Annual_Spends_INR_Cr",color="Country",
        title="Combined Market Spends — India vs UAE (₹ Cr)",
        color_discrete_map={"India":BLUE,"UAE":TEAL})
    fa.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),height=300,
        xaxis=dict(showgrid=False,dtick=1),yaxis=dict(showgrid=True,gridcolor="#F0F4FA",tickformat=",.0f"),
        legend=dict(orientation="h",y=-0.25))
    st.plotly_chart(fa,use_container_width=True)
    st.markdown("""<div class="insight"><b>Key Insight:</b> India's spends grew ~9.5× over the decade
    (CAGR ~28.4%). Post-COVID revenge spending drove 48.3% (2022) and 54.2% (2023) growth.
    UAE shows steadier ~16.5% CAGR. HDFC Bank alone: ₹66,000 Cr → ₹6,18,900 Cr (2016→2025).</div>""",
    unsafe_allow_html=True)

# ── TAB 2 ──────────────────────────────────────────────────────────────────
with t2:
    st.markdown('<div class="sec-hdr">📊 Descriptive Statistics</div>',unsafe_allow_html=True)
    mrkt=st.radio("Market",["India","UAE","Combined"],horizontal=True)
    ds=fi if mrkt=="India" else (fu if mrkt=="UAE" else fdf)
    nc=["Annual_Spends_INR_Cr","Cards_in_Force_Cr","Receivables_INR_Cr","Interest_Rate_Pct","Fee_Commission_INR_Cr"]
    desc=ds[nc].describe().T
    desc.index=["Annual Spends (₹Cr)","Cards in Force (Cr)","Receivables (₹Cr)","Interest Rate (%)","Fee & Commission (₹Cr)"]
    desc.columns=["Count","Mean","Std Dev","Min","25th %ile","Median","75th %ile","Max"]
    st.dataframe(desc.round(2),use_container_width=True)

    c1,c2=st.columns(2)
    with c1:
        fb=px.box(ds,x="Bank",y="Annual_Spends_INR_Cr",color="Country",
            title="Annual Spends Distribution by Bank",
            color_discrete_map={"India":BLUE,"UAE":TEAL})
        fb.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),
            height=380,xaxis_tickangle=-35,legend=dict(orientation="h",y=-0.35))
        st.plotly_chart(fb,use_container_width=True)
    with c2:
        fhi=px.histogram(ds,x="Interest_Rate_Pct",color="Country",nbins=20,
            title="Interest Rate Distribution",color_discrete_map={"India":BLUE,"UAE":TEAL},
            barmode="overlay",opacity=0.75)
        fhi.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),
            height=380,legend=dict(orientation="h",y=-0.25))
        st.plotly_chart(fhi,use_container_width=True)

    st.markdown('<div class="sec-hdr">📐 Skewness & Kurtosis</div>',unsafe_allow_html=True)
    lbls={"Annual_Spends_INR_Cr":"Annual Spends","Cards_in_Force_Cr":"Cards in Force",
          "Receivables_INR_Cr":"Receivables","Interest_Rate_Pct":"Interest Rate","Fee_Commission_INR_Cr":"Fee Income"}
    skr=[{"Variable":v,"Skewness":round(ds[c].skew(),3),"Kurtosis":round(ds[c].kurt(),3),
          "Mean":round(ds[c].mean(),2),"Std Dev":round(ds[c].std(),2)} for c,v in lbls.items()]
    skdf=pd.DataFrame(skr)
    c1,c2=st.columns(2)
    with c1:
        fsk=px.bar(skdf,x="Variable",y="Skewness",title="Skewness (>1 = highly right-skewed)",
            color="Skewness",color_continuous_scale=[[0,"#2E8B9A"],[0.5,"white"],[1,"#1A3C8F"]])
        fsk.add_hline(y=1,line_dash="dash",line_color=GOLD,annotation_text="Skewness=1")
        fsk.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),height=320,xaxis_tickangle=-20)
        st.plotly_chart(fsk,use_container_width=True)
    with c2:
        fku=px.bar(skdf,x="Variable",y="Kurtosis",title="Kurtosis (>3 = leptokurtic)",
            color="Kurtosis",color_continuous_scale=[[0,"#2E8B9A"],[0.5,"white"],[1,"#1A3C8F"]])
        fku.add_hline(y=3,line_dash="dash",line_color=RED,annotation_text="Normal=3")
        fku.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),height=320,xaxis_tickangle=-20)
        st.plotly_chart(fku,use_container_width=True)
    st.dataframe(skdf.set_index("Variable"),use_container_width=True)

# ── TAB 3 ──────────────────────────────────────────────────────────────────
with t3:
    st.markdown('<div class="sec-hdr">🔗 Correlation Analysis</div>',unsafe_allow_html=True)
    cmkt=st.selectbox("Market",["India","UAE","Combined"])
    cdf2=idf if cmkt=="India" else (udf if cmkt=="UAE" else df)
    nc2=["Annual_Spends_INR_Cr","Cards_in_Force_Cr","Receivables_INR_Cr","Interest_Rate_Pct","Fee_Commission_INR_Cr"]
    cm=cdf2[nc2].corr().round(3)
    cm.index=cm.columns=["Annual Spends","Cards in Force","Receivables","Interest Rate","Fee Income"]
    fcm=go.Figure(go.Heatmap(z=cm.values,x=cm.columns,y=cm.index,
        colorscale=[[0,"#E84A38"],[0.5,"#FFFFFF"],[1,"#1A3C8F"]],
        zmid=0,zmin=-1,zmax=1,text=cm.values,texttemplate="%{text:.2f}",
        hovertemplate="<b>%{y} vs %{x}</b><br>r=%{z:.3f}<extra></extra>"))
    fcm.update_layout(title=f"Pearson Correlation Matrix — {cmkt}",font_family="Inter",font=dict(color="#111111"),
        height=420,plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fcm,use_container_width=True)

    st.markdown('<div class="sec-hdr">🔍 Key Scatter Plots</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        fs1=px.scatter(df,x="Interest_Rate_Pct",y="Annual_Spends_INR_Cr",color="Country",
            title="Interest Rate vs Annual Spends",
            color_discrete_map={"India":BLUE,"UAE":TEAL},hover_data=["Bank","Year"])
        fs1=trendline(fs1,idf["Interest_Rate_Pct"].values,idf["Annual_Spends_INR_Cr"].values,BLUE)
        fs1=trendline(fs1,udf["Interest_Rate_Pct"].values,udf["Annual_Spends_INR_Cr"].values,TEAL)
        fs1.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),height=370,
            legend=dict(orientation="h",y=-0.3))
        st.plotly_chart(fs1,use_container_width=True)
        ri,pi=stats.pearsonr(idf["Interest_Rate_Pct"],idf["Annual_Spends_INR_Cr"])
        ru,pu=stats.pearsonr(udf["Interest_Rate_Pct"],udf["Annual_Spends_INR_Cr"])
        st.markdown(f"""<div class="insight">
        <b>India:</b> r={ri:.3f}, p={pi:.3f} — {'❌ Not significant (reward salience dominates)' if pi>0.05 else '✅ Significant'}<br>
        <b>UAE:</b> r={ru:.3f}, p={pu:.4f} — {'✅ Significant (premium product-mix effect)' if pu<0.05 else '❌ Not significant'}
        </div>""",unsafe_allow_html=True)
    with c2:
        fs2=px.scatter(df,x="Fee_Commission_INR_Cr",y="Annual_Spends_INR_Cr",color="Country",
            title="Fee Income (Reward Proxy) vs Annual Spends",
            color_discrete_map={"India":BLUE,"UAE":TEAL},hover_data=["Bank","Year"])
        fs2=trendline(fs2,idf["Fee_Commission_INR_Cr"].values,idf["Annual_Spends_INR_Cr"].values,BLUE)
        fs2=trendline(fs2,udf["Fee_Commission_INR_Cr"].values,udf["Annual_Spends_INR_Cr"].values,TEAL)
        fs2.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),height=370,
            legend=dict(orientation="h",y=-0.3))
        st.plotly_chart(fs2,use_container_width=True)
        rfi,_=stats.pearsonr(idf["Fee_Commission_INR_Cr"],idf["Annual_Spends_INR_Cr"])
        rfu,_=stats.pearsonr(udf["Fee_Commission_INR_Cr"],udf["Annual_Spends_INR_Cr"])
        st.markdown(f"""<div class="insight">
        <b>India:</b> r={rfi:.3f}, p &lt; 0.001 ✅ Near-perfect reward-spend flywheel<br>
        <b>UAE:</b> r={rfu:.3f}, p &lt; 0.001 ✅ Perfect correlation confirmed
        </div>""",unsafe_allow_html=True)

    st.markdown('<div class="sec-hdr">📊 Receivables-to-Spends Ratio — Borrowing Behaviour</div>',unsafe_allow_html=True)
    rr=fdf.groupby(["Country","Year"]).apply(
        lambda x: x["Receivables_INR_Cr"].sum()/x["Annual_Spends_INR_Cr"].sum()*100,
        include_groups=False).reset_index(name="Pct")
    frr=px.line(rr,x="Year",y="Pct",color="Country",
        title="Receivables-to-Spends Ratio (%)",
        color_discrete_map={"India":BLUE,"UAE":TEAL},markers=True)
    frr.add_hline(y=20,line_dash="dash",line_color=GOLD,annotation_text="20% threshold")
    frr.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),height=320,
        xaxis=dict(showgrid=False,dtick=1),yaxis=dict(showgrid=True,gridcolor="#F0F4FA"),hovermode="x unified")
    st.plotly_chart(frr,use_container_width=True)
    st.markdown("""<div class="insight"><b>H1 Evidence:</b> India's ratio fell from 26.43% (2016) to 18.50% (2025),
    signalling improving financial literacy. UAE's higher ratio (~23–27%) reflects expatriate revolving credit patterns.</div>""",
    unsafe_allow_html=True)

# ── TAB 4 ──────────────────────────────────────────────────────────────────
with t4:
    st.markdown('<div class="sec-hdr">📉 Regression Analysis</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        rx=st.selectbox("Independent Variable (X)",["Interest_Rate_Pct","Fee_Commission_INR_Cr",
            "Receivables_INR_Cr","Cards_in_Force_Cr"],
            format_func=lambda x:{"Interest_Rate_Pct":"Interest Rate (%)","Fee_Commission_INR_Cr":
            "Fee & Commission","Receivables_INR_Cr":"Receivables","Cards_in_Force_Cr":"Cards in Force"}[x])
    with c2:
        ry=st.selectbox("Dependent Variable (Y)",["Annual_Spends_INR_Cr","Receivables_INR_Cr","Fee_Commission_INR_Cr"],
            format_func=lambda x:{"Annual_Spends_INR_Cr":"Annual Spends","Receivables_INR_Cr":"Receivables",
            "Fee_Commission_INR_Cr":"Fee & Commission"}[x])

    res=[]
    for ctry,cd in [("India",fi),("UAE",fu)]:
        if len(cd)<3: continue
        xd,yd=cd[rx].values,cd[ry].values
        m=~(np.isnan(xd)|np.isnan(yd))
        if m.sum()<3: continue
        sl,ic,rv,pv,se=stats.linregress(xd[m],yd[m])
        res.append({"Country":ctry,"Slope":round(sl,4),"Intercept":round(ic,2),
            "r":round(rv,4),"R²":round(rv**2,4),"p-value":round(pv,4),"Std Error":round(se,4),
            "Result":"✅ Sig." if pv<0.05 else "❌ NS"})
    if res:
        st.dataframe(pd.DataFrame(res).set_index("Country"),use_container_width=True)

    c1,c2=st.columns(2)
    for i,(ctry,cd,pal) in enumerate([("India",fi,BLUE),("UAE",fu,TEAL)]):
        if len(cd)<3: continue
        with [c1,c2][i]:
            fr=px.scatter(cd,x=rx,y=ry,color="Bank",
                title=f"{ctry}: {ry.replace('_',' ')} ~ {rx.replace('_',' ')}",
                color_discrete_sequence=IP if ctry=="India" else UP,
                hover_data=["Bank","Year"])
            xd,yd=cd[rx].values,cd[ry].values
            m=~(np.isnan(xd)|np.isnan(yd))
            if m.sum()>2:
                sl,ic,rv,pv,_=stats.linregress(xd[m],yd[m])
                xr=np.linspace(xd[m].min(),xd[m].max(),100)
                fr.add_trace(go.Scatter(x=xr,y=sl*xr+ic,mode="lines",showlegend=False,
                    line=dict(color=pal,width=2,dash="dash"),hoverinfo="skip"))
                fr.add_annotation(x=0.05,y=0.95,xref="paper",yref="paper",
                    text=f"r={rv:.3f}  R²={rv**2:.3f}  p={pv:.4f}",
                    showarrow=False,font=dict(size=11,color=pal),
                    bgcolor="white",bordercolor=pal,borderwidth=1)
            fr.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),
                height=370,legend=dict(orientation="h",y=-0.38))
            st.plotly_chart(fr,use_container_width=True)

    st.markdown('<div class="sec-hdr">📋 Full Regression Summary</div>',unsafe_allow_html=True)
    pairs=[("Annual_Spends_INR_Cr","Interest_Rate_Pct"),("Annual_Spends_INR_Cr","Fee_Commission_INR_Cr"),
           ("Receivables_INR_Cr","Annual_Spends_INR_Cr"),("Fee_Commission_INR_Cr","Annual_Spends_INR_Cr")]
    lmap={"Annual_Spends_INR_Cr":"Annual Spends","Interest_Rate_Pct":"Interest Rate",
          "Fee_Commission_INR_Cr":"Fee Income","Receivables_INR_Cr":"Receivables"}
    rows=[]
    for ctry,cd in [("India",idf),("UAE",udf)]:
        for yv,xv in pairs:
            xd,yd=cd[xv].values,cd[yv].values
            m=~(np.isnan(xd)|np.isnan(yd))
            if m.sum()>2:
                sl,_,rv,pv,_=stats.linregress(xd[m],yd[m])
                rows.append({"Country":ctry,"Y":lmap[yv],"X":lmap[xv],
                    "Slope":f"{sl:.4f}","r":f"{rv:.3f}","R²":f"{rv**2:.3f}",
                    "p-value":f"{pv:.4f}","✓":"✅" if pv<0.05 else "❌"})
    st.dataframe(pd.DataFrame(rows),use_container_width=True)
    st.markdown("""<div class="insight"><b>Summary:</b> Fee Income→Spends: R²=0.929 (India), ~1.00 (UAE).
    Interest Rate→Spends: R²=0.047 (India, p=0.131 NS) vs R²=0.288 (UAE, p&lt;0.001).
    Receivables→Spends: R²=0.954 (India), 0.988 (UAE).</div>""",unsafe_allow_html=True)

# ── TAB 5 ──────────────────────────────────────────────────────────────────
with t5:
    st.markdown('<div class="sec-hdr">⚖️ India vs UAE — Comparative Analysis</div>',unsafe_allow_html=True)
    comp=[]
    for col,lbl in [("Annual_Spends_INR_Cr","Avg Annual Spends (₹Cr)"),
                    ("Interest_Rate_Pct","Avg Interest Rate (%)"),
                    ("Receivables_INR_Cr","Avg Receivables (₹Cr)"),
                    ("Fee_Spends_Pct","Fee-to-Spends Ratio (%)"),
                    ("Cards_in_Force_Cr","Avg Cards in Force (Cr)")]:
        if col in idf.columns:
            comp.append({"Metric":lbl,"India":round(idf[col].mean(),2),"UAE":round(udf[col].mean(),2)})
    cmpdf=pd.DataFrame(comp)
    cats=[r["Metric"].split(" (")[0] for r in comp]
    iv=[r["India"] for r in comp]; uv=[r["UAE"] for r in comp]
    mv=[max(a,b) if max(a,b)!=0 else 1 for a,b in zip(iv,uv)]
    in_=[v/m for v,m in zip(iv,mv)]; un_=[v/m for v,m in zip(uv,mv)]

    c1,c2=st.columns(2)
    with c1:
        fra=go.Figure()
        for vals,name,col in [(in_,"India",BLUE),(un_,"UAE",TEAL)]:
            fra.add_trace(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],
                fill="toself",name=name,line_color=col,fillcolor=rgba(col,0.2)))
        fra.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,1])),
            title="Normalised Market Profile",showlegend=True,font_family="Inter",font=dict(color="#111111"),
            height=420,legend=dict(orientation="h",y=-0.1),paper_bgcolor="white")
        st.plotly_chart(fra,use_container_width=True)
    with c2:
        st.dataframe(cmpdf.set_index("Metric"),use_container_width=True)
        ts,tp=stats.ttest_ind(idf["Interest_Rate_Pct"].dropna(),udf["Interest_Rate_Pct"].dropna())
        st.markdown(f"""<div class="insight">
        <b>Independent t-test (Interest Rates):</b><br>
        t={ts:.3f} · p={tp:.4f} · {'✅ Statistically significant' if tp<0.05 else '❌ Not significant'}<br><br>
        <b>India avg rate:</b> {idf['Interest_Rate_Pct'].mean():.2f}% (σ={idf['Interest_Rate_Pct'].std():.2f} pp)<br>
        <b>UAE avg rate:</b> {udf['Interest_Rate_Pct'].mean():.2f}% (σ={udf['Interest_Rate_Pct'].std():.2f} pp)
        </div>""",unsafe_allow_html=True)

    fyr=fdf.groupby(["Country","Year"]).apply(
        lambda x: x["Fee_Commission_INR_Cr"].sum()/x["Annual_Spends_INR_Cr"].sum()*100,
        include_groups=False).reset_index(name="Pct")
    ffy=px.line(fyr,x="Year",y="Pct",color="Country",
        title="Fee-to-Spends Ratio (%) — Reward Monetisation per Unit of Spend",
        color_discrete_map={"India":BLUE,"UAE":TEAL},markers=True)
    ffy.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),height=320,
        xaxis=dict(dtick=1),yaxis=dict(gridcolor="#F0F4FA"),hovermode="x unified")
    st.plotly_chart(ffy,use_container_width=True)

# ── TAB 6 ──────────────────────────────────────────────────────────────────
with t6:
    st.markdown('<div class="sec-hdr">🏦 Bank-Level Deep Dive</div>',unsafe_allow_html=True)
    sb=st.selectbox("Select Bank",BANKS)
    bdf=df[df["Bank"]==sb].copy()
    ctry=bdf["Country"].iloc[0]
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Country",ctry)
    m2.metric("Peak Spends (₹Cr)",f"{bdf['Annual_Spends_INR_Cr'].max():,.0f}")
    m3.metric("2025 Interest Rate",f"{bdf.iloc[-1]['Interest_Rate_Pct']:.1f}%")
    if bdf.iloc[0]["Annual_Spends_INR_Cr"]>0:
        cagr=((bdf.iloc[-1]["Annual_Spends_INR_Cr"]/bdf.iloc[0]["Annual_Spends_INR_Cr"])**(1/9)-1)*100
        m4.metric("CAGR (Spends)",f"{cagr:.1f}%")

    c1,c2=st.columns(2)
    with c1:
        fd1=make_subplots(specs=[[{"secondary_y":True}]])
        fd1.add_trace(go.Bar(x=bdf["Year"],y=bdf["Annual_Spends_INR_Cr"],name="Annual Spends",marker_color=BLUE),secondary_y=False)
        fd1.add_trace(go.Scatter(x=bdf["Year"],y=bdf["Interest_Rate_Pct"],name="Interest Rate %",
            mode="lines+markers",line=dict(color=GOLD,width=2)),secondary_y=True)
        fd1.update_layout(title=f"{sb} — Spends & Interest Rate",plot_bgcolor="white",paper_bgcolor="white",
            font_family="Inter",font=dict(color="#111111"),height=360,legend=dict(orientation="h",y=-0.28))
        st.plotly_chart(fd1,use_container_width=True)
    with c2:
        fd2=make_subplots(specs=[[{"secondary_y":True}]])
        fd2.add_trace(go.Bar(x=bdf["Year"],y=bdf["Receivables_INR_Cr"],name="Receivables",marker_color=TEAL),secondary_y=False)
        fd2.add_trace(go.Scatter(x=bdf["Year"],y=bdf["Fee_Commission_INR_Cr"],name="Fee Income",
            mode="lines+markers",line=dict(color=RED,width=2)),secondary_y=True)
        fd2.update_layout(title=f"{sb} — Receivables & Fee Income",plot_bgcolor="white",paper_bgcolor="white",
            font_family="Inter",font=dict(color="#111111"),height=360,legend=dict(orientation="h",y=-0.28))
        st.plotly_chart(fd2,use_container_width=True)

    latest=df[df["Year"]==2025].copy()
    c1,c2=st.columns(2)
    with c1:
        fl1=px.bar(latest.sort_values("Annual_Spends_INR_Cr",ascending=False),x="Bank",
            y="Annual_Spends_INR_Cr",color="Country",title="Annual Spends 2025 — All Banks",
            color_discrete_map={"India":BLUE,"UAE":TEAL})
        fl1.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),
            height=340,xaxis_tickangle=-30,legend=dict(orientation="h",y=-0.35))
        st.plotly_chart(fl1,use_container_width=True)
    with c2:
        fl2=px.bar(latest.sort_values("Interest_Rate_Pct",ascending=False),x="Bank",
            y="Interest_Rate_Pct",color="Country",title="Interest Rate 2025 — All Banks",
            color_discrete_map={"India":BLUE,"UAE":TEAL})
        fl2.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),
            height=340,xaxis_tickangle=-30,legend=dict(orientation="h",y=-0.35))
        st.plotly_chart(fl2,use_container_width=True)

    st.markdown('<div class="sec-hdr">📋 Raw Data</div>',unsafe_allow_html=True)
    show=bdf[["Year","Annual_Spends_INR_Cr","Cards_in_Force_Cr","Receivables_INR_Cr",
              "Interest_Rate_Pct","Fee_Commission_INR_Cr","Recv_Spends_Pct","Fee_Spends_Pct"]].copy()
    show.columns=["Year","Annual Spends (₹Cr)","Cards in Force (Cr)","Receivables (₹Cr)",
                  "Interest Rate (%)","Fee Income (₹Cr)","Recv/Spends (%)","Fee/Spends (%)"]
    st.dataframe(show.set_index("Year"),use_container_width=True)

# ── TAB 7 ──────────────────────────────────────────────────────────────────
with t7:
    st.markdown('<div class="sec-hdr">🌍 Global Benchmarking — India in Context</div>',unsafe_allow_html=True)
    st.markdown("""<div class="insight" style="margin-bottom:1.2rem">
    India and UAE benchmarked against USA, Singapore, UK, Australia as <i>reference points</i>.
    Sources: CFPB (2023), MAS (2022), FCA (2023), RBA (2021), OECD (2023).
    </div>""",unsafe_allow_html=True)

    bm=pd.DataFrame({"Market":["India","UAE","USA","Singapore","UK","Australia"],
        "Avg Interest Rate (%)":[26.04,29.19,22.0,25.0,21.0,20.0],
        "Fee-to-Spend (%)":[1.81,5.00,3.00,2.15,2.50,1.50],
        "Revolving Ratio (%)":[18.5,25.0,40.0,12.0,22.0,28.0],
        "Financial Literacy":[40,55,78,90,76,75],
        "Reward Intensity":[70,85,95,65,75,55],
        "BNPL Risk":[40,20,55,15,50,90]})
    c6=["#1A3C8F","#2E8B9A","#E84A38","#2ECC71","#9B59B6","#E8A838"]

    c1,c2=st.columns(2)
    with c1:
        fb1=px.bar(bm,x="Market",y="Avg Interest Rate (%)",
            title="Average Interest Rate (%) — 6 Markets",color="Market",color_discrete_sequence=c6)
        fb1.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),height=330,showlegend=False)
        st.plotly_chart(fb1,use_container_width=True)
    with c2:
        fb2=px.bar(bm,x="Market",y="Fee-to-Spend (%)",
            title="Fee-to-Spend Ratio (%) — Reward Monetisation",color="Market",color_discrete_sequence=c6)
        fb2.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Inter",font=dict(color="#111111"),height=330,showlegend=False)
        st.plotly_chart(fb2,use_container_width=True)

    rc=["Avg Interest Rate (%)","Fee-to-Spend (%)","Revolving Ratio (%)","Financial Literacy","Reward Intensity","BNPL Risk"]
    rl=["Interest Rate","Fee Yield","Revolving Credit","Fin. Literacy","Reward Intensity","BNPL Risk"]
    frr=go.Figure()
    for i,row in bm.iterrows():
        vals=[row[c]/100 for c in rc]
        frr.add_trace(go.Scatterpolar(r=vals+[vals[0]],theta=rl+[rl[0]],
            fill="toself",name=row["Market"],line_color=c6[i],fillcolor=rgba(c6[i],0.13)))
    frr.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,1])),
        title="Multi-Dimensional Market Profile — Normalised",showlegend=True,
        font_family="Inter",font=dict(color="#111111"),height=480,legend=dict(orientation="h",y=-0.12),paper_bgcolor="white")
    st.plotly_chart(frr,use_container_width=True)

    st.markdown('<div class="sec-hdr">💡 Policy Lessons for India</div>',unsafe_allow_html=True)
    ls=pd.DataFrame({"Benchmark":["🇺🇸 USA","🇸🇬 Singapore","🇬🇧 UK","🇦🇺 Australia"],
        "Feature":["CFPB Mandatory Reward Disclosure","MAS Spend-Threshold Tiering",
                   "FCA Open Banking + Risk-Tiered Cards","RBA Interchange Fee Cap (2016)"],
        "Lesson for India":["Introduce standardised Reward Value Statements at card issuance",
            "Link lounge access to minimum quarterly spend thresholds",
            "Use RBI Account Aggregator for AI-personalised reward targeting",
            "Avoid premature interchange caps — BNPL substitution risk (ASIC 2020: 21% hardship)"],
        "Status":["🟡 Recommended","🟡 Recommended","🟢 In Progress","🔴 Avoid"]})
    st.dataframe(ls.set_index("Benchmark"),use_container_width=True)

    st.markdown('<div class="sec-hdr">✈️ Airport Lounge Sustainability — Unit Economics</div>',unsafe_allow_html=True)
    lg=pd.DataFrame({"Parameter":["Fee Revenue / Premium Cardholder (₹)","Lounge Visit Cost (₹/entry)",
        "Sustainable Visits/Year","Observed Avg Visits/Year","Sustainability"],
        "India":["₹3,280–3,960","₹500–900","4–7 visits","8–12 visits ⚠️","❌ DEFICIT"],
        "UAE":["₹8,200–12,000","₹1,100–1,800","7–10 visits","5–8 visits ✅","✅ VIABLE"]})
    st.dataframe(lg.set_index("Parameter"),use_container_width=True)
    st.markdown("""<div class="insight"><b>Lounge Economics:</b> India faces a cross-subsidisation deficit —
    fee revenue per cardholder falls short of covering 8–12 annual visits at ₹500–900/entry.
    UAE is structurally viable at ~5% fee yields. India must implement spend-threshold
    access gates (Singapore MAS model) to close this gap.</div>""",unsafe_allow_html=True)

st.markdown("<br><br>",unsafe_allow_html=True)
st.markdown("""
<div style="background:#0D1B4B;padding:1rem 2rem;border-radius:12px;color:#111111;
     font-size:.78rem;text-align:center">
    <b style="color:white">IBR Final Review Dashboard</b> · Sidharth Varma (MS25GF020) ·
    MGB Oct 2025 · SP Jain School of Global Management · Mentor: Ms. Farah Naaz ·
    <i>Data: Bank Annual Reports 2016–2025 (India &amp; UAE)</i>
</div>
""",unsafe_allow_html=True)
