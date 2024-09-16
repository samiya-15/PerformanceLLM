import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load and preprocess data
df = pd.read_csv('data/sales_performance_data.csv')
df['dated'] = pd.to_datetime(df['dated'], errors='coerce')
df = df.dropna(subset=['dated'])

# Feature Engineering
df['month'] = df['dated'].dt.month
df['quarter'] = df['dated'].dt.to_period('Q')
df['lag_revenue'] = df['revenue_confirmed'].shift(1)
df['rolling_avg_revenue'] = df['revenue_confirmed'].rolling(window=3).mean()
df['day_of_week'] = df['dated'].dt.day_name()

# Resample and Aggregate
df.set_index('dated', inplace=True)
monthly_trends = df.resample('M').agg({'revenue_confirmed': 'sum'}).dropna()

# Visualization

# 1. Line Plot: Revenue Confirmed Over Time for Each Employee
plt.figure(figsize=(14, 7))
sns.lineplot(data=df.reset_index(), x='dated', y='revenue_confirmed', hue='employee_name')
plt.title('Revenue Confirmed Over Time for Each Employee')
plt.xlabel('Date')
plt.ylabel('Revenue Confirmed')
plt.legend(title='Employee Name', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()

# 2. Histogram: Distribution of Revenue Confirmed
plt.figure(figsize=(10, 6))
plt.hist(df['revenue_confirmed'].dropna(), bins=30, edgecolor='k', alpha=0.7)
plt.title('Distribution of Revenue Confirmed')
plt.xlabel('Revenue Confirmed')
plt.ylabel('Frequency')
plt.show()

# 3. Heatmap: Correlation Heatmap
plt.figure(figsize=(12, 10))
corr_matrix = df[['lead_taken', 'tours_booked', 'applications', 'revenue_confirmed', 'tours_per_lead', 'apps_per_tour', 'apps_per_lead']].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Heatmap')
plt.show()

# 4. Box Plot: Revenue Confirmed by Employee
plt.figure(figsize=(12, 7))
sns.boxplot(data=df.reset_index(), x='employee_name', y='revenue_confirmed')
plt.xticks(rotation=90)
plt.title('Box Plot of Revenue Confirmed by Employee')
plt.xlabel('Employee Name')
plt.ylabel('Revenue Confirmed')
plt.show()

# 5. Bar Plot: Average Tours Booked by Day of the Week
avg_tours_by_day = df.groupby('day_of_week')['tours_booked'].mean()
plt.figure(figsize=(10, 6))
avg_tours_by_day.plot(kind='bar', color='skyblue')
plt.title('Average Tours Booked by Day of the Week')
plt.xlabel('Day of the Week')
plt.ylabel('Average Tours Booked')
plt.xticks(rotation=45)
plt.show()

# 6. Heatmap of Total Calls by Day of the Week
calls_data = df[['mon_call', 'tue_call', 'wed_call', 'thur_call', 'fri_call', 'sat_call', 'sun_call']].sum()
calls_df = pd.DataFrame(calls_data).T
calls_df.index = ['Calls']
plt.figure(figsize=(10, 6))
sns.heatmap(calls_df, annot=True, cmap='YlGnBu', fmt='d')
plt.title('Heatmap of Total Calls by Day of the Week')
plt.show()

# 7. Facet Grid: Trend Analysis for Individual Employees
g = sns.FacetGrid(df.reset_index(), col='employee_name', col_wrap=4, height=4)
g.map_dataframe(sns.lineplot, x='dated', y='revenue_confirmed')
g.set_titles(col_template="{col_name}")
g.set_axis_labels("Date", "Revenue Confirmed")
plt.show()

# 8. Interactive Plotly Visualization: Revenue Confirmed Over Time
fig = px.line(df.reset_index(), x='dated', y='revenue_confirmed', color='employee_name', title='Revenue Confirmed Over Time for Each Employee')
fig.show()
