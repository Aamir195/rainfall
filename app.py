from flask import Flask, render_template, url_for, request, redirect
import pandas as pd
import datetime
from pandas.tseries.offsets import DateOffset
import statsmodels.api as sm

# model 
Kerala = pd.read_csv('Kerala.csv')
Kerala['Month'] = pd.to_datetime(Kerala['Month'])
Kerala.set_index('Month', inplace=True)
model = sm.tsa.statespace.SARIMAX(Kerala['Rainfall'], order=(5,0,2), seasonal_order=(5,0,[],12))
forecast_model = model.fit()

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        month = request.form['month']

        dt = datetime.datetime.strptime(month, '%Y-%m-%d')

        start_date = datetime.datetime(2017,12,1)
        end_date = datetime.datetime(dt.year, dt.month, dt.day)

        num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

        future_dates = [Kerala.index[-1] + DateOffset(months=x) for x in range(0,num_months+1)]

        future_dates_df = pd.DataFrame(index = future_dates[1:], columns = Kerala.columns)
        future_df = pd.concat([Kerala, future_dates_df])

        last_index = future_df.shape[0]

        future_df['forecast'] = forecast_model.predict(start = 1403, end = last_index, dynamic = True)
        print(future_df.index[-1], future_df.forecast[-1])
        data = []
        data.append(month)
        data.append(future_df.forecast[-1])
        return render_template('index.html', data = data)

    else:
        return render_template('index.html')


@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/calendar')
def calendar():
    return render_template('calendar.html')


if __name__ == "__main__":
    app.run(debug=True)