import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sympy import sympify, symbols, sqrt

plt.style.use(['ggplot', 'seaborn-darkgrid'])

st.title("Air Quality in Provo, UT")

st.write('''
In this analysis I seek to answer whether changes in air quality change transportation incentives for students at my univeristy, Brigham Young University (BYU).
''')

st.write('''
To answer this question I combine historical air quality data from the Utah Department of Environmental Quality along with the corresponding colinear weather factors for the corresponding dates.
To measure how the incentives of university students to drive to school I analyzed and aggregated approximated 150,000 traffic citations distributed from my university from the years 2014-2022.
         ''')

st.write('''
This dashboard contains visuals for key elements to exploring the key elements and factors used to distinguishing the "signal from the noise." The goal is to control for all other effects that could otherwise affect the daily number of traffic citations given and isolate the effect that changes in air quality has on students driving to school, and hence, on the number of tickets given out.''')

st.markdown("## Dashboard Guide")
st.markdown("- [Key Metrics Over Time](#key-metrics-over-time)")
st.markdown("- [Time Series Dependence Analysis](#lags-of-key-metrics)")
st.markdown("- [Compare Different Metrics](#analyze-different-metrics-by-school-term)")

provo = pd.read_csv("Provo.csv")

provo["DATE"] = pd.to_datetime(provo["DATE"])

st.markdown("---")

st.markdown("## Key Metrics Over Time")

metrics = ["CO", "NO2", "O3", "PM10", "PM25", "AQI", "MaxTemp", 
           "MinTemp", "MeanTemp", "RainPrecip", "SnowPrecip", 
           "Wind", "DailyNumFines", "NumPaidFines", 
           "TotalFineAmount"]
measurements = {
    "CO": "PPM 8-hour",
    "NO2": "PPB 1-hour",
    "O3": "PPM 8-hour",
    "PM25": "Micrograms/Cubic Meter 24-hour",
    "PM10": "Micrograms/Cubic Meter 24-Hour",
    "AQI": "",
    "MaxTemp": "Celcius",
    "MinTemp": "Celcius",
    "MeanTemp": "Celcius",
    "RainPrecip": "MM",
    "SnowPrecip": "MM",
    "Wind": "Km/h",
    "DailyNumFines": "",
    "NumPaidFines": "",
    "TotalFineAmount": "$",
    "DATE": ""
}

days = provo["Day"].unique()

selected_metric = st.selectbox("Select a Metric", metrics)
smoothness = st.slider("Adjust Smoothness*", min_value=1, max_value=180, value=30)

st.write("Smoothness* is calculated as a rolling average over the specified number of days; i.e. a smoothness of 30 indicates a rolling average spanning over 30 days.")

st.write("Select Days:")

selected_days = []

for day in days:
    checkbox_value = st.checkbox(f'{day}')
    if checkbox_value:
        selected_days.append(day)

st.markdown("---")
separate = st.checkbox("Separate Days by Color")

metric_plot = None
if separate:
    rolling_means = provo[provo["Day"].isin(selected_days)].copy().groupby("Day").rolling(window=smoothness).mean().reset_index(drop=True)
    rolling_means["DATE"] = provo[provo["Day"].isin(selected_days)]["DATE"]
    rolling_means["Day"] = provo[provo["Day"].isin(selected_days)]["Day"]
    rolling_means = rolling_means.dropna()
    metric_plot = px.line(rolling_means, x="DATE", y=selected_metric, color="Day")
else:
    rolling_means = provo[provo["Day"].isin(selected_days)].copy().rolling(window=smoothness).mean()
    rolling_means["DATE"] = provo[provo["Day"].isin(selected_days)]["DATE"]
    metric_plot = px.line(rolling_means, x="DATE", y=selected_metric)
ylabel = measurements[selected_metric]
if len(ylabel) > 0:
    ylabel = "(" + ylabel + ")"
metric_plot.update_yaxes(title_text=f"{selected_metric} {ylabel}")
st.plotly_chart(metric_plot)

st.markdown("## Lags of Key Metrics")

st.write('''
With this time series data set, analyze the effect of past values by calculating lags. Each lag is calculated as the values separated by the (previous) corresponding amount of days.
         ''')

st.markdown("See this [article](https://www.journals.uchicago.edu/doi/full/10.1086/690946) for more information about lagged variables.")

lags = st.slider("Select # of Lags", min_value=1, max_value=90, value=30)

lag_cols = []

for lag in range(1, lags + 1):
    lagged_cols = [provo[metric].shift(lag).rename(f"{metric}_Lag{lag}") for metric in metrics]
    lag_cols.append(pd.concat(lagged_cols, axis=1))

provo = pd.concat([provo] + lag_cols, axis=1)

provo = provo.iloc[lags:]

model = LinearRegression()

lag_metric = st.selectbox("Select a Metric to Analyze the Lags", metrics)

model.fit(provo[[f"{lag_metric}_Lag{lag}" for lag in range(1, lags+1)]], provo[lag_metric])
lag_df = {"Lag": range(1, lags+1),
          "Delta": model.coef_}
lag_df = pd.DataFrame(lag_df)

lag_plot = px.line(lag_df, x="Lag", y="Delta", title=f"{lag_metric} Regressed on {lags} Lag(s)")
lag_plot.update_xaxes(title_text = "Lag (Days Behind)")
lag_plot.update_yaxes(title_text='Coefficient')

st.plotly_chart(lag_plot)

st.markdown("## Analyze Different Metrics by School Term")

st.write("Select Terms:")
unique_terms = provo["Term"].unique()

selected_terms = []
for term in unique_terms:
    checkbox_value = st.checkbox(f'{term}')
    if checkbox_value:
        selected_terms.append(term)

st.markdown("---")

term_metric = st.selectbox("Metric to Analyze: ", metrics)
y_function = st.text_input(f"Equation to Transform {term_metric}. Ex: log({term_metric})", f"{term_metric}")
y = symbols(term_metric)

y_function = sympify(y_function)
st.write(y_function)

metric = st.selectbox("Measure Metric Against: ", ["DATE"]+metrics, index=0)
x_function = st.text_input(f"Equation to Transform {metric}", f"{metric}")
x = symbols(metric)

x_function = sympify(x_function)
st.write(x_function)

term_metrics = provo[provo["Term"].isin(selected_terms)].copy()

try:
    if term_metric != "DATE":
        #st.write(term_metrics[term_metric].apply(lambda z: np.log(z)))
        term_metrics[term_metric] = term_metrics[term_metric].apply(lambda z: float(y_function.subs(y, z)))
    if metric != "DATE":
        term_metrics[metric] = term_metrics[metric].apply(lambda z: float(x_function.subs(x, z)))
except Exception as e:
    st.write("Transformation failed.")
    #st.write(e)

term_metrics_fig = px.scatter(term_metrics, x=metric, y=term_metric, color="Term", color_discrete_sequence=["#4d8ebd", "#af8a82", "#7a9c51", "#e58c1e"],
                              title=f"{term_metric} vs. {metric}")
ylabel = measurements[term_metric]
if len(ylabel) > 0:
    ylabel = "(" + ylabel + ")"
xlabel = measurements[metric]
if len(xlabel) > 0:
    xlabel = "(" + xlabel + ")"

term_metrics_fig.update_yaxes(title_text=f"{term_metric} {ylabel}")
term_metrics_fig.update_xaxes(title_text=f"{metric} {xlabel}")

st.plotly_chart(term_metrics_fig)