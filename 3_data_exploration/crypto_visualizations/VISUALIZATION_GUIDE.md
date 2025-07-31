# Crisis Impact Visualization Guide

<!-- markdownlint-disable MD013 -->

## 📊 Overview

The cryptocurrency crisis impact analysis project includes comprehensive visualization capabilities using matplotlib and seaborn. This professional plotting system creates publication-quality charts and dashboards to visualize crisis correlation analysis results.

**Project Context**: Developed as part of the MIT Emerging Talents Program by Group 13 (Data Mavericks).

## 🚀 Quick Start

### Method 1: Integrated Analysis with Plots

Run the comprehensive analyzer with built-in plotting:

```bash
python comprehensive_analyzer.py
```

This will:

1. ✅ Calculate premiums
2. ✅ Analyze market structure  
3. ✅ Correlate with historical data
4. ✅ Generate insights report
5. ✅ **Create all visualizations automatically**

### Method 2: Standalone Plotting

Generate plots from existing analysis data:

```bash
python plot_results.py
```

This will create visualizations using the most recent analysis results.

## 📈 Generated Visualizations

### 1. Premium Analysis Charts (`premium_analysis.png`)

**4-panel visualization showing:**

- **Bar Chart**: Premium vs Official Exchange Rate by country
- **Pie Chart**: Market activity distribution
- **Scatter Plot**: Premium vs Market Size correlation
- **Crisis Assessment**: Severity level distribution

**Key Features:**

- Color-coded countries (Red=High Crisis, Blue=Stable, etc.)
- Crisis level indicators (>100% = Extreme, >50% = High)
- Value labels on all charts
- Professional styling with grid lines

### 2. Historical Correlation Analysis (`historical_correlation.png`)

**4-panel analysis of crisis events:**

- **Timeline**: Bitcoin volatility during crisis events
- **Country Comparison**: Average volatility by country
- **Event Types**: Impact analysis by crisis type
- **Correlation Heatmap**: Multi-cryptocurrency correlation matrix

**Key Features:**

- Date-formatted timeline with crisis event annotations
- Top volatile events highlighted with tooltips
- Crisis severity color coding
- Statistical correlation analysis

### 3. Market Structure Analysis (`market_structure.png`)

**4-panel market dynamics:**

- **Buy vs Sell**: Order distribution by country
- **Market Patterns**: Pattern distribution (balanced/pressure)
- **Crisis Indicators**: Activity vs crisis level scatter
- **Market Share**: Percentage distribution of trading activity

**Key Features:**

- Side-by-side buy/sell comparison
- Crisis indicator mapping (High/Moderate/Stable)
- Market concentration analysis
- Pattern recognition visualization

### 4. Comprehensive Dashboard (`comprehensive_dashboard.png`)

**Large-format executive summary:**

- **Top Row**: Premium analysis and market correlation
- **Second Row**: Historical volatility timeline and country comparison  
- **Third Row**: Market structure and pattern analysis
- **Bottom Row**: Key insights and recommendations text

**Key Features:**

- Executive-level overview on single page
- 20x16 inch high-resolution format
- Automated insights generation
- Professional dashboard layout

## 🎨 Customization Options

### Color Schemes

The visualization engine uses consistent color coding:

```python
country_colors = {
    'SD': '#FF6B6B',  # Red - High crisis (Sudan)
    'VE': '#4ECDC4',  # Teal - Moderate crisis (Venezuela)  
    'AR': '#45B7D1',  # Blue - Stable (Argentina)
    'AF': '#96CEB4',  # Green - Isolated (Afghanistan)
    'NG': '#FECA57',  # Orange (Nigeria)
    'ZW': '#A29BFE'   # Purple (Zimbabwe)
}

crisis_colors = {
    'high': '#FF4757',
    'moderate': '#FFA502', 
    'stable': '#2ED573',
    'isolated': '#5352ED'
}
```

### Plot Styling

- **Style**: `seaborn-v0_8-darkgrid` for professional appearance
- **Palette**: `husl` for distinct, vibrant colors
- **DPI**: 300 for publication-quality resolution
- **Format**: PNG with white background

