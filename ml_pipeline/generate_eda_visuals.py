import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

# Set aesthetic style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

# Directory for visuals
output_dir = '/home/hammad/.gemini/antigravity-ide/brain/0c835b87-3f24-4a54-bc3a-3409b9f2f4d1/visuals'
os.makedirs(output_dir, exist_ok=True)

# Load cleaned dataset
csv_path = '/home/hammad/Desktop/project zari - experimental/ml_pipeline/ANALYSIS_COMPLETE/dataset_clean_final.csv'
df = pd.read_csv(csv_path)

print(f"Loaded dataset with shape {df.shape}")

# -------------------------------------------------------------
# 1. CLASS IMBALANCE VISUALIZATION
# -------------------------------------------------------------
plt.figure(figsize=(14, 7), dpi=300)
class_counts = df['class_name'].value_counts()
top_15 = class_counts.head(15)
bottom_15 = class_counts.tail(15)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=300)

# Top 15 Classes
sns.barplot(x=top_15.values, y=top_15.index, palette='Blues_r', ax=ax1)
ax1.set_title('Top 15 Most Frequent Classes (Head)', fontsize=14, fontweight='bold', pad=10)
ax1.set_xlabel('Sample Count', fontsize=12)
for i, v in enumerate(top_15.values):
    ax1.text(v + 50, i, f"{v:,}", va='center', fontsize=10, fontweight='bold', color='#1e293b')

# Bottom 15 Classes
sns.barplot(x=bottom_15.values, y=bottom_15.index, palette='Reds_r', ax=ax2)
ax2.set_title('Bottom 15 Least Frequent Classes (Tail)', fontsize=14, fontweight='bold', pad=10)
ax2.set_xlabel('Sample Count', fontsize=12)
for i, v in enumerate(bottom_15.values):
    ax2.text(v + 2, i, f"{v:,}", va='center', fontsize=10, fontweight='bold', color='#1e293b')

plt.suptitle(f'Target Class Imbalance Analysis (Total Classes: {len(class_counts)}, Imbalance Ratio: {class_counts.max()/class_counts.min():.1f}:1)', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'class_imbalance_top_bottom.png'), bbox_inches='tight')
plt.close()

# Lorenz Curve / Gini Coefficient plot for Class Imbalance
plt.figure(figsize=(8, 6), dpi=300)
sorted_counts = np.sort(class_counts.values)
cum_samples = np.cumsum(sorted_counts) / np.sum(sorted_counts)
cum_classes = np.linspace(0, 1, len(sorted_counts))

# Gini calculation
n = len(sorted_counts)
index = np.arange(1, n + 1)
gini = ((2 * np.sum(index * sorted_counts)) / (n * np.sum(sorted_counts))) - (n + 1) / n

plt.plot(cum_classes * 100, cum_samples * 100, color='#2563eb', linewidth=2.5, label=f'Class Distribution (Gini = {gini:.3f})')
plt.plot([0, 100], [0, 100], color='#94a3b8', linestyle='--', label='Perfect Equality (1:1)')
plt.fill_between(cum_classes * 100, cum_classes * 100, cum_samples * 100, color='#3b82f6', alpha=0.15)

plt.title('Lorenz Curve & Inequality of Class Representation', fontsize=14, fontweight='bold')
plt.xlabel('Cumulative % of Classes', fontsize=12)
plt.ylabel('Cumulative % of Total Samples', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'class_imbalance_lorenz_gini.png'), bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 2. CROP & PATHOGEN METADATA BREAKDOWN
# -------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(18, 6), dpi=300)

