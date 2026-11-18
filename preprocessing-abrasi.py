import os
import matplotlib.pyplot as plt
import pandas as pd

file_path = r"D:\Kuliah\TUGAS\Semester 5\Statistika Lingkungan\Projek pt 2\Research\gee-output\tabel_statistik_abrasi_jateng_2020_2026.csv"
output_dir = "visual"
os.makedirs(output_dir, exist_ok=True)

try:
    df = pd.read_csv(file_path)
    p1 = df[df['Periode'].str.contains('Fase 1', na=False)].iloc[0]
    p2 = df[df['Periode'].str.contains('Fase 2', na=False)].iloc[0]
    ero = [float(p1['Luas_Abrasi_Ha']), float(p2['Luas_Abrasi_Ha'])]
    acc = [float(p1['Luas_Akresi_Ha']), float(p2['Luas_Akresi_Ha'])]
except Exception:
    ero = [1364.0, 1915.0]
    acc = [2471.0, 1376.0]

phases = ['Phase 1 (2020–2023)\nLa Niña & Surges', 'Phase 2 (2023–2026)\nSuper El Niño']
net = [a - e for a, e in zip(acc, ero)]
x = range(len(phases))

plt.rcParams['font.family'] = 'sans-serif'
fig, ax = plt.subplots(figsize=(7, 4.8), dpi=300)

b_acc = ax.bar(x, acc, width=0.36, color='#2a9d8f', alpha=0.9, label='Accretion')
b_ero = ax.bar(x, [-e for e in ero], width=0.36, color='#e63946', alpha=0.9, label='Erosion')
ax.plot(x, net, color='#1d3557', marker='o', markersize=6, linewidth=1.8, linestyle='--', label='Net Balance')

ax.axhline(0, color='#333333', linewidth=0.8)

for b in b_acc:
    h = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, h + 50, f"+{h:,.0f} ha", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#2a9d8f')

for b in b_ero:
    h = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, h - 140, f"-{abs(h):,.0f} ha", ha='center', va='top', fontsize=8, fontweight='bold', color='#e63946')

for i, val in enumerate(net):
    prefix = "+" if val > 0 else ""
    ax.text(i + 0.22, val, f"Net: {prefix}{val:,.0f} ha", va='center', fontsize=8.5, fontweight='bold', color='#1d3557')

ax.set_title('Central Java Coastal Sediment Budget Shift', fontsize=11, fontweight='600', pad=12, loc='left')
ax.set_ylabel('Area Dynamics (Hectares)', fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(phases, fontsize=8.5)
ax.set_ylim(-2400, 2900)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linestyle=':', alpha=0.35, color='#888888')
ax.xaxis.grid(False)
ax.tick_params(axis='both', which='both', length=0)
ax.legend(frameon=False, loc='upper right', fontsize=8.5)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "sediment_budget_balance.png"), bbox_inches='tight')
plt.close()

fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=300)

ax.plot(x, ero, color='#e63946', marker='o', markersize=7, linewidth=2.2, label='Erosion')
ax.plot(x, acc, color='#2a9d8f', marker='s', markersize=7, linewidth=2.2, label='Accretion')

ax.text(0.02, acc[0] + 60, f"{acc[0]:,.0f} ha", color='#2a9d8f', fontweight='bold', fontsize=8.5)
ax.text(0.98, acc[1] - 110, f"{acc[1]:,.0f} ha (-44%)", color='#2a9d8f', fontweight='bold', fontsize=8.5, ha='right')
ax.text(0.02, ero[0] - 110, f"{ero[0]:,.0f} ha", color='#e63946', fontweight='bold', fontsize=8.5)
ax.text(0.98, ero[1] + 60, f"{ero[1]:,.0f} ha (+40%)", color='#e63946', fontweight='bold', fontsize=8.5, ha='right')

ax.annotate('Crossover Point:\nSediment Starvation',
            xy=(0.58, 1680), xytext=(0.4, 2100),
            arrowprops=dict(facecolor='#1d3557', shrink=0.08, width=0.8, headwidth=4),
            fontsize=8, fontweight='600', color='#1d3557', ha='center')

ax.set_title('Coastal Inversion Trajectory', fontsize=11, fontweight='600', pad=12, loc='left')
ax.set_ylabel('Area Extent (Hectares)', fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(phases, fontsize=8.5)
ax.set_xlim(-0.15, 1.15)
ax.set_ylim(1000, 2700)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linestyle=':', alpha=0.35, color='#888888')
ax.xaxis.grid(False)
ax.tick_params(axis='both', which='both', length=0)
ax.legend(frameon=False, loc='lower left', fontsize=8.5)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "coastal_scissors_trajectory.png"), bbox_inches='tight')
plt.close()