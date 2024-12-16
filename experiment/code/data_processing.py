import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 数据加载
file_path = '/mnt/data/Agrofood_co2_emission.csv'
data = pd.read_csv(file_path)

# 数据清洗
columns_to_drop = [
    'Rural population', 'Urban population', 'Total Population - Male',
    'Total Population - Female'
]
data_cleaned = data.drop(columns=columns_to_drop)

# 填充缺失值
numeric_columns = data_cleaned.select_dtypes(include=['float64', 'int64']).columns
data_cleaned[numeric_columns] = data_cleaned[numeric_columns].fillna(data_cleaned[numeric_columns].mean())

# 1. 总碳排放趋势分析
emission_trend = data_cleaned.groupby('Year')['total_emission'].mean()
plt.figure(figsize=(10, 6))
plt.plot(emission_trend.index, emission_trend.values, marker='o', linestyle='-', linewidth=2, color='royalblue')
plt.xlabel('Year', fontsize=12)
plt.ylabel('Average Total Emission (CO2)', fontsize=12)
plt.title('Trend of Total CO2 Emission Over Years', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 2. 碳排放来源贡献分析
emission_sources = [
    'Savanna fires', 'Forest fires', 'Crop Residues', 'Rice Cultivation',
    'Food Transport', 'Food Processing', 'Manure Management', 'total_emission'
]
source_contribution = data_cleaned[emission_sources].mean()
source_contribution_percent = source_contribution / source_contribution['total_emission'] * 100
source_contribution_percent = source_contribution_percent.drop('total_emission')
plt.figure(figsize=(8, 8))
plt.pie(
    source_contribution_percent,
    labels=source_contribution_percent.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=plt.cm.tab20.colors
)
plt.title('Contribution of Different Sources to Total Emission', fontsize=14)
plt.tight_layout()
plt.show()

# 3. 区域间碳排放对比
latest_year = data_cleaned['Year'].max()
latest_year_data = data_cleaned[data_cleaned['Year'] == latest_year]
region_emission = latest_year_data.groupby('Area')['total_emission'].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(12, 6))
plt.bar(region_emission.index, region_emission.values, color='royalblue', edgecolor='black', alpha=0.8)
plt.xlabel('Area', fontsize=12)
plt.ylabel('Total Emission (CO2)', fontsize=12)
plt.title(f'Total CO2 Emission by Top 10 Regions in {latest_year}', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 4. 平均气温与总碳排放的关系
temperature_emission_data = data_cleaned[['Average Temperature ', 'total_emission']].dropna()
plt.figure(figsize=(10, 6))
plt.scatter(
    temperature_emission_data['Average Temperature '],
    temperature_emission_data['total_emission'],
    alpha=0.7,
    color='royalblue',
    edgecolor='black'
)
plt.xlabel('Average Temperature (°C)', fontsize=12)
plt.ylabel('Total Emission (CO2)', fontsize=12)
plt.title('Correlation between Average Temperature and Total Emission', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 5. 重要特征对总排放量的贡献
important_features = [
    'Rice Cultivation', 'Food Transport', 'Food Processing',
    'Manure Management', 'Average Temperature ', 'total_emission'
]
correlation_matrix = data_cleaned[important_features].corr()
plt.figure(figsize=(10, 8))
plt.imshow(correlation_matrix, cmap='coolwarm', interpolation='nearest')
plt.colorbar(label='Correlation Coefficient')
plt.xticks(range(len(important_features)), important_features, rotation=45, ha='right', fontsize=12)
plt.yticks(range(len(important_features)), important_features, fontsize=12)
plt.title('Correlation of Features with Total Emission', fontsize=14)
for i in range(len(important_features)):
    for j in range(len(important_features)):
        value = correlation_matrix.iloc[i, j]
        plt.text(j, i, f"{value:.2f}", ha='center', va='center', color="black")
plt.tight_layout()
plt.show()
