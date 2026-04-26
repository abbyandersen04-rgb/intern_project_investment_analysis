# Macro Economic Sensitivity Analyzer

A Streamlit web app that models how macroeconomic shifts (inflation, interest rates, GDP, FX) impact a business's P&L — with an AI-generated macro briefing powered by Claude.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### 3. API Key
To use the AI briefing feature, you need an Anthropic API key.
Get one at: https://console.anthropic.com

Enter it in the app when prompted (it is never stored).

## Features
- Business profile inputs (revenue, COGS, OpEx, debt, export/FX exposure)
- Four macro scenario sliders: inflation, interest rates, GDP growth, USD strength
- Real-time P&L impact metrics
- Waterfall and bar charts (Plotly)
- AI-generated 3-paragraph macro briefing via Claude

## File structure
```
macro_analyzer/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
└── README.md
```