## 🔧 Advanced Usage

### Custom Plot Generation

```python
from visualization.crisis_plots import CrisisVisualizationEngine
import pandas as pd

# Initialize visualizer
visualizer = CrisisVisualizationEngine(output_dir="custom_plots")

# Load your data
premium_data = pd.read_csv("data/analysis/reports/premium_summary_latest.csv")
correlation_data = pd.read_csv("data/analysis/crisis_correlations/historical_correlation_latest.csv")
market_data = pd.read_csv("data/processed/country_aggregates/market_structure_latest.csv")

# Generate specific plots
visualizer.plot_premium_analysis(premium_data, "custom_premium.png")
visualizer.plot_historical_correlation(correlation_data, "custom_correlation.png")
visualizer.plot_market_structure(market_data, "custom_market.png")

# Create comprehensive dashboard
visualizer.plot_comprehensive_dashboard(premium_data, correlation_data, market_data, "custom_dashboard.png")
```

### Programmatic Access

```python
# Run analysis and get plotting results
from comprehensive_analyzer import CrisisImpactAnalyzer

analyzer = CrisisImpactAnalyzer()
results = analyzer.run_full_analysis(include_plots=True)

if results['plots_generated']:
    print("✅ Plots created successfully!")
    # Access the raw data for custom analysis
    premium_data = results['premium_data']
    market_data = results['market_data']
    correlation_data = results['correlation_data']
```

## 📁 Output Structure

```text
data/analysis/plots/
├── premium_analysis.png          # Premium vs exchange rate analysis
├── historical_correlation.png    # Crisis event correlations  
├── market_structure.png          # P2P market dynamics
└── comprehensive_dashboard.png   # Executive summary dashboard
```

## 🎯 Key Features

### Professional Quality

- **High Resolution**: 300 DPI for publications/reports
- **Consistent Styling**: Professional color schemes and fonts
- **Publication Ready**: White backgrounds, clean layouts
- **Scalable**: Vector-quality rendering

### Interactive Elements

- **Annotations**: Key events and insights highlighted
- **Value Labels**: Precise values shown on charts
- **Color Coding**: Consistent country and crisis level colors
- **Grid Lines**: Easy value reading

### Comprehensive Coverage

- **Multi-Perspective**: Premium, correlation, and market analysis
- **Time Series**: Historical event correlation tracking
- **Comparative**: Cross-country and cross-crypto analysis
- **Summary**: Executive dashboard with key insights

## 🔍 Troubleshooting

### Missing Dependencies

```bash
pip install matplotlib seaborn
```

### Data Not Found

Ensure you have run the analysis first:

```bash
python comprehensive_analyzer.py
```

### Custom Output Directory

```python
visualizer = CrisisVisualizationEngine(output_dir="my_custom_plots")
```

### Memory Issues

For large datasets, the plotting may require significant memory. Consider:

- Reducing data size through filtering
- Running plots separately rather than all at once
- Increasing system memory allocation

## 📊 Example Results

The visualizations will help you identify:

- **🔥 Crisis Hotspots**: Countries with extreme premiums (>100%)
- **📈 Volatility Patterns**: How crypto markets react to specific crisis events
- **🏗️ Market Dynamics**: Whether markets show buy pressure, sell pressure, or balance
- **🌍 Regional Trends**: Geographic patterns in crisis impact
- **📅 Timeline Analysis**: When and how crises affect cryptocurrency adoption

## 🚀 Next Steps

1. **Run Analysis**: Execute `python comprehensive_analyzer.py`
2. **Review Plots**: Open the plots directory to examine results
3. **Customize**: Modify colors, layouts, or add new visualizations
4. **Share Results**: Use high-resolution plots in presentations/reports
5. **Automate**: Set up scheduled analysis runs with automatic plot generation

## 💡 Tips

- **Best Practice**: Always run the full analysis before generating standalone plots
- **Performance**: Plotting is fast - typically completes in under 30 seconds
- **Quality**: Plots are publication-ready at 300 DPI
- **Flexibility**: Easy to customize colors, layouts, and output formats
- **Integration**: Plotting seamlessly integrates with existing analysis workflow
