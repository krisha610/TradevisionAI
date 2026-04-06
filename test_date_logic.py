from datetime import datetime, timedelta

def generate_forecast_dates(last_date, forecast_days):
    forecast_dates = []
    current_date = last_date
    while len(forecast_dates) < forecast_days:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # 0=Mon, 4=Fri
            forecast_dates.append(current_date)
    return forecast_dates

# Test Scenarios
# Friday, April 3rd, 2026 (Friday is 4)
last_date_fri = datetime(2026, 4, 3) 
print(f"Last Date: Friday {last_date_fri.strftime('%Y-%m-%d')}")
dates = generate_forecast_dates(last_date_fri, 5)
for i, d in enumerate(dates):
    print(f"Day {i+1}: {d.strftime('%Y-%m-%d (%A)')}")

# Wednesday, April 1st, 2026 (Wednesday is 2)
last_date_wed = datetime(2026, 4, 1) 
print(f"\nLast Date: Wednesday {last_date_wed.strftime('%Y-%m-%d')}")
dates_wed = generate_forecast_dates(last_date_wed, 5)
for i, d in enumerate(dates_wed):
    print(f"Day {i+1}: {d.strftime('%Y-%m-%d (%A)')}")
