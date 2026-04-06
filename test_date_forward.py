from datetime import datetime, timedelta

def generate_forecast_dates(last_date, forecast_days, mock_today):
    forecast_dates = []
    current_date = last_date
    today = mock_today.date()
    
    while len(forecast_dates) < forecast_days:
        current_date += timedelta(days=1)
        # Skip if weekend OR if date is already in the past
        if current_date.weekday() < 5 and current_date.date() >= today:
            forecast_dates.append(current_date)
    return forecast_dates

# Scenario: Today is Monday, April 6, 2026.
# History ends on Thursday, April 2nd (Friday was a holiday).
mock_today = datetime(2026, 4, 6)
last_date = datetime(2026, 4, 2)

print(f"MOCK TODAY: {mock_today.strftime('%Y-%m-%d (%A)')}")
print(f"LAST DATE IN DATA: {last_date.strftime('%Y-%m-%d (%A)')}")

dates = generate_forecast_dates(last_date, 5, mock_today)
for i, d in enumerate(dates):
    print(f"FORECAST {i+1}: {d.strftime('%Y-%m-%d (%A)')}")