# Crop Distribution
crop_counts = df['crop'].value_counts()
sns.barplot(x=crop_counts.values, y=crop_counts.index, palette='Greens_r', ax=axes[0])
axes[0].set_title('Sample Distribution by Crop', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Count', fontsize=11)

# Pathogen Type Breakdown
pathogen_counts = df['pathogen_type'].value_counts()
axes[1].pie(pathogen_counts.values, labels=pathogen_counts.index, autopct='%1.1f%%',
            colors=['#059669', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b'],
            startangle=140, textprops={'fontsize': 11, 'weight': 'bold'})
axes[1].set_title('Pathogen Type Breakdown', fontsize=13, fontweight='bold')

# Crop Family
family_counts = df['crop_family'].value_counts()
sns.barplot(x=family_counts.values, y=family_counts.index, palette='Purples_r', ax=axes[2])
axes[2].set_title('Crop Family Distribution', fontsize=13, fontweight='bold')
axes[2].set_xlabel('Count', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'crop_pathogen_metadata.png'), bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 3. DOMAIN, SOURCE DATASET, AND SPLIT BREAKDOWN
# -------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)

# Domain Distribution (Lab vs Field vs Mixed)
domain_counts = df['domain'].value_counts()
sns.barplot(x=domain_counts.index, y=domain_counts.values, palette=['#0284c7', '#d97706', '#16a34a'], ax=axes[0])
axes[0].set_title('Domain Distribution (Lab vs Field)', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Sample Count', fontsize=11)
for i, v in enumerate(domain_counts.values):
    axes[0].text(i, v + 1000, f"{v:,}\n({v/len(df)*100:.1f}%)", ha='center', fontweight='bold')

# Source Dataset
source_counts = df['source_dataset'].value_counts()
sns.barplot(x=source_counts.index, y=source_counts.values, palette='Oranges_r', ax=axes[1])
axes[1].set_title('Source Dataset Origin', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Sample Count', fontsize=11)
for i, v in enumerate(source_counts.values):
    axes[1].text(i, v + 1000, f"{v:,}\n({v/len(df)*100:.1f}%)", ha='center', fontweight='bold')

# Split Breakdown (Train / Val / Test)
split_counts = df['split'].value_counts()
axes[2].pie(split_counts.values, labels=split_counts.index, autopct='%1.1f%%',
            colors=['#3b82f6', '#10b981', '#f59e0b'], startangle=90,
            textprops={'fontsize': 11, 'weight': 'bold'})
axes[2].set_title('Train / Val / Test Split Ratio', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'domain_source_split.png'), bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 4. IMAGE QUALITY & DIFFICULTY SCORES METADATA
# -------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(18, 10), dpi=300)

# Image Quality Score Distribution
sns.histplot(df['image_quality_score'], bins=40, kde=True, color='#2563eb', ax=axes[0, 0])
axes[0, 0].set_title('Overall Image Quality Score', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Quality Score (0-100)')

# Difficulty Score Breakdown
diff_counts = df['difficulty_score'].value_counts()
sns.barplot(x=diff_counts.index, y=diff_counts.values, palette=['#10b981', '#f59e0b', '#ef4444'], ax=axes[0, 1])
axes[0, 1].set_title('Difficulty Classification (Easy / Medium / Hard)', fontsize=12, fontweight='bold')
for i, v in enumerate(diff_counts.values):
    axes[0, 1].text(i, v + 1000, f"{v:,}\n({v/len(df)*100:.1f}%)", ha='center', fontweight='bold')

# Blur Score (Laplacian Variance)
sns.histplot(np.log1p(df['blur_score']), bins=40, kde=True, color='#8b5cf6', ax=axes[0, 2])
axes[0, 2].set_title('Blur Score Distribution (log1p scale)', fontsize=12, fontweight='bold')
axes[0, 2].set_xlabel('log1p(Blur Score)')

# Brightness vs Contrast
sns.scatterplot(data=df.sample(min(5000, len(df)), random_state=42), x='brightness_score', y='contrast_score', hue='domain', alpha=0.4, palette=['#0284c7', '#d97706', '#16a34a'], ax=axes[1, 0])
axes[1, 0].set_title('Brightness vs Contrast by Domain', fontsize=12, fontweight='bold')

# Entropy Score
sns.kdeplot(data=df, x='entropy_score', hue='domain', fill=True, palette=['#0284c7', '#d97706', '#16a34a'], ax=axes[1, 1])
axes[1, 1].set_title('Image Entropy Distribution across Domains', fontsize=12, fontweight='bold')

# Background Complexity vs Edge Density
sns.scatterplot(data=df.sample(min(5000, len(df)), random_state=42), x='background_complexity', y='edge_density', hue='source_dataset', alpha=0.4, ax=axes[1, 2])
axes[1, 2].set_title('Background Complexity vs Edge Density', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'image_quality_difficulty_metadata.png'), bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# 5. RESOLUTION & ASPECT RATIO ANALYSIS
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

res_df = df.groupby(['image_width', 'image_height']).size().reset_index(name='count').sort_values(by='count', ascending=False).head(10)
res_df['Resolution'] = res_df['image_width'].astype(str) + ' x ' + res_df['image_height'].astype(str)

sns.barplot(data=res_df, x='count', y='Resolution', palette='Blues_r', ax=ax1)
ax1.set_title('Top 10 Most Common Image Resolutions', fontsize=13, fontweight='bold')
ax1.set_xlabel('Sample Count', fontsize=11)
for i, v in enumerate(res_df['count']):
    ax1.text(v + 1000, i, f"{v:,}", va='center', fontweight='bold')

sns.histplot(df['aspect_ratio'], bins=30, kde=True, color='#0284c7', ax=ax2)
ax2.set_title('Aspect Ratio Distribution (Width / Height)', fontsize=13, fontweight='bold')
ax2.axvline(1.0, color='#ef4444', linestyle='--', label='1.0 Square (256x256)')
ax2.legend()

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'resolution_aspect_ratio.png'), bbox_inches='tight')
plt.close()

print("All visual artifacts successfully generated in:", output_dir)
