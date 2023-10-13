import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
import os
import pandas as pd


print(os.environ.get('PYTHONPATH'))

# Initialize session state if it hasn't been initialized
if 'chem_unit_price' not in st.session_state:
    st.session_state.chem_unit_price = None

if 'synth_chem_df_list' not in st.session_state:
    st.session_state.synth_chem_df_list = []


def run_app():
    st.title("API Plotting")

    # initialize the dataframe csv_df
    csv_df = pd.DataFrame()

    # Open the file explorer dialog for selecting an Excel file
    csv_file = st.file_uploader("Select an Excel file", type=["csv"])
    if csv_file is not None:
        st.write(f"File Name: `{csv_file.name}`")
        csv_df = pd.read_csv(csv_file, index_col=0)
        # Convert the index to DatetimeIndex if it's not
        csv_df.index = pd.DatetimeIndex(csv_df.index)
        st.write(csv_df)


    # Submit Button
    if st.button('Submit'):

        # loop through the columns of the csv file
        for col in csv_df.columns:

            # st.write(f"API: `{col}`")

            # plotting
            fig_synt = go.Figure()

            weighted_df = csv_df[[col]]
            # st.write("weighted_df: ", weighted_df.reset_index()[col])

            # check if there are no entries
            if weighted_df[[col]].isnull().values.all():
                st.write("No entries found in the database")
                continue

            # Apply smoothing
            weighted_df = weighted_df.rolling(10).mean().dropna()

            # --- ARIMA Model ---
            # Fit ARIMA model
            model = ARIMA(weighted_df, order=(1, 1, 1))
            fit_model = model.fit()

            # Forecast future values
            future_steps = 30  # Number of days you want to forecast
            forecast = fit_model.forecast(steps=future_steps)

            # Create future dates
            future_dates = pd.date_range(start=weighted_df.index[-1] + pd.Timedelta(days=1), periods=future_steps, freq='D')

            # Create a new DataFrame to hold the forecast values
            weighted_forecast_df = pd.DataFrame({col: forecast}, index=future_dates)

            # Append forecasted data to the original DataFrame
            weighted_extended_df = pd.concat([weighted_df, weighted_forecast_df])

            # st.write("weighted_extended_df: ", weighted_extended_df)

            # Add line plot for connecting the data points
            fig_synt.add_trace(go.Scatter(x=weighted_extended_df.index, y=weighted_extended_df[col], mode='lines',
                                          name=f"Weighted Sum"))


            # Add vertical line to indicate where the forecast starts
            last_actual_date = weighted_df.index[-1]
            fig_synt.add_shape(type="line", x0=last_actual_date, x1=last_actual_date,
                               y0=0, y1=1, yref='paper', line=dict(color="Red", width=1))

            # Set layout
            fig_synt.update_layout(title=f"{col}", xaxis_title='Date', yaxis_title='FOB Price',
                               plot_bgcolor='rgba(0, 0, 0, 0)')

            # Display the plot
            st.plotly_chart(fig_synt, use_container_width=True)


run_app()
