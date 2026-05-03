#!/usr/bin/env python3
"""Generate weekly and monthly recommendations"""

import mysql.connector
from datetime import datetime, timedelta

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Emp10yDEX',
    database='indices_db',
    unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'
)
cursor = conn.cursor(dictionary=True)

today = datetime.now()
week_start = today - timedelta(days=today.weekday())
week_end = week_start + timedelta(days=6)

print(f'Generating recommendations for:')
print(f'  Week: {week_start.strftime("%Y-%m-%d")} to {week_end.strftime("%Y-%m-%d")}')

# Delete old weekly recommendations for this week
cursor.execute('DELETE FROM weekly_recommendations WHERE week_start_date = %s', (week_start.strftime('%Y-%m-%d'),))

# Get weekly recommendations based on 3-week momentum
cursor.execute('''
    SELECT 
        im.id as index_id,
        im.symbol,
        im.name,
        icd.weekly_change_percent,
        icd.daily_change_percent,
        imd.three_week_cumulative_return
    FROM indices_master im
    LEFT JOIN index_calculated_data icd ON im.id = icd.index_id 
        AND icd.calculation_date = (SELECT MAX(calculation_date) FROM index_calculated_data WHERE index_id = im.id)
    LEFT JOIN index_momentum_data imd ON im.id = imd.index_id 
        AND imd.calculation_date = (SELECT MAX(calculation_date) FROM index_momentum_data WHERE index_id = im.id)
    WHERE im.is_active = 1 AND imd.three_week_cumulative_return IS NOT NULL
    ORDER BY imd.three_week_cumulative_return DESC
    LIMIT 10
''')

results = cursor.fetchall()
print('\n=== WEEKLY RECOMMENDATIONS ===')
for i, row in enumerate(results):
    rank = i + 1
    print(f"  {rank}. {row['symbol']} ({row['name']})")
    print(f"      1W: {row['weekly_change_percent']}%, 3W: {row['three_week_cumulative_return']}%")
    
    cursor.execute('''
        INSERT INTO weekly_recommendations 
        (index_id, week_start_date, week_end_date, rank, weekly_change_percent, three_week_cumulative_return)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (
        row['index_id'],
        week_start.strftime('%Y-%m-%d'),
        week_end.strftime('%Y-%m-%d'),
        rank,
        row['weekly_change_percent'],
        row['three_week_cumulative_return']
    ))

conn.commit()
print(f'\nGenerated {len(results)} weekly recommendations')

# Monthly
month_start = today.replace(day=1)
next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
month_end = next_month - timedelta(days=1)

print(f'\n=== MONTHLY RECOMMENDATIONS ===')
print(f'  Month: {month_start.strftime("%Y-%m-%d")} to {month_end.strftime("%Y-%m-%d")}')

# Delete old monthly recommendations for this month
cursor.execute('DELETE FROM monthly_recommendations WHERE month_start_date = %s', (month_start.strftime('%Y-%m-%d'),))

cursor.execute('''
    SELECT 
        im.id as index_id,
        im.symbol,
        im.name,
        icd.monthly_change_percent,
        icd.daily_change_percent,
        imd.three_month_cumulative_return
    FROM indices_master im
    LEFT JOIN index_calculated_data icd ON im.id = icd.index_id 
        AND icd.calculation_date = (SELECT MAX(calculation_date) FROM index_calculated_data WHERE index_id = im.id)
    LEFT JOIN index_momentum_data imd ON im.id = imd.index_id 
        AND imd.calculation_date = (SELECT MAX(calculation_date) FROM index_momentum_data WHERE index_id = im.id)
    WHERE im.is_active = 1 AND imd.three_month_cumulative_return IS NOT NULL
    ORDER BY imd.three_month_cumulative_return DESC
    LIMIT 10
''')

monthly_results = cursor.fetchall()
for i, row in enumerate(monthly_results):
    rank = i + 1
    print(f"  {rank}. {row['symbol']} ({row['name']})")
    print(f"      1M: {row['monthly_change_percent']}%, 3M: {row['three_month_cumulative_return']}%")
    
    cursor.execute('''
        INSERT INTO monthly_recommendations 
        (index_id, month_start_date, month_end_date, rank, monthly_change_percent, three_month_cumulative_return)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (
        row['index_id'],
        month_start.strftime('%Y-%m-%d'),
        month_end.strftime('%Y-%m-%d'),
        rank,
        row['monthly_change_percent'],
        row['three_month_cumulative_return']
    ))

conn.commit()
print(f'\nGenerated {len(monthly_results)} monthly recommendations')

conn.close()
print('\n✓ Recommendations generated successfully!')