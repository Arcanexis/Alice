#!/usr/bin/env python3
"""
市场研究报告图表生成器 (修复版)
使用 matplotlib 直接生成所有图表，无需外部依赖
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch, FancyArrowPatch, Ellipse
import numpy as np
from pathlib import Path
import argparse
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 配色方案
COLORS = {
    'dark_blue': '#1f4e78',
    'medium_blue': '#4a7ab0',
    'light_blue': '#8ab6d9',
    'green': '#5d8aa8',
    'red': '#d9534f',
    'orange': '#f0ad4e',
    'yellow': '#ffd700',
    'gray': '#999999',
    'white': '#ffffff',
    'light_green': '#90ee90',
    'light_red': '#ffcccb'
}

def create_market_growth_chart(output_path):
    """市场增长轨迹条形图"""
    fig, ax = plt.subplots(figsize=(12, 7), dpi=100)
    
    years = list(range(2020, 2035))
    historical = [15, 22, 35, 52, 75]
    forecast = [95, 125, 160, 200, 245, 295, 350, 410, 475, 545]
    values = historical + forecast
    
    colors = [COLORS['dark_blue']] * 5 + [COLORS['light_blue']] * 10
    bars = ax.bar(years, values, color=colors, edgecolor='black', linewidth=0.5)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'${val}B', ha='center', va='bottom', fontsize=7)
    
    ax.axvline(x=2024.5, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(2024.5, max(values)*1.05, 'Forecast', ha='center', color='red', fontsize=10, fontweight='bold')
    
    cagr = ((545/75)**(1/10) - 1) * 100
    ax.text(2029.5, max(values)*0.5, f'CAGR: {cagr:.1f}%', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Market Size (Billions USD)', fontsize=12, fontweight='bold')
    ax.set_title('Market Growth Trajectory (2020-2034)', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, max(values)*1.15)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()
    print(f"  [完成] 01_market_growth_trajectory.png")

def create_tam_sam_som_chart(output_path):
    """TAM/SAM/SOM 同心圆图"""
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    
    center = (0.5, 0.5)
    tam_circle = Circle(center, 0.45, color=COLORS['dark_blue'], alpha=0.3, label='TAM')
    sam_circle = Circle(center, 0.32, color=COLORS['medium_blue'], alpha=0.4, label='SAM')
    som_circle = Circle(center, 0.18, color=COLORS['light_blue'], alpha=0.5, label='SOM')
    
    ax.add_patch(tam_circle)
    ax.add_patch(sam_circle)
    ax.add_patch(som_circle)
    
    ax.text(center[0], center[1], 'SOM\\n$27B\\n(5%)', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    ax.text(center[0], 0.35, 'SAM\\n$162B\\n(30%)', ha='center', va='center',
            fontsize=12, fontweight='bold')
    ax.text(center[0], 0.15, 'TAM\\n$540B\\n(100%)', ha='center', va='center',
            fontsize=12, fontweight='bold')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('TAM / SAM / SOM Analysis', fontsize=14, fontweight='bold', pad=20)
    
    legend_elements = [
        mpatches.Patch(color=COLORS['dark_blue'], alpha=0.3, label='TAM: Total Addressable Market'),
        mpatches.Patch(color=COLORS['medium_blue'], alpha=0.4, label='SAM: Serviceable Available Market'),
        mpatches.Patch(color=COLORS['light_blue'], alpha=0.5, label='SOM: Serviceable Obtainable Market')
    ]
    ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=1, fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  [完成] 02_tam_sam_som.png")

def create_porters_five_forces(output_path):
    """波特五力分析图"""
    fig, ax = plt.subplots(figsize=(11, 8), dpi=100)
    
    center_x, center_y = 0.5, 0.5
    
    center_box = FancyBboxPatch((center_x-0.12, center_y-0.08), 0.24, 0.16,
                                boxstyle="round,pad=0.02", 
                                facecolor=COLORS['orange'], edgecolor='black', linewidth=2)
    ax.add_patch(center_box)
    ax.text(center_x, center_y, 'Rivalry\\nMedium', ha='center', va='center', 
            fontsize=10, fontweight='bold')
    
    forces = [
        {'pos': (center_x, center_y+0.35), 'label': 'Threat of New Entrants', 'level': 'High', 'color': COLORS['red']},
        {'pos': (center_x-0.35, center_y), 'label': 'Supplier Power', 'level': 'Medium', 'color': COLORS['orange']},
        {'pos': (center_x+0.35, center_y), 'label': 'Buyer Power', 'level': 'Medium', 'color': COLORS['orange']},
        {'pos': (center_x, center_y-0.35), 'label': 'Threat of Substitutes', 'level': 'Low', 'color': COLORS['green']}
    ]
    
    for force in forces:
        box = FancyBboxPatch((force['pos'][0]-0.12, force['pos'][1]-0.06), 0.24, 0.12,
                            boxstyle="round,pad=0.02",
                            facecolor=force['color'], edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(force['pos'][0], force['pos'][1]-0.02, force['label'], 
                ha='center', va='center', fontsize=8)
        ax.text(force['pos'][0], force['pos'][1]+0.04, force['level'], 
                ha='center', va='center', fontsize=8, fontweight='bold')
        
        arrow = FancyArrowPatch(
            force['pos'], (center_x, center_y),
            connectionstyle="arc3,rad=0.1",
            arrowstyle="Simple,tail_width=0.5,head_width=4,head_length=8",
            color='gray', alpha=0.6, linewidth=1.5
        )
        ax.add_patch(arrow)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Porter's Five Forces Analysis", fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  [完成] 03_porters_five_forces.png")

def create_competitive_positioning(output_path):
    """2x2 竞争定位矩阵"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axhline(y=5, color='gray', linestyle='--', linewidth=1)
    ax.axvline(x=5, color='gray', linestyle='--', linewidth=1)
    
    quadrants = [
        {'pos': (7.5, 7.5), 'label': 'Platform Leaders', 'color': COLORS['green']},
        {'pos': (2.5, 7.5), 'label': 'Niche Platforms', 'color': COLORS['light_green']},
        {'pos': (7.5, 2.5), 'label': 'Product Leaders', 'color': COLORS['light_blue']},
        {'pos': (2.5, 2.5), 'label': 'Specialists', 'color': COLORS['gray']}
    ]
    
    for q in quadrants:
        ax.text(q['pos'][0], q['pos'][1], q['label'], 
                ha='center', va='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor=q['color'], alpha=0.3))
    
    companies = [
        {'name': 'NVIDIA', 'x': 8.5, 'y': 9, 'size': 500, 'color': COLORS['dark_blue']},
        {'name': 'AMD', 'x': 6.5, 'y': 8, 'size': 350, 'color': COLORS['red']},
        {'name': 'Intel', 'x': 7, 'y': 6, 'size': 400, 'color': COLORS['medium_blue']},
        {'name': 'Qualcomm', 'x': 3, 'y': 7.5, 'size': 300, 'color': COLORS['orange']},
        {'name': 'ARM', 'x': 2, 'y': 8, 'size': 250, 'color': COLORS['green']},
        {'name': 'Google TPU', 'x': 9, 'y': 7, 'size': 200, 'color': COLORS['light_blue']},
        {'name': 'AWS Inferentia', 'x': 4, 'y': 3, 'size': 180, 'color': COLORS['yellow']},
        {'name': 'AI Chips', 'x': 1.5, 'y': 2, 'size': 150, 'color': COLORS['gray']}
    ]
    
    for comp in companies:
        ax.scatter(comp['x'], comp['y'], s=comp['size'], c=comp['color'], 
                  alpha=0.7, edgecolor='black', linewidth=1)
        ax.text(comp['x'], comp['y'], comp['name'], ha='center', va='center', 
                fontsize=7, fontweight='bold', color='white')
    
    ax.set_xlabel('Market Focus (Niche → Broad)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Solution Approach (Product → Platform)', fontsize=12, fontweight='bold')
    ax.set_title('Competitive Positioning Matrix', fontsize=14, fontweight='bold', pad=20)
    
    ax.scatter([], [], s=500, c=COLORS['dark_blue'], label='Market Share Size', alpha=0.7)
    ax.legend(loc='lower right', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()
    print(f"  [完成] 04_competitive_positioning.png")

def create_risk_heatmap(output_path):
    """风险热图"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    impact_labels = ['Low', 'Medium', 'High', 'Critical']
    probability_labels = ['Unlikely', 'Possible', 'Likely', 'Very Likely']
    
    colors_map = {
        'low': COLORS['light_green'],
        'medium': COLORS['yellow'],
        'high': COLORS['orange'],
        'critical': COLORS['red']
    }
    
    for i in range(4):
        for j in range(4):
            if i + j <= 2:
                color = colors_map['low']
            elif i + j <= 3:
                color = colors_map['medium']
            elif i + j <= 5:
                color = colors_map['high']
            else:
                color = colors_map['critical']
            
            rect = Rectangle((i, j), 1, 1, 
                            facecolor=color, edgecolor='black', linewidth=1)
            ax.add_patch(rect)
    
    risks = [
        {'name': 'R1', 'label': 'Supply Chain', 'impact': 2, 'probability': 2},
        {'name': 'R2', 'label': 'Geopolitical', 'impact': 3, 'probability': 1},
        {'name': 'R3', 'label': 'Tech Obsolescence', 'impact': 2, 'probability': 3},
        {'name': 'R4', 'label': 'Regulatory', 'impact': 1, 'probability': 2},
        {'name': 'R5', 'label': 'Competition', 'impact': 2, 'probability': 2},
        {'name': 'R6', 'label': 'Talent', 'impact': 1, 'probability': 3},
        {'name': 'R7', 'label': 'Market Saturation', 'impact': 2, 'probability': 1},
        {'name': 'R8', 'label': 'Cybersecurity', 'impact': 3, 'probability': 2},
        {'name': 'R9', 'label': 'IP Risk', 'impact': 1, 'probability': 1},
        {'name': 'R10', 'label': 'Currency', 'impact': 1, 'probability': 2}
    ]
    
    for risk in risks:
        ax.scatter(risk['probability'] + 0.5, risk['impact'] + 0.5, 
                  s=200, c='black', alpha=0.5)
        ax.text(risk['probability'] + 0.5, risk['impact'] + 0.5, risk['name'],
                ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    ax.set_xlabel('Impact', fontsize=12, fontweight='bold')
    ax.set_ylabel('Probability', fontsize=12, fontweight='bold')
    ax.set_title('Risk Assessment Heatmap', fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_xticks([0.5, 1.5, 2.5, 3.5])
    ax.set_xticklabels(impact_labels)
    ax.set_yticks([0.5, 1.5, 2.5, 3.5])
    ax.set_yticklabels(probability_labels)
    
    legend_elements = [
        mpatches.Patch(color=COLORS['light_green'], label='Low Risk'),
        mpatches.Patch(color=COLORS['yellow'], label='Medium Risk'),
        mpatches.Patch(color=COLORS['orange'], label='High Risk'),
        mpatches.Patch(color=COLORS['red'], label='Critical Risk')
    ]
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  [完成] 05_risk_heatmap.png")

def create_exec_summary_infographic(output_path):
    """执行摘要信息图"""
    fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
    
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    ax.text(6, 7.5, 'Executive Summary: NVIDIA Market Analysis', 
            ha='center', va='center', fontsize=16, fontweight='bold', color=COLORS['dark_blue'])
    
    center_box = FancyBboxPatch((5, 3), 2, 2.5, boxstyle="round,pad=0.05",
                               facecolor=COLORS['dark_blue'], edgecolor='black', linewidth=2)
    ax.add_patch(center_box)
    ax.text(6, 4.5, '$540B', ha='center', va='center', 
            fontsize=28, fontweight='bold', color='white')
    ax.text(6, 4, 'Total Addressable Market', ha='center', va='center',
            fontsize=10, color='white')
    ax.text(6, 3.5, '(TAM by 2030)', ha='center', va='center',
            fontsize=9, color='white', alpha=0.8)
    
    quadrants = [
        {'pos': (1.5, 5), 'title': 'Growth Rate', 'value': '21.8%', 'subtitle': 'CAGR (2024-2030)'},
        {'pos': (10.5, 5), 'title': 'Key Players', 'value': 'Top 5', 'subtitle': 'NVIDIA, AMD, Intel...'},
        {'pos': (1.5, 1.5), 'title': 'Main Segments', 'value': '4 Core', 'subtitle': 'Data Center, Gaming...'},
        {'pos': (10.5, 1.5), 'title': 'Regional Leaders', 'value': 'NA #1', 'subtitle': 'North America 40%'}
    ]
    
    for q in quadrants:
        box = FancyBboxPatch((q['pos'][0]-1, q['pos'][1]-0.8), 2, 1.6,
                           boxstyle="round,pad=0.03",
                           facecolor=COLORS['light_blue'], edgecolor=COLORS['dark_blue'], linewidth=1.5)
        ax.add_patch(box)
        ax.text(q['pos'][0], q['pos'][1]+0.3, q['title'], 
                ha='center', va='center', fontsize=9, fontweight='bold')
        ax.text(q['pos'][0], q['pos'][1]-0.1, q['value'], 
                ha='center', va='center', fontsize=14, fontweight='bold', color=COLORS['dark_blue'])
        ax.text(q['pos'][0], q['pos'][1]-0.4, q['subtitle'], 
                ha='center', va='center', fontsize=7)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  [完成] 06_exec_summary_infographic.png")

def create_industry_ecosystem(output_path):
    """行业生态系统"""
    fig, ax = plt.subplots(figsize=(14, 6), dpi=100)
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    ax.text(7, 5.5, 'Industry Ecosystem Value Chain', 
            ha='center', va='center', fontsize=14, fontweight='bold')
    
    reg_box = FancyBboxPatch((2, 4.8), 10, 0.5, boxstyle="round,pad=0.02",
                            facecolor=COLORS['gray'], alpha=0.3)
    ax.add_patch(reg_box)
    ax.text(7, 5.05, 'Regulatory Oversight (FTC, SEC, International Trade)', 
            ha='center', va='center', fontsize=9)
    
    stages = [
        {'pos': 1.5, 'label': 'Suppliers', 'subs': ['TSMC', 'Samsung', 'Raw Materials']},
        {'pos': 4.5, 'label': 'Manufacturers', 'subs': ['NVIDIA', 'AMD', 'Intel']},
        {'pos': 7.5, 'label': 'Distributors', 'subs': ['OEMs', 'Retailers', 'Cloud']},
        {'pos': 10.5, 'label': 'End Users', 'subs': ['Enterprises', 'Gamers', 'Researchers']}
    ]
    
    for stage in stages:
        main_box = FancyBboxPatch((stage['pos']-1, 2), 2, 1.5, boxstyle="round,pad=0.03",
                                 facecolor=COLORS['medium_blue'], edgecolor='black')
        ax.add_patch(main_box)
        ax.text(stage['pos'], 3.1, stage['label'], ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')
        
        for i, sub in enumerate(stage['subs']):
            sub_box = FancyBboxPatch((stage['pos']-0.9, 2.7 - i*0.3), 1.8, 0.25,
                                    boxstyle="round,pad=0.01",
                                    facecolor='white', alpha=0.8)
            ax.add_patch(sub_box)
            ax.text(stage['pos'], 2.82 - i*0.3, sub, ha='center', va='center', fontsize=7)
    
    for i in range(len(stages)-1):
        arrow = FancyArrowPatch((stages[i]['pos']+1, 2.75), (stages[i+1]['pos']-1, 2.75),
                               arrowstyle='->', mutation_scale=20, 
                               color=COLORS['dark_blue'], linewidth=2)
        ax.add_patch(arrow)
    
    money_arrow = FancyArrowPatch((10.5, 1.5), (1.5, 1.5),
                                 arrowstyle='->', mutation_scale=20,
                                 color=COLORS['green'], linewidth=2, linestyle='--')
    ax.add_patch(money_arrow)
    ax.text(6, 1.3, 'Payment Flow', ha='center', va='center', 
            fontsize=8, color=COLORS['green'])
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  [完成] 07_industry_ecosystem.png")

def create_regional_breakdown(output_path):
    """区域分解饼图"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'ME & Africa']
    values = [40, 28, 22, 6, 4]
    colors = [COLORS['dark_blue'], COLORS['medium_blue'], COLORS['green'], 
              COLORS['light_blue'], COLORS['gray']]
    
    wedges, texts, autotexts = ax.pie(values, labels=regions, colors=colors,
                                     autopct='%1.1f%%', startangle=90,
                                     textprops={'fontsize': 10, 'fontweight': 'bold'})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
    
    ax.set_title('Market Size by Region', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()
    print(f"  [完成] 08_regional_breakdown.png")

def create_segment_growth(output_path):
    """细分增长条形图"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    segments = ['Data Center', 'Automotive', 'Prof. Vis.', 'Gaming', 'OEM & IP']
    cagr = [25.5, 22.0, 18.5, 15.0, 12.0]
    
    colors = plt.cm.RdYlGn_r(np.linspace(0, 0.6, len(segments)))
    
    bars = ax.barh(segments, cagr, color=colors, edgecolor='black', linewidth=0.5)
    
    for bar, val in zip(bars, cagr):
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2., 
                f'{val}%', ha='left', va='center', fontsize=10, fontweight='bold')
    
    ax.axvline(x=18.6, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(18.6, len(segments)-0.2, 'Avg: 18.6%', ha='center', va='center',
            fontsize=9, color='red', fontweight='bold')
    
    ax.set_xlabel('CAGR (%)', fontsize=12, fontweight='bold')
    ax.set_title('Segment Growth Rate Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.set_xlim(0, 30)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()
    print(f"  [完成] 09_segment_growth.png")

def create_driver_impact_matrix(output_path):
    """驱动因素影响矩阵"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axhline(y=5, color='gray', linestyle='--', linewidth=1)
    ax.axvline(x=5, color='gray', linestyle='--', linewidth=1)
    
    quadrants = [
        {'pos': (7.5, 7.5), 'label': 'Key Drivers', 'color': COLORS['red']},
        {'pos': (2.5, 7.5), 'label': 'Monitor', 'color': COLORS['yellow']},
        {'pos': (7.5, 2.5), 'label': 'Watch', 'color': COLORS['yellow']},
        {'pos': (2.5, 2.5), 'label': 'Lower Priority', 'color': COLORS['light_green']}
    ]
    
    for q in quadrants:
        ax.text(q['pos'][0], q['pos'][1], q['label'], 
                ha='center', va='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor=q['color'], alpha=0.3))
    
    drivers = [
        {'name': 'AI Adoption', 'impact': 9, 'prob': 8, 'size': 300},
        {'name': 'Cloud Computing', 'impact': 8, 'prob': 9, 'size': 280},
        {'name': '5G Expansion', 'impact': 7, 'prob': 8, 'size': 200},
        {'name': 'EV Growth', 'impact': 6, 'prob': 7, 'size': 180},
        {'name': 'Edge Computing', 'impact': 5, 'prob': 6, 'size': 150},
        {'name': 'IoT', 'impact': 6, 'prob': 5, 'size': 160},
        {'name': 'Digital Twin', 'impact': 4, 'prob': 4, 'size': 120},
        {'name': 'Quantum Ready', 'impact': 3, 'prob': 2, 'size': 100}
    ]
    
    for driver in drivers:
        ax.scatter(driver['prob'], driver['impact'], s=driver['size'], 
                  c=COLORS['dark_blue'], alpha=0.6, edgecolor='black')
        ax.text(driver['prob'], driver['impact'], driver['name'], 
                ha='center', va='center', fontsize=7, fontweight='bold', color='white')
    
    ax.set_xlabel('Impact (Low → High)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Probability (Low → High)', fontsize=12, fontweight='bold')
    ax.set_title('Driver Impact Assessment Matrix', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()
    print(f"  [完成] 10_driver_impact_matrix.png")

def create_pestle_analysis(output_path):
    """PESTLE 分析六边形"""
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    
    center = (0.5, 0.5)
    radius = 0.35
    
    pestle_factors = [
        {'name': 'Political', 'color': COLORS['red'], 'angle': 90, 'factors': ['Trade Policies', 'Gov Support', 'Regulations']},
        {'name': 'Economic', 'color': COLORS['dark_blue'], 'angle': 30, 'factors': ['Inflation', 'Exchange Rates', 'GDP Growth']},
        {'name': 'Social', 'color': COLORS['green'], 'angle': -30, 'factors': ['Demographics', 'Work Culture', 'Education']},
        {'name': 'Technological', 'color': COLORS['orange'], 'angle': -90, 'factors': ['AI/ML', '5G', 'Cloud']},
        {'name': 'Legal', 'color': '#8e44ad', 'angle': -150, 'factors': ['IP Laws', 'Antitrust', 'Data Privacy']},
        {'name': 'Environmental', 'color': '#27ae60', 'angle': 150, 'factors': ['Sustainability', 'E-waste', 'Energy']}
    ]
    
    hexagon = mpatches.RegularPolygon(center, numVertices=6, radius=0.08,
                                    orientation=np.pi/6, facecolor=COLORS['dark_blue'],
                                    edgecolor='black', linewidth=2)
    ax.add_patch(hexagon)
    ax.text(center[0], center[1], 'Market\\nAnalysis', ha='center', va='center',
            fontsize=9, fontweight='bold', color='white')
    
    for factor in pestle_factors:
        angle_rad = np.deg2rad(factor['angle'])
        x = center[0] + radius * np.cos(angle_rad)
        y = center[1] + radius * np.sin(angle_rad)
        
        outer_hex = mpatches.RegularPolygon((x, y), numVertices=6, radius=0.12,
                                          orientation=np.pi/6, facecolor=factor['color'],
                                          edgecolor='black', linewidth=1.5, alpha=0.8)
        ax.add_patch(outer_hex)
        
        ax.text(x, y + 0.16, factor['name'], ha='center', va='center',
                fontsize=10, fontweight='bold')
        
        for i, f in enumerate(factor['factors']):
            fy = y - 0.08 - i*0.04
            ax.text(x, fy, f'• {f}', ha='center', va='center', fontsize=7)
        
        line = plt.Line2D([center[0], x], [center[1], y], color='gray', alpha=0.5, linewidth=1)
        ax.add_line(line)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('PESTLE Analysis', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  [完成] 11_pestle_analysis.png")

def create_trends_timeline(output_path):
    """趋势时间线"""
    fig, ax = plt.subplots(figsize=(14, 6), dpi=100)
    
    ax.set_xlim(2023.5, 2030.5)
    ax.set_ylim(0, 4)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_title('Technology Trends Timeline (2024-2030)', fontsize=14, fontweight='bold', pad=20)
    
    ax.axhline(y=2, color='gray', linewidth=2)
    
    trends = [
        {'year': 2024, 'name': 'GenAI Mainstream', 'desc': 'AI assistants widely adopted', 'type': 'tech'},
        {'year': 2025, 'name': 'Edge AI', 'desc': 'AI processing at device level', 'type': 'tech'},
        {'year': 2025.5, 'name': 'Quantum Prep', 'desc': 'Quantum-ready systems', 'type': 'tech'},
        {'year': 2026, 'name': 'AI Governance', 'desc': 'Global AI regulations', 'type': 'reg'},
        {'year': 2027, 'name': '6G Research', 'desc': 'Next-gen wireless begins', 'type': 'tech'},
        {'year': 2028, 'name': 'Neuromorphic', 'desc': 'Brain-inspired computing', 'type': 'tech'},
        {'year': 2029, 'name': 'Green AI', 'desc': 'Energy-efficient AI chips', 'type': 'tech'},
        {'year': 2030, 'name': 'AGI Milestone', 'desc': 'Human-level AI research', 'type': 'tech'}
    ]
    
    for year in range(2024, 2031):
        ax.axvline(x=year, color='lightgray', linestyle='--', alpha=0.5)
        ax.text(year, 1.8, str(year), ha='center', va='top', fontsize=9)
    
    ax.axvline(x=2024, color=COLORS['red'], linewidth=3, alpha=0.7)
    ax.text(2024, 3.8, 'NOW', ha='center', va='center', 
            fontsize=12, fontweight='bold', color=COLORS['red'],
            bbox=dict(boxstyle='round', facecolor='white', edgecolor=COLORS['red']))
    
    for trend in trends:
        if trend['type'] == 'tech':
            color = COLORS['dark_blue']
        else:
            color = COLORS['orange']
        
        ax.scatter(trend['year'], 2, s=150, c=color, edgecolor='black', zorder=5)
        
        y_pos = 2.5 if len([t for t in trends if t['year'] == trend['year']]) == 1 else 3
        ax.text(trend['year'], y_pos, trend['name'], ha='center', va='bottom',
                fontsize=9, fontweight='bold')
        ax.text(trend['year'], y_pos - 0.25, trend['desc'], ha='center', va='top',
                fontsize=7)
    
    ax.set_ylim(1, 4)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()
    print(f"  [完成] 12_trends_timeline.png")

def create_market_share(output_path):
    """市场份额饼图"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    companies = ['NVIDIA', 'AMD', 'Intel', 'Qualcomm', 'Others']
    shares = [18, 15, 12, 10, 45]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    wedges, texts, autotexts = ax.pie(shares, labels=companies, colors=colors,
                                     autopct='%1.1f%%', startangle=90,
                                     textprops={'fontsize': 10, 'fontweight': 'bold'},
                                     explode=(0.1, 0, 0, 0, 0))
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
    
    ax.set_title('Market Share by Company', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()
    print(f"  [完成] 13_market_share.png")

def create_strategic_groups(output_path):
    """战略群体图"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel('Geographic Scope (Regional → Global)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Product Breadth (Narrow → Wide)', fontsize=12, fontweight='bold')
    ax.set_title('Strategic Groups Map', fontsize=14, fontweight='bold', pad=20)
    
    groups = [
        {'label': 'Global Integrators', 'pos': (7.5, 7.5), 'size': 0.8, 'color': COLORS['dark_blue'], 'companies': ['NVIDIA', 'Intel', 'AMD']},
        {'label': 'Regional Specialists', 'pos': (2.5, 7.5), 'size': 0.6, 'color': COLORS['green'], 'companies': ['Qualcomm', 'MediaTek']},
        {'label': 'Focused Innovators', 'pos': (7.5, 2.5), 'size': 0.5, 'color': COLORS['orange'], 'companies': ['AI Startups', 'TPU Teams']},
        {'label': 'Niche Players', 'pos': (2.5, 2.5), 'size': 0.4, 'color': COLORS['gray'], 'companies': ['Specialized', 'FPGA']}
    ]
    
    for group in groups:
        ellipse = Ellipse(group['pos'], group['size']*2, group['size']*1.5,
                          angle=0, facecolor=group['color'], alpha=0.3,
                          edgecolor=group['color'], linewidth=2)
        ax.add_patch(ellipse)
        
        ax.text(group['pos'][0], group['pos'][1] + group['size']*0.6, group['label'],
                ha='center', va='center', fontsize=10, fontweight='bold')
        
        for i, comp in enumerate(group['companies']):
            ax.text(group['pos'][0], group['pos'][1] - group['size']*0.2 - i*0.15,
                    comp, ha='center', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()
    print(f"  [完成] 14_strategic_groups.png")

def create_customer_segments(output_path):
    """客户细分树图"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    segments = [
        {'name': 'Enterprise', 'share': 45, 'color': COLORS['dark_blue']},
        {'name': 'Mid-Market', 'share': 30, 'color': COLORS['medium_blue']},
        {'name': 'SMB', 'share': 18, 'color': COLORS['light_blue']},
        {'name': 'Consumer', 'share': 7, 'color': COLORS['green']}
    ]
    
    y_pos = 0.9
    for seg in segments:
        height = seg['share'] / 100 * 6
        rect = Rectangle((0.3, y_pos - height), 9, height,
                        facecolor=seg['color'], edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        
        ax.text(4.8, y_pos - height/2, f"{seg['name']}\\n{seg['share']}%",
                ha='center', va='center', fontsize=12, fontweight='bold', color='white')
        
        y_pos -= height
    
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_title('Customer Segments by Market Share', fontsize=14, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()
    print(f"  [完成] 15_customer_segments.png")

def create_segment_attractiveness(output_path):
    """细分吸引力矩阵"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
    
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axhline(y=5, color='gray', linestyle='--', linewidth=1)
    ax.axvline(x=5, color='gray', linestyle='--', linewidth=1)
    
    quadrants = [
        {'pos': (7.5, 7.5), 'label': 'Priority Investment', 'color': COLORS['green']},
        {'pos': (2.5, 7.5), 'label': 'Invest for Growth', 'color': COLORS['yellow']},
        {'pos': (7.5, 2.5), 'label': 'Harvest', 'color': COLORS['orange']},
        {'pos': (2.5, 2.5), 'label': 'Deprioritize', 'color': COLORS['gray']}
    ]
    
    for q in quadrants:
        ax.text(q['pos'][0], q['pos'][1], q['label'], 
                ha='center', va='center', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor=q['color'], alpha=0.3))
    
    segments = [
        {'name': 'Data Center', 'size': 8, 'growth': 9, 'profit': 8},
        {'name': 'Gaming', 'size': 9, 'growth': 7, 'profit': 7},
        {'name': 'Automotive', 'size': 6, 'growth': 8, 'profit': 6},
        {'name': 'Prof. Vis.', 'size': 4, 'growth': 5, 'profit': 6},
        {'name': 'OEM & IP', 'size': 5, 'growth': 4, 'profit': 5}
    ]
    
    colors_list = [COLORS['dark_blue'], COLORS['red'], COLORS['green'], COLORS['orange'], COLORS['purple']]
    
    for i, seg in enumerate(segments):
        ax.scatter(seg['size'], seg['growth'], s=seg['profit']*80, 
                  c=colors_list[i], alpha=0.7, edgecolor='black', linewidth=1)
        ax.text(seg['size'], seg['growth'], seg['name'], 
                ha='center', va='center', fontsize=7, fontweight='bold', color='white')
    
    ax.set_xlabel('Segment Size (Small → Large)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Growth Rate (Low → High)', fontsize=12, fontweight='bold')
    ax.set_title('Segment Attractiveness Matrix', fontsize=14, fontweight='bold', pad=20)
    
    ax.scatter([], [], s=100, c=COLORS['dark_blue'], label='Circle Size = Profitability', alpha=0.7)
    ax.legend(loc='lower right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()
    print(f"  [完成] 16_segment_attractiveness.png")

def main():
    parser = argparse.ArgumentParser(description='生成市场研究报告图表')
    parser.add_argument('--topic', '-t', default='NVIDIA', help='市场主题')
    parser.add_argument('--output-dir', '-o', default='figures', help='输出目录')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\\n{'=' * 60}")
    print(f"市场研究图表生成器 (修复版)")
    print(f"{'=' * 60}")
    print(f"主题: {args.topic}")
    print(f"输出目录: {output_dir.absolute()}")
    print(f"{'=' * 60}\\n")
    
    charts = [
        (create_market_growth_chart, '01_market_growth_trajectory.png'),
        (create_tam_sam_som_chart, '02_tam_sam_som.png'),
        (create_porters_five_forces, '03_porters_five_forces.png'),
        (create_competitive_positioning, '04_competitive_positioning.png'),
        (create_risk_heatmap, '05_risk_heatmap.png'),
        (create_exec_summary_infographic, '06_exec_summary_infographic.png'),
        (create_industry_ecosystem, '07_industry_ecosystem.png'),
        (create_regional_breakdown, '08_regional_breakdown.png'),
        (create_segment_growth, '09_segment_growth.png'),
        (create_driver_impact_matrix, '10_driver_impact_matrix.png'),
        (create_pestle_analysis, '11_pestle_analysis.png'),
        (create_trends_timeline, '12_trends_timeline.png'),
        (create_market_share, '13_market_share.png'),
        (create_strategic_groups, '14_strategic_groups.png'),
        (create_customer_segments, '15_customer_segments.png'),
        (create_segment_attractiveness, '16_segment_attractiveness.png')
    ]
    
    for chart_func, filename in charts:
        output_path = output_dir / filename
        try:
            chart_func(output_path)
        except Exception as e:
            print(f"  [错误] {filename}: {str(e)}")
    
    print(f"\\n{'=' * 60}")
    print(f"生成完成！")
    print(f"{'=' * 60}\\n")

if __name__ == '__main__':
    main()
