import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

from sympy import sympify, symbols, sqrt

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
st.markdown("- [Time Series Modeling](#the-model)")

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
    rolling_means = provo[provo["Day"].isin(selected_days)].copy()
    rolling_means[selected_metric] = rolling_means.groupby("Day")[selected_metric].rolling(window=smoothness).mean().reset_index(drop=True)
    rolling_means = rolling_means.dropna()
    metric_plot = px.line(rolling_means, x="DATE", y=selected_metric, color="Day")
else:
    rolling_means = provo[provo["Day"].isin(selected_days)].copy()
    rolling_means[selected_metric] = rolling_means[selected_metric].rolling(window=smoothness).mean()
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

st.write(f"R-squared: {term_metrics[term_metric].corr(term_metrics[metric])**2}")

################################################################################################################

st.markdown("---")

st.markdown("## The Model")

st.markdown('''
In the end I computed three main models to help me decipher the effect that environmental factors had on daily fluctuations in traffic citations:
         
1) A multilinear regression model using lasso variable selection methods. Due to time series dependency, a series of lag variable and lag interaction terms are also included in the regression.
2) A multilinear regression using first differences to account for the time series dependence. A lasso regression was also used here to select the appropriate variables. Additionally, due to non-normality of the residuals, robust linear regression was performed.
3) A random forest model across all factors for optimal prediction.
            
A more in depth analysis of the model fitting and selection process can be found on my blog post.
         ''')

provo = pd.read_csv("Provo.csv")
provo["DATE"] = pd.to_datetime(provo["DATE"])

recompile_models = st.button("Recompile Models")

fileExists = False
predictions = pd.DataFrame()

try:
    predictions = pd.read_csv("predictions.csv")
    fileExists = True
except Exception as e:
    fileExists = False

