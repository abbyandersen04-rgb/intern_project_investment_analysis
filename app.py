import streamlit as st
import anthropic
import plotly.graph_objects as go

st.set_page_config(
    page_title="Macro Economic Sensitivity Analyzer",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card { background: #f8f9fa; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 0.5rem; }
    .impact-pos { color: #1D9E75; font-weight: 600; }
    .impact-neg { color: #E24B4A; font-weight: 600; }
    .section-header { font-size: 0.75rem; font-weight: 600; color: #888; text-transform: uppercase;
                      letter-spacing: 0.08em; margin-top: 1.5rem; margin-bottom: 0.5rem; }
    .ai-box { background: #f0f4ff; border-left: 3px solid #378ADD; border-radius: 6px;
               padding: 1.25rem; margin-top: 0.5rem; font-size: 0.95rem; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Macro Economic Sensitivity Analyzer")
st.caption("Model how macroeconomic shifts impact your business P&L — powered by AI analysis")

# ── Sidebar: Business Profile ─────────────────────────────────────────────────
with st.sidebar:
    st.header("Business Profile")

    revenue = st.number_input("Annual revenue ($M)", min_value=1.0, value=50.0, step=1.0)
    cogs_pct = st.number_input("Cost of goods sold (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
    opex = st.number_input("Operating expenses ($M)", min_value=0.0, value=8.0, step=0.5)
    debt = st.number_input("Debt outstanding ($M)", min_value=0.0, value=20.0, step=1.0)
    exports_pct = st.number_input("Revenue from exports (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
    fxcosts_pct = st.number_input("Costs in foreign currency (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)

    st.markdown("---")
    st.caption("Adjust the sliders on the main panel to model different macro scenarios.")

# ── Main: Macro Scenario Sliders ──────────────────────────────────────────────
st.markdown('<p class="section-header">Macro Scenario</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    inflation = st.slider("Inflation rate change (%)", min_value=-3.0, max_value=8.0, value=2.0, step=0.5)
    rates = st.slider("Interest rate change (%)", min_value=-2.0, max_value=5.0, value=1.0, step=0.25)
with col2:
    gdp = st.slider("GDP growth / demand proxy (%)", min_value=-4.0, max_value=5.0, value=2.0, step=0.5)
    fx = st.slider("USD strength change (%)", min_value=-15.0, max_value=15.0, value=5.0, step=1.0)

# ── Calculations ──────────────────────────────────────────────────────────────
cogs = cogs_pct / 100
exports = exports_pct / 100
fxcosts = fxcosts_pct / 100

base_gross_profit = revenue * (1 - cogs)
base_ebit = base_gross_profit - opex
base_interest = debt * 0.05
base_net_income = base_ebit - base_interest

cogs_impact      = -(revenue * cogs * (inflation / 100) * 0.6)
opex_impact      = -(opex * (inflation / 100) * 0.4)
revenue_growth   =  revenue * (gdp / 100) * 0.5
interest_impact  = -(debt * (rates / 100))
fx_revenue       =  revenue * exports * ((-fx) / 100) * 0.5
fx_cost          =  revenue * fxcosts * (fx / 100) * 0.3
fx_net           =  fx_revenue + fx_cost

total_impact    = cogs_impact + opex_impact + revenue_growth + interest_impact + fx_net
new_net_income  = base_net_income + total_impact
margin_base     = (base_net_income / revenue) * 100
margin_new      = (new_net_income / revenue) * 100
margin_delta    = margin_new - margin_base
pct_change      = ((new_net_income - base_net_income) / abs(base_net_income)) * 100 if base_net_income != 0 else 0

def fmt_m(v):
    sign = "+" if v >= 0 else "-"
    return f"{sign}${abs(v):.1f}M"

def fmt_pct(v):
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.1f}%"

# ── Metrics Row ───────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">P&L Impact</p>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Baseline net income", f"${base_net_income:.1f}M")
m2.metric("Projected net income", f"${new_net_income:.1f}M", delta=fmt_m(total_impact))
m3.metric("Net P&L impact", fmt_m(total_impact))
m4.metric("Margin change", fmt_pct(margin_delta), delta=f"{pct_change:.1f}% of base")

# ── Waterfall Chart ───────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Impact Breakdown</p>', unsafe_allow_html=True)

drivers = {
    "Baseline":        base_net_income,
    "COGS inflation":  cogs_impact,
    "OpEx inflation":  opex_impact,
    "Revenue demand":  revenue_growth,
    "Interest expense":interest_impact,
    "FX net impact":   fx_net,
}

measures = ["absolute"] + ["relative"] * (len(drivers) - 1)
labels   = list(drivers.keys())
values   = list(drivers.values())

colors = []
for i, (k, v) in enumerate(drivers.items()):
    if i == 0:
        colors.append("#378ADD")
    elif v >= 0:
        colors.append("#1D9E75")
    else:
        colors.append("#E24B4A")

fig = go.Figure(go.Waterfall(
    orientation="v",
    measure=measures,
    x=labels,
    y=values,
    connector={"line": {"color": "rgba(0,0,0,0.15)", "width": 1}},
    increasing={"marker": {"color": "#1D9E75"}},
    decreasing={"marker": {"color": "#E24B4A"}},
    totals={"marker": {"color": "#378ADD"}},
    text=[f"${v:+.1f}M" for v in values],
    textposition="outside",
))

fig.update_layout(
    height=380,
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(title="Net income ($M)", gridcolor="rgba(0,0,0,0.06)"),
    xaxis=dict(gridcolor="rgba(0,0,0,0)"),
    showlegend=False,
    font=dict(size=12),
)

st.plotly_chart(fig, use_container_width=True)

# ── Driver bar chart ──────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Driver magnitude</p>', unsafe_allow_html=True)

driver_items = [
    ("COGS inflation",   cogs_impact),
    ("OpEx inflation",   opex_impact),
    ("Revenue demand",   revenue_growth),
    ("Interest expense", interest_impact),
    ("FX net impact",    fx_net),
]

bar_labels = [d[0] for d in driver_items]
bar_vals   = [d[1] for d in driver_items]
bar_colors = ["#1D9E75" if v >= 0 else "#E24B4A" for v in bar_vals]

fig2 = go.Figure(go.Bar(
    x=bar_vals,
    y=bar_labels,
    orientation="h",
    marker_color=bar_colors,
    text=[fmt_m(v) for v in bar_vals],
    textposition="outside",
))
fig2.update_layout(
    height=240,
    margin=dict(l=20, r=80, t=10, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(title="Impact ($M)", gridcolor="rgba(0,0,0,0.06)", zeroline=True, zerolinecolor="rgba(0,0,0,0.2)"),
    yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    showlegend=False,
    font=dict(size=12),
)
st.plotly_chart(fig2, use_container_width=True)

# ── AI Briefing ───────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">AI Macro Briefing</p>', unsafe_allow_html=True)

api_key = st.text_input(
    "Anthropic API key",
    type="password",
    placeholder="sk-ant-...",
    help="Get your key at console.anthropic.com"
)

if st.button("Generate AI briefing", type="primary"):
    if not api_key:
        st.warning("Please enter your Anthropic API key above.")
    else:
        prompt = f"""You are a senior macro economist advising a business. Here is their scenario:

Business: ${revenue:.0f}M revenue, {cogs_pct:.0f}% COGS, ${opex:.1f}M OpEx, ${debt:.0f}M debt, {exports_pct:.0f}% export revenue, {fxcosts_pct:.0f}% costs in foreign currency.

Macro scenario applied: inflation {fmt_pct(inflation)}, interest rates {fmt_pct(rates)}, GDP growth {fmt_pct(gdp)}, USD {fmt_pct(fx)}.

Modeled P&L impact: Net income moves from ${base_net_income:.1f}M to ${new_net_income:.1f}M ({fmt_m(total_impact)} total impact). Key drivers: COGS {fmt_m(cogs_impact)}, OpEx {fmt_m(opex_impact)}, revenue demand {fmt_m(revenue_growth)}, interest {fmt_m(interest_impact)}, FX net {fmt_m(fx_net)}.

Write a concise 3-paragraph macro briefing (no headers, plain prose):
1) What this macro environment means for the business and why
2) The biggest risks and what is driving them
3) Two or three concrete strategic recommendations to mitigate the impact.
Be direct and specific. No bullet points."""

        with st.spinner("Generating AI macro briefing..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                briefing = message.content[0].text
                st.markdown(f'<div class="ai-box">{briefing}</div>', unsafe_allow_html=True)
            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check and try again.")
            except Exception as e:
                st.error(f"Error: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Macro Economic Sensitivity Analyzer · Built with Streamlit + Anthropic Claude")
