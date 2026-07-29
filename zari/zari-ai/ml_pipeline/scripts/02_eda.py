import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Configuration
RAW_DATA_DIR = "ml_pipeline/data/raw"
OUTPUT_CSV = "ml_pipeline/dataset_metadata.csv"
PLOTS_DIR = "ml_pipeline/eda_plots"
PDF_REPORT = "ml_pipeline/ZARI_Data_Analysis_Report.pdf"

os.makedirs(PLOTS_DIR, exist_ok=True)

def extract_metadata():
    print("Starting metadata extraction across all datasets...")
    data = []
    
    datasets = ['plantcity', 'plantdoc', 'plantvillage', 'nwrd']
    for source in datasets:
        source_path = os.path.join(RAW_DATA_DIR, source)
        if not os.path.exists(source_path):
            continue
            
        for root, _, files in os.walk(source_path):
            class_name = os.path.basename(root)
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(root, file)
                    try:
                        file_size_kb = os.path.getsize(file_path) / 1024
                        with Image.open(file_path) as img:
                            width, height = img.size
                            mode = img.mode
                            color_channels = len(img.getbands())
                            
                        aspect_ratio = width / height if height > 0 else 0
                        
                        data.append({
                            'dataset_source': source,
                            'class_name': class_name,
                            'file_path': file_path,
                            'width': width,
                            'height': height,
                            'aspect_ratio': aspect_ratio,
                            'color_channels': color_channels,
                            'file_size_kb': file_size_kb
                        })
                    except Exception:
                        pass # Ignore broken files during EDA
                        
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Metadata extracted for {len(df)} images. Saved to {OUTPUT_CSV}")
    return df

def generate_visualizations(df):
    print("Generating EDA visualizations...")
    sns.set_theme(style="whitegrid")
    
    # 1. Source Distribution
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, x='dataset_source', palette='viridis')
    plt.title("Image Count by Dataset Source")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "source_distribution.png"))
    plt.close()
    
    # 2. Top 20 Class Distribution
    plt.figure(figsize=(12, 6))
    top_classes = df['class_name'].value_counts().nlargest(20)
    sns.barplot(x=top_classes.values, y=top_classes.index, palette='rocket')
    plt.title("Top 20 Classes by Image Count (Class Imbalance)")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "class_distribution.png"))
    plt.close()
    
    # 3. Resolution Scatter (sampled for speed)
    plt.figure(figsize=(8, 6))
    sample_df = df.sample(n=min(5000, len(df)), random_state=42)
    sns.scatterplot(data=sample_df, x='width', y='height', hue='dataset_source', alpha=0.6, palette='deep')
    plt.title("Image Resolution Distribution (Sampled)")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "resolution_scatter.png"))
    plt.close()

    # 4. Dummy Confusion Matrix Placeholder (Requested by User for Representation Logic)
    plt.figure(figsize=(8, 6))
    dummy_cm = np.random.randint(0, 100, size=(5, 5))
    sns.heatmap(dummy_cm, annot=True, fmt='d', cmap='Greens', cbar=False)
    plt.title("Evaluation Representation: Expected Confusion Matrix Structure")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "confusion_matrix_representation.png"))
    plt.close()
    
    print("Visualizations saved.")

def generate_pdf_report(df):
    print("Compiling ZARI.ai PDF Report...")
    doc = SimpleDocTemplate(PDF_REPORT, pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []
    
    # Title
    Story.append(Paragraph("ZARI.ai - Phase 2 Exploratory Data Analysis (EDA)", styles['Title']))
    Story.append(Spacer(1, 12))
    
    # Executive Summary Table
    Story.append(Paragraph("1. Executive Summary", styles['Heading2']))
    
    total_images = len(df)
    total_classes = df['class_name'].nunique()
    max_class = df['class_name'].value_counts().max()
    min_class = df['class_name'].value_counts().min()
    imbalance_ratio = max_class / min_class if min_class > 0 else 0
    
    summary_data = [
        ["Metric", "Value"],
        ["Total Images Processed", f"{total_images:,}"],
        ["Total Unique Classes", f"{total_classes:,}"],
        ["Max Images in a Class", f"{max_class:,}"],
        ["Min Images in a Class", f"{min_class:,}"],
        ["Class Imbalance Ratio (Max/Min)", f"{imbalance_ratio:.2f}x"]
    ]
    
    t = Table(summary_data, colWidths=[200, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#00FFA3')),
        ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    Story.append(t)
    Story.append(Spacer(1, 20))
    
    # Plots
    Story.append(Paragraph("2. Dataset Representation & Imbalance", styles['Heading2']))
    Story.append(RLImage(os.path.join(PLOTS_DIR, "source_distribution.png"), width=400, height=250))
    Story.append(Spacer(1, 12))
    Story.append(RLImage(os.path.join(PLOTS_DIR, "class_distribution.png"), width=400, height=200))
    Story.append(Spacer(1, 20))
    
    Story.append(Paragraph("3. Image Resolution Profile", styles['Heading2']))
    Story.append(RLImage(os.path.join(PLOTS_DIR, "resolution_scatter.png"), width=400, height=300))
    Story.append(Spacer(1, 20))
    
    Story.append(Paragraph("4. Evaluation & Model Performance Architecture", styles['Heading2']))
    Story.append(Paragraph("Per user requirements, below is the expected evaluation representation structure mapping our planned EfficientNetV2-S outputs against True classes. This layout will be dynamically populated during Phase 5 testing.", styles['Normal']))
    Story.append(Spacer(1, 12))
    Story.append(RLImage(os.path.join(PLOTS_DIR, "confusion_matrix_representation.png"), width=400, height=300))
    
    doc.build(Story)
    print(f"PDF Report generated successfully at {PDF_REPORT}")

def main():
    print("Initiating Phase 2...")
    df = extract_metadata()
    
    with open("ml_pipeline/logs/02_eda_metrics.txt", "w") as f:
        f.write(f"Total Rows: {len(df)}\n")
        f.write(f"Total Columns: {len(df.columns)}\n")
        f.write(f"Columns: {list(df.columns)}\n")
        
    generate_visualizations(df)
    generate_pdf_report(df)
    print("Phase 2 Complete!")

if __name__ == "__main__":
    main()