if not fileExists or recompile_models:
    model_factors = ["MaxTemp", "MinTemp", "MeanTemp", "RainPrecip", "SnowPrecip",
                    "Wind", "CO", "NO2", "O3", "PM10", "PM25", "AQI", "Mon", 
                    "Tues", "Wed", "Thurs", "Fri", "Sun", "FullTime", 
                    "Holiday", "Exam", "February", "March", "April", "May", 
                    "June", "July", "August", "September", "October", "November",
                    "December", "Spring", "Summer", "Fall", "DailyNumFines_Lag1",
                    "DailyNumFines_Lag7",
                    "DailyNumFines_Lag14", "DailyNumFines_Lag21", 
                    "DailyNumFines_Lag28"]

    lags = [1, 7, 14, 21, 28]

    provo['log_DailyNumFines'] = np.log(provo['DailyNumFines'] + 1)
    for lag in lags:
        provo[f'DailyNumFines_Lag{lag}'] = provo['DailyNumFines'].shift(lag)

    # Missing Data
    end_date = "2019-04-23"
    begin_date = "2017-03-08"

    # COVID
    covid_begin_date = "2020-03-14"
    covid_end_date = "2020-09-07"

    def truncate_provo(p):
        return p[~((p['DATE'] >= pd.to_datetime(begin_date)) & (p['DATE'] <= pd.to_datetime(end_date)) |
                (p['DATE'] >= pd.to_datetime(covid_begin_date)) & (p['DATE'] <= pd.to_datetime(covid_end_date)))]


    # Add dummy variables
    provo = pd.concat([provo, pd.get_dummies(provo["Term"])], axis=1)

    log_factors = ["RainPrecip", "SnowPrecip", "Wind", "NO2", "PM10", "PM25", "AQI", "FullTime"]

    # Log transformation for log factors
    for factor in log_factors:
        provo[factor] = np.log(provo[factor] + 1)

    polynomial_factors = ["MaxTemp", "MinTemp", "MeanTemp", "RainPrecip", "SnowPrecip",
                        "Wind", "CO", "NO2", "O3", "PM10", "PM25", "AQI",
                        "FullTime", "DailyNumFines_Lag1",
                        "DailyNumFines_Lag7",
                        "DailyNumFines_Lag14", "DailyNumFines_Lag21", 
                        "DailyNumFines_Lag28"]

    for factor in polynomial_factors:
        provo[f'{factor}_2'] = provo[factor]**2
        
    polynomial_factors = [f'{factor}_2' for factor in polynomial_factors]

    env_lag_factors = []

    def add_interaction_factors():
        global provo
        interaction_factors = []

        env_factors = ["MaxTemp", "MinTemp", "MeanTemp", "RainPrecip", "SnowPrecip",
                    "Wind", "CO", "NO2", "O3", "PM10", "PM25", "AQI"]

        days = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sun"]

        months = ["February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        # Create dummy variables for months
        for month in months:
            col = provo['Month'] == month
            col.name = month
            provo = pd.concat([provo, col], axis=1)
        seasons = ["Spring", "Summer", "Fall"]
        lag_factors = ["DailyNumFines_Lag1", "DailyNumFines_Lag7", "DailyNumFines_Lag14", "DailyNumFines_Lag21", "DailyNumFines_Lag28"]

        combinations = [(x, y) for i, x in enumerate(env_factors) for y in env_factors[i + 1:]]
        for combination in combinations:
            factor = '_'.join(combination)
            interaction_factors.append(factor)
            col = provo[combination[0]] * provo[combination[1]]
            col.name = factor
            provo = pd.concat([provo, col], axis=1)

        for day in days:
            factor = f'{day}_DailyNumFines_Lag1'
            env_lag_factors.append(factor)
            interaction_factors.append(factor)
            col = provo[day] * provo['DailyNumFines_Lag1']
            col.name = factor
            provo = pd.concat([provo, col], axis=1)

        for env_factor in env_factors:
            for lag_factor in lag_factors:
                factor = f'{env_factor}_{lag_factor}'
                env_lag_factors.append(factor)
                interaction_factors.append(factor)
                col = provo[env_factor] * provo[lag_factor]
                col.name = factor
                provo = pd.concat([provo, col], axis=1)

            for month in months:
                factor = f'{env_factor}_{month}'
                interaction_factors.append(factor)
                col = provo[env_factor] * provo[month]
                col.name = factor
                provo = pd.concat([provo, col], axis=1)

            for season in seasons:
                factor = f'{env_factor}_{season}'
                interaction_factors.append(factor)
                col = provo[env_factor] * provo[season]
                col.name = factor
                provo = pd.concat([provo, col], axis=1)

        return interaction_factors

    interaction_factors = add_interaction_factors()

    model_factors = model_factors + interaction_factors + polynomial_factors

    provo_truncated = truncate_provo(provo)

    lasso_factors = [
        "NO2", "AQI", "CO", "SnowPrecip", "MinTemp", "MaxTemp", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sun", "FullTime", "Holiday", "Exam", "DailyNumFines_Lag1", "DailyNumFines_Lag14", "DailyNumFines_Lag21", "February", "May", "November", "Spring", "Fall", "RainPrecip", "December", "Wind", "DailyNumFines_Lag7", "August", "O3", "PM10", "DailyNumFines_Lag28", "PM25", "July",
        "SnowPrecip_CO", "Mon_DailyNumFines_Lag1", "Tues_DailyNumFines_Lag1", "Wed_DailyNumFines_Lag1", "Thurs_DailyNumFines_Lag1", "Fri_DailyNumFines_Lag1", "Sun_DailyNumFines_Lag1",
        "MinTemp_DailyNumFines_Lag1", "MaxTemp_DailyNumFines_Lag14", "MaxTemp_DailyNumFines_Lag21", "MinTemp_February", "MinTemp_May", "MinTemp_November", "MinTemp_Spring", "MinTemp_Fall", "RainPrecip_May", "RainPrecip_December", "SnowPrecip_DailyNumFines_Lag1", "SnowPrecip_DailyNumFines_Lag14", "SnowPrecip_DailyNumFines_Lag21",
        "SnowPrecip_February", "Wind_DailyNumFines_Lag7", "Wind_DailyNumFines_Lag14", "Wind_Summer", "CO_August", "CO_November", "NO2_August", "O3_DailyNumFines_Lag7", "O3_DailyNumFines_Lag14", "O3_May", "PM10_DailyNumFines_Lag21", "PM10_DailyNumFines_Lag28", "PM25_July", "PM25_December", "CO_2", "FullTime_2", "DailyNumFines_Lag1_2", "DailyNumFines_Lag7_2"
    ]

    provo_lasso = model.fit(provo_truncated[lasso_factors].iloc[np.max(lags):], provo_truncated["log_DailyNumFines"].iloc[np.max(lags):])

    provo["FirstDifferencePrediction"] = None
    provo["LassoPrediction"] = None
    provo["RFPrediction"] = None

    provo.loc[np.max(lags):, "LassoPrediction"] = np.exp(provo_lasso.predict(provo[lasso_factors].iloc[max(lags):]))-1

    difference = 1

    difference_factors = [
        "NO2", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sun", "Holiday", "Exam", "MaxTemp", "PM25", "MinTemp", "MeanTemp", "RainPrecip", "CO", "SnowPrecip", "Wind", "O3", "AQI", "October", "December", "June", "Wind", "April",  "May", "August", "Spring", "Summer", "PM10", "September", "February",
        "MaxTemp_PM25", "MinTemp_MeanTemp", "RainPrecip_CO", "SnowPrecip_CO", "Wind_NO2", "NO2_O3", "PM25_AQI", "MeanTemp_October", "RainPrecip_December", "SnowPrecip_June", "Wind_April", "Wind_May", "CO_April", "CO_August", "CO_December", "CO_Spring", "NO2_August",
        "NO2_Spring", "NO2_Summer", "PM10_April", "PM10_June", "PM10_September", "PM10_December", "AQI_February", "SnowPrecip_2"
    ]

    for factor in ["log_DailyNumFines"] + difference_factors:
        col = provo[factor]-provo[factor].shift(difference)
        col.name = factor + "_change"
        provo_truncated = pd.concat([provo_truncated, col], axis=1)
        provo = pd.concat([provo, col], axis=1)

    difference_factors = [factor + "_change" for factor in difference_factors]

    provo_first_difference = model.fit(provo_truncated[difference_factors].iloc[difference:], provo_truncated["log_DailyNumFines_change"].iloc[difference:])

    provo.loc[difference:, "FirstDifferencePrediction"] = np.exp(provo_first_difference.predict(provo[difference_factors].iloc[difference:]) + np.log(provo["DailyNumFines"].shift(difference) + 1).iloc[1:])-1

    rf = RandomForestRegressor(n_estimators=100, random_state=1120)
    rf.fit(provo[model_factors].iloc[max(lags):], provo["log_DailyNumFines"].iloc[max(lags):])

    provo.loc[np.max(lags):, "RFPrediction"] = np.exp(rf.predict(provo[model_factors].iloc[max(lags):]))-1

    predictions = provo[["DATE", "DailyNumFines", "LassoPrediction", "FirstDifferencePrediction", "RFPrediction"]]
    predictions.to_csv("predictions.csv", index=False)

predictions["DATE"] = pd.to_datetime(predictions["DATE"])

col1, col2 = st.columns(2)

with col1:
    selected_year = st.selectbox("Select a Year", ["All"]+(np.unique(predictions["DATE"].dt.year)).tolist(), index=0)

with col2:
    selected_term = st.selectbox("Select a Term", ["All"]+(np.unique(predictions["Term"]).tolist()), index=0)

if selected_year == "All":
    selected_year = np.unique(predictions["DATE"].dt.year).tolist()
else:
    selected_year = [int(selected_year)]

if selected_term == "All":
    selected_term = np.unique(predictions["Term"]).tolist()
else:
    selected_term = [selected_term]

model_smoothness = st.slider("Adjust Smoothness", min_value=1, max_value=180, value=30)

predictions = predictions[(predictions["DATE"].dt.year.isin(selected_year)) & (predictions["Term"].isin(selected_term))].copy()

for m in ["LassoPrediction", "FirstDifferencePrediction", "RFPrediction"]:
    predictions[m] = np.maximum(np.round(predictions[m]), [0])

rolling_means = predictions[["DailyNumFines", "LassoPrediction", "FirstDifferencePrediction", "RFPrediction"]].rolling(window=model_smoothness).mean().reset_index(drop=True)
rolling_means["DATE"] = predictions["DATE"].reset_index(drop=True)
rolling_means = rolling_means.iloc[(model_smoothness-1):].copy()

st.write("\# of Daily Fines Over Time")
predictive_plot = px.line(rolling_means, x="DATE", y="DailyNumFines", color_discrete_sequence=["#ff97ff"])
predictive_plot.update_yaxes(title_text="Daily # of Fines")

for m in ["LassoPrediction", "FirstDifferencePrediction", "RFPrediction"]:
    label = ""
    if m == "LassoPrediction":
        label = "Multilinear Model (w/ Weekly Lags)"
    elif m == "FirstDifferencePrediction":
        label = "First Differences"
    else:
        label = "Random Forest"

    predictive_plot.add_scatter(x=rolling_means["DATE"], y=rolling_means[m], mode='lines', name=label)

st.plotly_chart(predictive_plot)

