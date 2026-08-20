import os
import pandas as pd
import numpy as np
import json
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# ---------------------------------------------------------
# Numbered Canvas Class for Header & Footer Page Numbers
# ---------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#334155"))
            self.drawString(36, 756, "ZARI.ai — Complete Exploratory Data Analysis & Specification Report")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.75)
            self.line(36, 748, 576, 748)

        # Running Footer (all pages)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(36, 25, "Confidential — ZARI Machine Learning Core Data Pipeline")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 25, page_text)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(36, 37, 576, 37)

        self.restoreState()

# ---------------------------------------------------------
# Main Script
# ---------------------------------------------------------
def generate_pdf():
    # Load dataset & statistics
    csv_path = '/home/hammad/Desktop/project zari - experimental/ml_pipeline/ANALYSIS_COMPLETE/dataset_clean_final.csv'
    df = pd.read_csv(csv_path)

    img_dir = '/home/hammad/.gemini/antigravity-ide/brain/0c835b87-3f24-4a54-bc3a-3409b9f2f4d1/visuals'
    out_pdf_paths = [
        '/home/hammad/Desktop/project zari/ml_pipeline/reports/ZARI_Complete_EDA_Report.pdf',
        '/home/hammad/.gemini/antigravity-ide/brain/0c835b87-3f24-4a54-bc3a-3409b9f2f4d1/ZARI_Complete_EDA_Report.pdf'
    ]

    for p in out_pdf_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)

    target_pdf = out_pdf_paths[0]
    doc = SimpleDocTemplate(
        target_pdf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1e3a8a")     # Deep Navy
    c_secondary = colors.HexColor("#0284c7")   # Blue Accent
    c_dark = colors.HexColor("#0f172a")        # Slate Dark Text
    c_bg_light = colors.HexColor("#f8fafc")    # Light Table Header
    c_border = colors.HexColor("#e2e8f0")      # Table border

    # Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=6
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_dark
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=c_dark
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    story = []

    # ---------------------------------------------------------
    # Header Banner
    # ---------------------------------------------------------
    story.append(Paragraph("ZARI.ai Dataset Specification & EDA Report", title_style))
    story.append(Paragraph(f"Complete Exploratory Data Analysis, Metadata Audit & Class Imbalance Assessment • Date: {datetime.now().strftime('%Y-%m-%d')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=0, spaceAfter=10))

    # ---------------------------------------------------------
    # Executive Summary Table
    # ---------------------------------------------------------
    story.append(Paragraph("1. Executive Summary & Core Metrics", h1_style))
    story.append(Paragraph("The dataset `dataset_clean_final.csv` forms the clean core benchmark for ZARI.ai agricultural plant disease diagnosis system. Below is the quantitative breakdown of the dataset dimensions and statistical properties.", body_style))

    exec_data = [
        [Paragraph("Metric Attribute", table_header_style), Paragraph("Value", table_header_style), Paragraph("Description / Analytical Significance", table_header_style)],
        [Paragraph("Total Sample Count", table_cell_bold), Paragraph("142,596", table_cell_style), Paragraph("Verified agricultural leaf image dataset size", table_cell_style)],
        [Paragraph("Total Features / Schema", table_cell_bold), Paragraph("39 Columns", table_cell_style), Paragraph("26 populated attributes, 13 placeholder metadata fields", table_cell_style)],
        [Paragraph("Target Classes", table_cell_bold), Paragraph("150 Classes", table_cell_style), Paragraph("Crop-disease taxonomy combinations", table_cell_style)],
        [Paragraph("Max Class Size (Head)", table_cell_bold), Paragraph("5,507", table_cell_style), Paragraph("<code>Orange_Haunglongbing_Greening</code> (3.86% of total)", table_cell_style)],
        [Paragraph("Min Class Size (Tail)", table_cell_bold), Paragraph("41", table_cell_style), Paragraph("<code>Unknown_22</code> (0.0288% of total dataset)", table_cell_style)],
        [Paragraph("Imbalance Ratio (Max:Min)", table_cell_bold), Paragraph("134.32 : 1", table_cell_style), Paragraph("Severe multi-class long-tail imbalance ratio", table_cell_style)],
        [Paragraph("Gini Coefficient", table_cell_bold), Paragraph("0.4503", table_cell_style), Paragraph("High class representation inequality across target classes", table_cell_style)],
        [Paragraph("Pareto 80/20 Concentration", table_cell_bold), Paragraph("48.96%", table_cell_style), Paragraph("Top 20% of classes account for ~49% of all images", table_cell_style)],
        [Paragraph("Domain Environment", table_cell_bold), Paragraph("Lab / Mixed / Field", table_cell_style), Paragraph("Lab: 51.6% (73.6k), Mixed: 36.7% (52.3k), Field: 11.7% (16.7k)", table_cell_style)],
        [Paragraph("Train / Val / Test Split", table_cell_bold), Paragraph("81.2% / 9.3% / 9.6%", table_cell_style), Paragraph("Train: 115,749 | Val: 13,215 | Test: 13,632", table_cell_style)],
    ]

    t_exec = Table(exec_data, colWidths=[130, 95, 315])
    t_exec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_exec)
    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # Section 2: Target Class Imbalance
    # ---------------------------------------------------------
    story.append(Paragraph("2. Target Class Imbalance Analysis & Visuals", h1_style))
    story.append(Paragraph("The dataset exhibits extreme long-tail class imbalance with a **134.32:1 max-to-min ratio** and a Gini coefficient of **0.4503**. Without appropriate algorithmic mitigation (such as weighted sampling or Dirichlet Evidential Loss), neural network models will suffer severe bias towards high-frequency head classes while failing on low-sample field diseases.", body_style))

    # Add Figure 1
    fig1_path = os.path.join(img_dir, 'class_imbalance_top_bottom.png')
    if os.path.exists(fig1_path):
        story.append(Image(fig1_path, width=540, height=236))
        story.append(Paragraph("<b>Figure 1:</b> Top 15 Most Frequent Classes (Head) vs. Bottom 15 Least Frequent Classes (Tail).", ParagraphStyle('Cap', parent=body_style, fontSize=8, textColor=colors.HexColor("#475569"), alignment=1)))
        story.append(Spacer(1, 8))

    # Add Figure 2
    fig2_path = os.path.join(img_dir, 'class_imbalance_lorenz_gini.png')
    if os.path.exists(fig2_path):
        story.append(Image(fig2_path, width=380, height=285))
        story.append(Paragraph("<b>Figure 2:</b> Lorenz Curve depicting cumulative class distribution inequality (Gini = 0.4503).", ParagraphStyle('Cap', parent=body_style, fontSize=8, textColor=colors.HexColor("#475569"), alignment=1)))
        story.append(Spacer(1, 10))

    # Top & Bottom Class Tables
    class_counts = df['class_name'].value_counts()
    top10 = class_counts.head(10)
    bot10 = class_counts.tail(10)

    top_bot_data = [
        [Paragraph("Top 10 Head Classes", table_header_style), Paragraph("Count", table_header_style), Paragraph("% Total", table_header_style),
         Paragraph("Bottom 10 Tail Classes", table_header_style), Paragraph("Count", table_header_style), Paragraph("% Total", table_header_style)]
    ]

    for (k1, v1), (k2, v2) in zip(top10.items(), bot10.items()):
        top_bot_data.append([
            Paragraph(f"<code>{k1}</code>", table_cell_bold),
            Paragraph(f"{v1:,}", table_cell_style),
            Paragraph(f"{v1/len(df)*100:.2f}%", table_cell_style),
            Paragraph(f"<code>{k2}</code>", table_cell_bold),
            Paragraph(f"{v2:,}", table_cell_style),
            Paragraph(f"{v2/len(df)*100:.4f}%", table_cell_style),
        ])

    t_tb = Table(top_bot_data, colWidths=[150, 45, 45, 160, 45, 95])
    t_tb.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_tb)
    story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # Section 3: Crop, Pathogen & Family Metadata
    # ---------------------------------------------------------
    story.append(PageBreak()) # New page for visual clarity
    story.append(Paragraph("3. Crop Species, Botanical Family & Pathogen Etiology", h1_style))
    story.append(Paragraph("Distribution across crop species, pathogen types (Fungal, Bacterial, Viral, Insect/Pest, Healthy), and botanical families.", body_style))

    fig3_path = os.path.join(img_dir, 'crop_pathogen_metadata.png')
    if os.path.exists(fig3_path):
        story.append(Image(fig3_path, width=540, height=180))
        story.append(Paragraph("<b>Figure 3:</b> Sample Distribution across Crop Species, Pathogen Etiology, and Botanical Families.", ParagraphStyle('Cap', parent=body_style, fontSize=8, textColor=colors.HexColor("#475569"), alignment=1)))
        story.append(Spacer(1, 10))

    # Pathogen & Crop Table
    path_counts = df['pathogen_type'].value_counts()
    crop_counts = df['crop'].value_counts().head(6)

    path_data = [
        [Paragraph("Pathogen Category", table_header_style), Paragraph("Samples", table_header_style), Paragraph("% Share", table_header_style),
         Paragraph("Top Crop Species", table_header_style), Paragraph("Samples", table_header_style), Paragraph("% Share", table_header_style)]
    ]

    for (p_name, p_cnt), (c_name, c_cnt) in zip(path_counts.items(), crop_counts.items()):
        path_data.append([
            Paragraph(f"<b>{p_name}</b>", table_cell_style),
            Paragraph(f"{p_cnt:,}", table_cell_style),
            Paragraph(f"{p_cnt/len(df)*100:.1f}%", table_cell_style),
            Paragraph(f"<b>{c_name}</b>", table_cell_style),
            Paragraph(f"{c_cnt:,}", table_cell_style),
            Paragraph(f"{c_cnt/len(df)*100:.1f}%", table_cell_style),
        ])

    t_path = Table(path_data, colWidths=[130, 60, 60, 150, 60, 80])
    t_path.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_path)
    story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # Section 4: Domain, Source Dataset & Split Ratio
    # ---------------------------------------------------------
    story.append(Paragraph("4. Domain Stratification & Source Dataset Breakdown", h1_style))
    story.append(Paragraph("Images are categorized by environmental domain: **Lab** (controlled studio lighting), **Mixed**, and **Field** (real farm in-the-wild conditions). Lab images dominate (51.6%), creating domain-shift risks during field deployment.", body_style))

    fig4_path = os.path.join(img_dir, 'domain_source_split.png')
    if os.path.exists(fig4_path):
        story.append(Image(fig4_path, width=540, height=165))
        story.append(Paragraph("<b>Figure 4:</b> Domain Distribution (Lab vs Field), Source Datasets (PlantVillage, PlantCity, NWRD, PlantDoc), and Data Split Ratios.", ParagraphStyle('Cap', parent=body_style, fontSize=8, textColor=colors.HexColor("#475569"), alignment=1)))
        story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # Section 5: Image Quality Metrics & Difficulty Scores
    # ---------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("5. Image Quality Metrics & Difficulty Stratification", h1_style))
    story.append(Paragraph("Algorithmic extraction of image focus (blur score via Laplacian variance), brightness, contrast, entropy, and composite quality score across samples.", body_style))

    fig5_path = os.path.join(img_dir, 'image_quality_difficulty_metadata.png')
    if os.path.exists(fig5_path):
        story.append(Image(fig5_path, width=540, height=300))
        story.append(Paragraph("<b>Figure 5:</b> Image Quality Metric Distributions (Blur, Contrast, Entropy) and Difficulty Score Breakdown.", ParagraphStyle('Cap', parent=body_style, fontSize=8, textColor=colors.HexColor("#475569"), alignment=1)))
        story.append(Spacer(1, 10))

    q_data = [
        [Paragraph("Quality Metric", table_header_style), Paragraph("Mean Value", table_header_style), Paragraph("Std Dev", table_header_style), Paragraph("Analytical Purpose & Thresholds", table_header_style)],
        [Paragraph("Blur Score (Laplacian)", table_cell_bold), Paragraph(f"{df['blur_score'].mean():.2f}", table_cell_style), Paragraph(f"{df['blur_score'].std():.2f}", table_cell_style), Paragraph("Sharpness of leaf textures (>500 indicates high focus)", table_cell_style)],
        [Paragraph("Brightness Score", table_cell_bold), Paragraph(f"{df['brightness_score'].mean():.2f}", table_cell_style), Paragraph(f"{df['brightness_score'].std():.2f}", table_cell_style), Paragraph("Luminosity (0-255). Ideal range: 80 - 180", table_cell_style)],
        [Paragraph("Contrast Score", table_cell_bold), Paragraph(f"{df['contrast_score'].mean():.2f}", table_cell_style), Paragraph(f"{df['contrast_score'].std():.2f}", table_cell_style), Paragraph("Standard deviation of pixel intensity dynamics", table_cell_style)],
        [Paragraph("Entropy Score", table_cell_bold), Paragraph(f"{df['entropy_score'].mean():.2f}", table_cell_style), Paragraph(f"{df['entropy_score'].std():.2f}", table_cell_style), Paragraph("Information richness / detail complexity", table_cell_style)],
        [Paragraph("Composite Quality Score", table_cell_bold), Paragraph(f"{df['image_quality_score'].mean():.2f}", table_cell_style), Paragraph(f"{df['image_quality_score'].std():.2f}", table_cell_style), Paragraph("Aggregated quality benchmark (0 - 100 scale)", table_cell_style)],
    ]
    t_q = Table(q_data, colWidths=[130, 75, 65, 270])
    t_q.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_q)
    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # Section 6: Resolution & Metadata Field Audit
    # ---------------------------------------------------------
    story.append(Paragraph("6. Image Resolution & Metadata Audit", h1_style))

    fig6_path = os.path.join(img_dir, 'resolution_aspect_ratio.png')
    if os.path.exists(fig6_path):
        story.append(Image(fig6_path, width=540, height=230))
        story.append(Paragraph("<b>Figure 6:</b> Image Resolution Frequencies and Aspect Ratio Distribution.", ParagraphStyle('Cap', parent=body_style, fontSize=8, textColor=colors.HexColor("#475569"), alignment=1)))
        story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Schema Completeness Audit (39 Total Features):</b>", h2_style))
    story.append(Paragraph("• <b>26 Populated Features (100% complete):</b> <code>image_path, crop, disease, class_name, class_id, split, source_dataset, domain, annotation_type, crop_family, disease_family, pathogen_type, image_width, image_height, aspect_ratio, blur_score, brightness_score, contrast_score, sharpness_score, noise_score, entropy_score, background_complexity, edge_density, image_quality_score, difficulty_score</code>.<br/>• <b>13 Placeholder Features (0% populated):</b> <code>lesion_pixels, leaf_pixels, lesion_percentage, severity_score, severity_class, weather, temperature, humidity, gps, country, camera_type, timestamp, farm_id, farmer_id</code>.", body_style))
    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # Section 7: Machine Learning Recommendations
    # ---------------------------------------------------------
    story.append(Paragraph("7. Actionable Machine Learning & Pipeline Recommendations", h1_style))
    rec_text = (
        "1. <b>Evidential Deep Learning (R-EDL):</b> Train model heads to output Dirichlet concentration parameters (α) to quantify predictive uncertainty, allowing the system to abstain from predictions on low-confidence field samples.<br/>"
        "2. <b>Domain-Stratified DataLoader:</b> Standard random sampling yields 88%+ lab/mixed images per batch. Enforce a sampler that forces 50% Field / 50% Lab images in every batch.<br/>"
        "3. <b>Square-Root Class Weighting:</b> Use class weights scaled by <i>1 / sqrt(N_class)</i> to handle the 134:1 class imbalance without gradient explosion on rare classes.<br/>"
        "4. <b>Mixup / CutMix Augmentation:</b> Synthesize lesion boundaries for tail classes (< 200 samples) to prevent over-fitting."
    )
    story.append(Paragraph(rec_text, body_style))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Also copy PDF to second destination
    import shutil
    shutil.copy(target_pdf, out_pdf_paths[1])

    print("PDF generation completed successfully!")
    print("Saved to:")
    for p in out_pdf_paths:
        print(" -", p)

if __name__ == '__main__':
    generate_pdf()
