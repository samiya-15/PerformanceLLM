import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-GUI operations

from flask import Flask, send_file
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io

app = Flask(__name__)

# Load and preprocess data
df = pd.read_csv('data/sales_performance_data.csv')
df['dated'] = pd.to_datetime(df['dated'], format='%d/%m/%Y', errors='coerce')
df = df.dropna(subset=['dated'])
df['month'] = df['dated'].dt.month
df['quarter'] = df['dated'].dt.to_period('Q')
df['lag_revenue'] = df['revenue_confirmed'].shift(1)
df['rolling_avg_revenue'] = df['revenue_confirmed'].rolling(window=3).mean()
df['day_of_week'] = df['dated'].dt.day_name()
df.set_index('dated', inplace=True)

# Endpoint for Line Plot
@app.route('/api/line_plot')
def line_plot():
    plt.figure(figsize=(14, 7))
    sns.lineplot(data=df.reset_index(), x='dated', y='revenue_confirmed', hue='employee_name')
    plt.title('Revenue Confirmed Over Time for Each Employee')
    plt.xlabel('Date')
    plt.ylabel('Revenue Confirmed')
    plt.legend(title='Employee Name', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png', as_attachment=False, download_name='line_plot.png')

# Endpoint for Histogram
@app.route('/api/histogram')
def histogram():
    plt.figure(figsize=(10, 6))
    plt.hist(df['revenue_confirmed'].dropna(), bins=30, edgecolor='k', alpha=0.7)
    plt.title('Distribution of Revenue Confirmed')
    plt.xlabel('Revenue Confirmed')
    plt.ylabel('Frequency')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png', as_attachment=False, download_name='histogram.png')

# Endpoint for Heatmap
@app.route('/api/heatmap')
def heatmap():
    plt.figure(figsize=(12, 10))
    corr_matrix = df[['lead_taken', 'tours_booked', 'applications', 'revenue_confirmed', 'tours_per_lead', 'apps_per_tour', 'apps_per_lead']].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Heatmap')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png', as_attachment=False, download_name='heatmap.png')

# Endpoint for Box Plot
@app.route('/api/box_plot')
def box_plot():
    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df.reset_index(), x='employee_name', y='revenue_confirmed')
    plt.xticks(rotation=90)
    plt.title('Box Plot of Revenue Confirmed by Employee')
    plt.xlabel('Employee Name')
    plt.ylabel('Revenue Confirmed')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png', as_attachment=False, download_name='box_plot.png')

# Endpoint for Bar Plot
@app.route('/api/bar_plot')
def bar_plot():
    avg_tours_by_day = df.groupby('day_of_week')['tours_booked'].mean()
    plt.figure(figsize=(10, 6))
    avg_tours_by_day.plot(kind='bar', color='skyblue')
    plt.title('Average Tours Booked by Day of the Week')
    plt.xlabel('Day of the Week')
    plt.ylabel('Average Tours Booked')
    plt.xticks(rotation=45)
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png', as_attachment=False, download_name='bar_plot.png')

# Endpoint for Heatmap of Calls
@app.route('/api/calls_heatmap')
def calls_heatmap():
    calls_data = df[['mon_call', 'tue_call', 'wed_call', 'thur_call', 'fri_call', 'sat_call', 'sun_call']].sum()
    calls_df = pd.DataFrame(calls_data).T
    calls_df.index = ['Calls']
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(calls_df, annot=True, cmap='YlGnBu', fmt='d')
    plt.title('Heatmap of Total Calls by Day of the Week')
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png', as_attachment=False, download_name='calls_heatmap.png')

# Endpoint for Facet Grid (Individual Employee Trends)
@app.route('/api/facet_grid')
def facet_grid():
    g = sns.FacetGrid(df.reset_index(), col='employee_name', col_wrap=4, height=4)
    g.map_dataframe(sns.lineplot, x='dated', y='revenue_confirmed')
    g.set_titles(col_template="{col_name}")
    g.set_axis_labels("Date", "Revenue Confirmed")
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return send_file(img, mimetype='image/png', as_attachment=False, download_name='facet_grid.png')

# Endpoint for Interactive Plotly Visualization
@app.route('/api/interactive_plot')
def interactive_plot():
    fig = px.line(df.reset_index(), x='dated', y='revenue_confirmed', color='employee_name', title='Revenue Confirmed Over Time for Each Employee')
    img = fig.to_image(format='png')
    
    return send_file(io.BytesIO(img), mimetype='image/png', as_attachment=False, download_name='interactive_plot.png')

if __name__ == '__main__':
    app.run(debug=True)
