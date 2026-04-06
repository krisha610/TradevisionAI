import numpy as np
from datetime import datetime, timedelta, timezone

def safe_predict(model, data):
    """
    Keras 3 internal bug workaround: model.predict() can fail with
    AttributeError: 'NoneType' object has no attribute 'pop' in name_scope
    when used in multi-threaded environments like Streamlit.
    """
    return model(data, training=False).numpy()

def make_predictions(model, X_train, X_test, y_train, y_test, scaler, close_scaler):
    train_pred = safe_predict(model, X_train)
    test_pred  = safe_predict(model, X_test)

    # Inverse transform using close_scaler (single feature)
    train_pred = close_scaler.inverse_transform(train_pred)
    test_pred  = close_scaler.inverse_transform(test_pred)

    y_train_actual = close_scaler.inverse_transform(y_train.reshape(-1, 1))
    y_test_actual  = close_scaler.inverse_transform(y_test.reshape(-1, 1))

    rmse = np.sqrt(np.mean((test_pred - y_test_actual) ** 2))
    total_actual = np.concatenate((y_train_actual, y_test_actual))

    return train_pred, test_pred, total_actual, rmse


def next_day_prediction(model, scaled_data, close_scaler, window_size=60):
    last_window = scaled_data[-window_size:].reshape(1, window_size, scaled_data.shape[1])
    next_scaled = safe_predict(model, last_window)
    return close_scaler.inverse_transform(next_scaled)[0][0]


def forecast_n_days(model, scaled_data, close_scaler, last_date, window_size=60, forecast_days=5):
    n_features = scaled_data.shape[1]
    current_batch = scaled_data[-window_size:].copy()  # (window, n_features)
    forecast_scaled = []

    for _ in range(forecast_days):
        inp = current_batch.reshape(1, window_size, n_features)
        next_pred = safe_predict(model, inp)[0][0]  # scaled close
        forecast_scaled.append([[next_pred]])

        # Shift window: drop oldest row, append new row
        # For new row: use last row's features but update Close (index 0)
        new_row = current_batch[-1].copy()
        new_row[0] = next_pred
        current_batch = np.vstack([current_batch[1:], new_row])

    forecast_prices = close_scaler.inverse_transform(
        np.array([f[0] for f in forecast_scaled])
    )
    # Generate only business days (Monday-Friday) for forecast dates
    # Ensure they are forward-looking (no past dates)
    forecast_dates = []
    current_date = last_date
    # Use IST (UTC+5.5) for the current date to match India markets
    today = (datetime.now(timezone.utc) + timedelta(hours=5.5)).date()

    
    while len(forecast_dates) < forecast_days:
        current_date += timedelta(days=1)
        # Skip if weekend OR if date is already in the past
        if current_date.weekday() < 5 and current_date.date() >= today:
            forecast_dates.append(current_date)
            
    return forecast_dates, forecast_prices
