import os
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 
import plotly.graph_objects as go
from plotly.subplots import make_subplots

data_file = "data/processed/clean_kerala_monsoon.csv"
figure_folder="reports/figures"
report_folder ='reports'

os.makedirs(figure_folder,exist_ok=True)
os.makedirs(report_folder,exist_ok=True)

df =pd.read_csv(data_file)
mean_rainfall =df["ANNUAL"].mean()
df["ANOMALY"]=df["ANNUAL"] -mean_rainfall
df["ROLLING_MEAN"]=df["ANNUAL"].rolling(window=10).mean()
std_anomaly=df["ANOMALY"].std()
upper_limit= 1.5*std_anomaly
lower_limit =-1.5*std_anomaly

plt.figure(figsize=(15,6))
colors=["blue" if value >= 0 else "red"
          for value in df["ANOMALY"]]
plt.bar(df["YEAR"],df["ANOMALY"],color=colors,alpha=0.6,
        label="Annual Rainfall Anomaly")
plt.plot(df["YEAR"],df["ROLLING_MEAN"]-mean_rainfall,
         color="black",linewidth=2,label="10-Year Rolling Mean Anomaly")
plt.axhline(upper_limit,color="green",linestyle="--",
            label="+1.5 Standard Deviation")
plt.axhline(lower_limit,color="red",linestyle="--",
            label="-1.5 Standard Deviation")
plt.axhline(0,color="black",linewidth=0.8)

wettest=df.loc[df["ANNUAL"].idxmax()]
driest=df.loc[df["ANNUAL"].idxmin()]

plt.annotate(
    f"Wettest: {int(wettest['YEAR'])}\n{wettest['ANNUAL']:.0f} mm",
    xy=(wettest["YEAR"],wettest["ANOMALY"]),
    xytext=(10,15),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->")
)

plt.annotate(
    f"Driest: {int(driest['YEAR'])}\n{driest['ANNUAL']:.0f} mm",
    xy=(driest["YEAR"],driest["ANOMALY"]),
    xytext=(-65,-35),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->")
)

plt.title("Kerala Annual Rainfall Anomalies (1901–2017)")
plt.xlabel("Year")
plt.ylabel("Rainfall Anomaly (mm)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(
    figure_folder+"/primary_envelope.png",
    dpi=300
)
plt.close()
print("Q10 chart created successfully!")

months = [
    "JAN","FEB","MAR","APR","MAY","JUN",
    "JUL","AUG","SEP","OCT","NOV","DEC"
]

df["DECADE"]=((df["YEAR"]-1901)//10)*10+1901
decade_month=df.groupby("DECADE")[months].mean()
decade_month.index=[f'{year}-{min(year+9,2017)}' for year in decade_month.index ]

plt.figure(figsize=(15,9))
sns.heatmap(
    decade_month,
    cmap="YlGnBu",
    annot=True,
    fmt='.0f',
    annot_kws={'size':7},
    linewidths=0.3,
    cbar_kws={"label":"Average Rainfall (mm)"}
)
plt.title("Average Monthly Rainfall Across Decades")
plt.xlabel("Month")
plt.ylabel("Decade")
plt.tight_layout()
plt.savefig(
    figure_folder+"/correlation_heatmap.png",
    dpi=300
)
plt.close()
print("Q11 heatmap created successfully!")

df["EPOCH"]=pd.cut(
    df["YEAR"],
    bins=[1900, 1930, 1960, 1990, 2017],
    labels=[
        "1901-1930",
        "1931-1960",
        "1961-1990",
        "1991-2017"
    ]
)
plt.figure(figsize=(12,7))
ax=sns.boxplot(
    data=df,
    x="EPOCH",
    y="SW_Monsoon"
)
for i ,epoch in enumerate(df["EPOCH"].cat.categories):
    median=df.loc[
        df["EPOCH"]==epoch,
        "SW_Monsoon"
    ].median()
    ax.text(
        i,
        median,
        f"{median:.0f} mm",
        ha="center",
        va="bottom",
        fontweight="bold"
    )    
plt.title("Southwest Monsoon Rainfall Across Four Epochs")
plt.xlabel("Climate Epoch")
plt.ylabel("SW Monsoon Rainfall (mm)")
plt.grid(axis="y",alpha=0.3)
plt.tight_layout()
plt.savefig(
    figure_folder+"/distribution_regimes.png",
    dpi=300
)
plt.close()
print("Q11 boxplot created successfully!")


fig=make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.08,
    subplot_titles=(
        "Annual Rainfall",
        "Southwest Monsoon Rainfall",
        "Northeast Monsoon Rainfall"
    )
)
fig.add_trace(go.Scatter(
    x=df["YEAR"],
    y=df["ANNUAL"],
    mode="lines+markers",
    name="Annual Rainfall",
    hovertemplate="Year: %{x}<br>Annual Rainfall: %{y:.2f} mm<extra></extra>"
),row=1,col=1)

