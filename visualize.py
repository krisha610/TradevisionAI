import matplotlib.pyplot as plt

def plot_initial_trend(data, stock_name):
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label=f'{stock_name} Close Price')
    plt.title(f"{stock_name} Stock Price Trend (2017 - Present)")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


def plot_predictions(total_actual, train_predictions, test_predictions, stock_name):
    plt.figure(figsize=(16, 8))

    plt.plot(total_actual, color='black', alpha=0.4, label='Actual Stock Price')
    plt.plot(range(len(train_predictions)), train_predictions, label='Train Prediction')
    start = len(train_predictions)
    plt.plot(range(start, start + len(test_predictions)),
             test_predictions, label='Test Prediction')

    plt.title(f'{stock_name} Price Prediction - RNN Model Result')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


def plot_5day_forecast(data, forecast_dates, forecast_prices, stock_name):
    plt.figure(figsize=(16, 8))
    plt.plot(data.index[-100:], data['Close'][-100:], label='Actual Recent Price')
    plt.plot(forecast_dates, forecast_prices,
             marker='o', linestyle='--', label='5-Day RNN Forecast')

    plt.title(f'{stock_name} - 5 Day Future Trend Prediction')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
