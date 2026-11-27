import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

data_file="data/processed/clean_kerala_monsoon.csv"
figure_folder="reports/figures"
report_folder="reports"

os.makedirs(figure_folder,exist_ok=True)
os.makedirs(report_folder,exist_ok=True)

df=pd.read_csv(data_file)

months=["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

required_columns=["YEAR","ANNUAL","SW_Monsoon","NE_Monsoon"]+months
missing_columns=[col for col in required_columns if col not in df.columns]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

for col in required_columns:
    df[col]=pd.to_numeric(df[col],errors="coerce")

df=df.dropna(subset=required_columns)
df=df.sort_values("YEAR").reset_index(drop=True)

if df.empty:
    raise ValueError("No complete rainfall records found.")

if df["YEAR"].duplicated().any():
    raise ValueError("Duplicate years found in the dataset.")

df["YEAR"]=df["YEAR"].astype(int)

start_year=int(df["YEAR"].min())
end_year=int(df["YEAR"].max())

mean_rainfall=df["ANNUAL"].mean()
df["ANOMALY"]=df["ANNUAL"]-mean_rainfall
df["ROLLING_MEAN"]=df["ANNUAL"].rolling(window=10,min_periods=10).mean()

rolling_mean_anomaly=df["ROLLING_MEAN"]-mean_rainfall
std_anomaly=df["ANOMALY"].std()

upper_limit=1.5*std_anomaly
lower_limit=-1.5*std_anomaly



fig,ax=plt.subplots(figsize=(16,7))
colors=["royalblue" if value>=0 else "indianred" for value in df["ANOMALY"]]
ax.bar(df["YEAR"],df["ANOMALY"],color=colors,alpha=0.7,width=0.8,label="Annual rainfall anomaly")
ax.plot(df["YEAR"],rolling_mean_anomaly,color="black",linewidth=2,label="10-year rolling mean")
ax.axhline(upper_limit,color="green",linestyle="--",linewidth=1.5,label="+1.5 standard deviations")
ax.axhline(lower_limit,color="red",linestyle="--",linewidth=1.5,label="-1.5 standard deviations")
ax.axhline(0,color="black",linewidth=0.8)
ax.set_title(f"Kerala Annual Rainfall Anomalies ({start_year}-{end_year})",fontsize=15,pad=15)
ax.set_xlabel("Year",fontsize=12)
ax.set_ylabel("Rainfall anomaly (mm)",fontsize=12)
ax.set_xlim(start_year-1,end_year+1)
ax.set_xticks(np.arange(start_year,end_year+1,10))
ax.tick_params(axis="both",labelsize=9)

ax.grid(axis="y",linestyle="--",alpha=0.3)
ax.set_axisbelow(True)

ax.legend(loc="upper right",fontsize=9,frameon=True)

plt.tight_layout()
plt.savefig(figure_folder+"/primary_envelope.png",dpi=300,bbox_inches="tight")
plt.close()

print("Q10 anomaly chart created successfully!")



df["DECADE"]=((df["YEAR"]-start_year)//10)*10+start_year
decade_month=df.groupby("DECADE")[months].mean()
decade_labels=[f"{year}-{min(year+9,end_year)}"for year in decade_month.index]
decade_month.index=decade_labels
fig_height=max(7,len(decade_month)*0.55)
fig,ax=plt.subplots(figsize=(16,fig_height))

sns.heatmap(decade_month,cmap="YlGnBu",annot=True,fmt=".0f",annot_kws={"size":8},linewidths=0.5,linecolor="white",cbar_kws={"label":"Average monthly rainfall (mm)"},ax=ax)
ax.set_title("Average Monthly Rainfall Across Decades",fontsize=15,pad=15)
ax.set_xlabel("Month",fontsize=12)
ax.set_ylabel("Decade",fontsize=12)
ax.tick_params(axis="both",labelsize=9)
ax.set_xticklabels(ax.get_xticklabels(),rotation=0)
plt.tight_layout()
plt.savefig(figure_folder+"/correlation_heatmap.png",dpi=300,bbox_inches="tight")
plt.close()

print("Q11 heatmap created successfully!")

epoch_bins=[start_year-1,1930,1960,1990,end_year]
epoch_labels=["1901-1930","1931-1960","1961-1990",f"1991-{end_year}"]

if start_year>1901:
    epoch_bins=[start_year-1,1930,1960,1990,end_year]
    epoch_labels=[f"{start_year}-1930","1931-1960","1961-1990",f"1991-{end_year}"]

df["EPOCH"]=pd.cut(df["YEAR"],bins=epoch_bins,labels=epoch_labels,include_lowest=True)
fig,ax=plt.subplots(figsize=(12,7))

sns.boxplot(data=df,x="EPOCH",y="SW_Monsoon",order=epoch_labels,width=0.5,showmeans=True,meanprops={"marker":"D","markerfacecolor":"white","markeredgecolor":"black","markersize":7},ax=ax)
ax.set_title("Southwest Monsoon Rainfall Across Four Epochs",fontsize=15,pad=15)
ax.set_xlabel("Climate epoch",fontsize=12)
ax.set_ylabel("Southwest monsoon rainfall (mm)",fontsize=12)
ax.tick_params(axis="both",labelsize=10)
ax.grid(axis="y",linestyle="--",alpha=0.3)
ax.set_axisbelow(True)
ax.scatter([],[],marker="D",facecolors="white",edgecolors="black",label="Mean")
ax.legend(loc="upper right",fontsize=9,frameon=True)

fig.text(0.5,0.01,"Box = middle 50% of values  |  Centre line = median  |  Diamond = mean  |  Dots = outliers",ha="center",fontsize=9)
sns.despine(ax=ax)
plt.tight_layout(rect=[0,0.04,1,1])
plt.savefig(figure_folder+"/distribution_regimes.png",dpi=300,bbox_inches="tight")
plt.close()

print("Q11 boxplot created successfully!")


fig=make_subplots(rows=3,cols=1,shared_xaxes=True,vertical_spacing=0.09,subplot_titles=("Annual Rainfall","Southwest Monsoon Rainfall", "Northeast Monsoon Rainfall" ))
chart_data=[("ANNUAL","Annual rainfall","royalblue"),("SW_Monsoon","Southwest monsoon","seagreen"),("NE_Monsoon","Northeast monsoon","darkorange")]

for row,(column,name,color) in enumerate(chart_data,start=1):
    fig.add_trace(go.Scatter(x=df["YEAR"],y=df[column],mode="lines",name=name,line=dict(color=color,width=1.8),hovertemplate="<b>"+name+"</b><br>"+"Year: %{x}<br>"+"Rainfall: %{y:,.2f} mm"+"<extra></extra>"),row=row, col=1)

    fig.update_yaxes(title_text="Rainfall (mm)",showgrid=True,gridcolor="lightgray", zeroline=False,row=row,col=1)

fig.update_xaxes(showgrid=True,gridcolor="lightgray",tickmode="linear",dtick=10)
fig.update_xaxes(
    title_text="Year",
    rangeslider=dict(
        visible=True,
        thickness=0.10,
        bgcolor="whitesmoke",
        bordercolor="gray",
        borderwidth=1
    ),
    row=3,
    col=1
)
fig.update_layout(
    title=dict(
        text=f"Kerala Rainfall Interactive Dashboard ({start_year}-{end_year})",
        x=0.5,
        xanchor="center",
        font=dict(size=21)
    ),
    template="plotly_white",
    height=1050,
    hovermode="x",
    showlegend=False,
    margin=dict(t=110,b=100,l=90,r=50),
    font=dict(size=12),
    dragmode="zoom"
)

fig.update_xaxes(rangeselector=dict(buttons=[dict(count=10,label="10 Years",step="year",stepmode="backward"),dict(count=25,label="25 Years",step="year",stepmode="backward"),dict(count=50,label="50 Years",step="year",stepmode="backward"),dict(step="all",label="All Years")]),row=1,col=1)
fig.write_html(report_folder+"/interactive_dashboard.html",include_plotlyjs=True,full_html=True,config={"responsive":True,"scrollZoom":True,"displayModeBar":True,"displaylogo":False})

print("Q12 interactive dashboard created successfully!")
wettest_year=df.loc[df["ANNUAL"].idxmax()]
driest_year=df.loc[df["ANNUAL"].idxmin()]
highest_sw=df.loc[df["SW_Monsoon"].idxmax()]
lowest_sw=df.loc[df["SW_Monsoon"].idxmin()]
monthly_data=df.melt(id_vars=["YEAR"],value_vars=months,var_name="MONTH", value_name="RAINFALL")
top_five_months=monthly_data.nlargest(5,"RAINFALL")

with open(report_folder+"/visualization_results.txt","w") as file:
    file.write("KERALA MONSOON ANALYSIS RESULTS\n")
    file.write("================================\n\n")
    file.write(f"Years Covered: {start_year}-{end_year}\n")
    file.write(f"Total Records: {len(df)}\n\n")
    file.write(f"Average Annual Rainfall: {mean_rainfall:.2f} mm\n")
    file.write(f"Annual Rainfall Standard Deviation: {df['ANNUAL'].std():.2f} mm\n\n")
    file.write("WETTEST YEAR\n")
    file.write(f"Year: {int(wettest_year['YEAR'])}\n")
    file.write(f"Rainfall: {wettest_year['ANNUAL']:.2f} mm\n\n")
    file.write("DRIEST YEAR\n")
    file.write(f"Year: {int(driest_year['YEAR'])}\n")
    file.write(f"Rainfall: {driest_year['ANNUAL']:.2f} mm\n\n")
    file.write("HIGHEST SW MONSOON RAINFALL\n")
    file.write(f"Year: {int(highest_sw['YEAR'])}\n")
    file.write(f"Rainfall: {highest_sw['SW_Monsoon']:.2f} mm\n\n")
    file.write("LOWEST SW MONSOON RAINFALL\n")
    file.write(f"Year: {int(lowest_sw['YEAR'])}\n")
    file.write(f"Rainfall: {lowest_sw['SW_Monsoon']:.2f} mm\n\n")
    file.write("TOP FIVE WETTEST MONTHS\n")
    for _,row in top_five_months.iterrows():
        file.write(
            f"{int(row['YEAR'])}-{row['MONTH']} : "
            f"{row['RAINFALL']:.2f} mm\n"
        )
print("Results report generated successfully!")
print("\nALL VISUALIZATION TASKS COMPLETED!")