fig.add_trace(go.Scatter(
    x=df["YEAR"],
    y=df["SW_Monsoon"],
    mode="lines+markers",
    name="Southwest Monsoon",
    hovertemplate="Year: %{x}<br>SW Monsoon: %{y:.2f} mm<extra></extra>"
),row=2,col=1)

fig.add_trace(go.Scatter(
    x=df["YEAR"],
    y=df["NE_Monsoon"],
    mode="lines+markers",
    name="Northeast Monsoon",
    hovertemplate="Year:%{x}<br>NE Monsoon: %{y:.2f} mm<extra></extra>"
),row=3,col=1)
fig.update_layout(
    title="Kerala Rainfall Timeline (1901–2017)",
    height=950,
    hovermode="x unified",
    template="plotly_white"
)
fig.update_yaxes(title_text="Rainfall (mm)",row=1,col=1)
fig.update_yaxes(title_text="Rainfall (mm)",row=2,col=1)
fig.update_yaxes(title_text="Rainfall (mm)",row=3,col=1)

fig.update_xaxes(title_text="Year",row=3,col=1)
fig.update_xaxes(
    rangeslider=dict(visible=True),
    row=3,
    col=1
)
fig.write_html(
    report_folder+"/interactive_dashboard.html"
)
print("Q12 interactive dashboard created successfully!")

wettest_year=df.loc[df["ANNUAL"].idxmax()]
driest_year=df.loc[df["ANNUAL"].idxmin()]
highest_sw=df.loc[df["SW_Monsoon"].idxmax()]
lowest_sw=df.loc[df["SW_Monsoon"].idxmin()]

monthly_data=df.melt(
    id_vars=["YEAR"],
    value_vars=months,
    var_name="MONTH",
    value_name="RAINFALL"
)
top_five_months=monthly_data.nlargest(5,"RAINFALL")

with open(report_folder+"/visualization_results.txt","w") as file:
    file.write("KERALA MONSOON ANALYSIS RESULTS\n")
    file.write("================================\n\n")
    file.write(f"Years Covered:{df['YEAR'].min()}-{df['YEAR'].max()}\n")
    file.write(f"Total Records:{len(df)}\n\n")
    file.write(f"Average Annual Rainfall:{mean_rainfall:.2f} mm\n")
    file.write(f"Annual Rainfall Standard Deviation:{df['ANNUAL'].std():.2f}mm\n\n")
    file.write("WETTEST YEAR\n")
    file.write(f"Year:{int(wettest_year['YEAR'])}\n")
    file.write(f"Rainfall:{wettest_year['ANNUAL']:.2f}mm\n\n")
    file.write("DRIEST YEAR\n")
    file.write(f"Year:{int(driest_year['YEAR'])}\n")
    file.write(f"Rainfall:{driest_year['ANNUAL']:.2f}mm\n\n")
    file.write("HIGHEST SW MONSOON RAINFALL\n")
    file.write(f"Year:{int(highest_sw['YEAR'])}\n")
    file.write(f"Rainfall:{highest_sw['SW_Monsoon']:.2f} mm\n\n")
    file.write("LOWEST SW MONSOON RAINFALL\n")
    file.write(f"Year:{int(lowest_sw['YEAR'])}\n")
    file.write(f"Rainfall:{lowest_sw['SW_Monsoon']:.2f}mm\n\n")
    file.write("TOP FIVE WETTEST MONTHS\n")
    for _, row in top_five_months.iterrows():
        file.write(
            f"{int(row['YEAR'])}-{row['MONTH']} : "
            f"{row['RAINFALL']:.2f} mm\n"
        )
print("Report results generated successfully!")
print("\nALL VISUALIZATION TASKS COMPLETED!")