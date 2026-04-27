# 📈 Broker Contribution Dashboard

A professional-grade financial dashboard built to automate the tracking and ranking of broker transaction volumes across multiple asset classes: **Forex Swap, Fixed Income, and Money Market**.

## 🌟 Key Features

- **All-in-One Market Recap**: A unified view of all categories with Monthly and Daily comparative bar charts in a single screen.
- **Automated Financial Data Parsing**: Custom utility to process non-standard CSV layouts with Indonesian number formatting (e.g., handling `1.280,00` as numeric).
- **Dual Ranking System**: 
  - *Monthly Ranking*: Automated look-back at the previous month's performance.
  - *Daily/Ongoing Ranking*: Real-time updates based on the latest transaction data.
- **Interactive Visualizations**: Dynamic bar charts with volume labels and market share analytics using Plotly.
- **Data Management**: CRUD (Create, Read, Update, Delete) functionality through an interactive data editor and manual input forms.
- **Session-Based State**: Fast and reactive UI using Streamlit's Session State for temporary data handling.

## 🚀 Tech Stack

- **Python 3.x**
- **Streamlit** (Frontend & App Framework)
- **Pandas** (Data Manipulation & Cleaning)
- **Plotly** (Interactive Data Visualization)

## 📁 File Structure

- `app.py`: The main entry point of the dashboard containing the UI logic and multi-page routing.
- `utils.py`: Backend logic for data parsing, ranking calculations, and volume cleaning.
- `data/`: Directory for storing exported master CSV files.
- `requirements.txt`: List of Python dependencies.

## 📥 Installation & Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rexibernardino/Contribution-Dashboard/
   cd broker-ranking-dashboard

2. **Install dependencies**:

```Bash
pip install -r requirements.txt
```
3. **Run the application**:

```Bash
python -m streamlit run app.py
```
