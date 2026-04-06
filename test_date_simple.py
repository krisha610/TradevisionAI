from datetime import datetime, timedelta

def generate_forecast_dates(last_date, forecast_days):
    forecast_dates = []
    current_date = last_date
    while len(forecast_dates) < forecast_days:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # 0=Mon, 4=Fri
            forecast_dates.append(current_date)
    return forecast_dates

# Test Scenario: Starting Friday, April 3, 2026
last_date = datetime(2026, 4, 3) 
dates = generate_forecast_dates(last_date, 5)

print(f"LAST DATE: {last_date.strftime('%Y-%m-%d (%A)')}")
for i, d in enumerate(dates):
    print(f"FORECAST {i+1}: {d.strftime('%Y-%m-%d (%A)')}")
