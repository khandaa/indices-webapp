from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# os.environ['DB_TYPE'] = 'mysql'  # Comment out to allow environment variable control

from datetime import datetime

# Add parent directory to path for importing backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_calculator import DataCalculator
from data_loader import DataLoader
from momentum_calculator import MomentumCalculator
from date_utils import (
    get_past_weeks, get_upcoming_weeks, get_past_months, get_upcoming_months,
    format_week_display, format_month_display, get_week_from_date, get_month_from_date
)
from niftybees_helper import NiftybeesHelper
from whatif_simulator import WhatIfSimulator
from db import Database
from fastapi.responses import StreamingResponse
import csv
import io

app = FastAPI(
    title="Indices Web API",
    description="API for Indices Web Application",
    version="1.0.0"
)

# Environment-based configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3050,http://127.0.0.1:3000").split(",")
DB_TYPE = os.getenv('DB_TYPE', 'mysql')

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Indices Web API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

@app.get("/api/indices")
async def get_all_indices():
    """Get all indices with their latest performance data including momentum metrics"""
    try:
        calculator = DataCalculator()
        momentum_calc = MomentumCalculator()
        calculator.connect()
        momentum_calc.connect()
        
        # Get all active indices
        cursor = calculator.conn.cursor()
        cursor.execute("""
            SELECT 
                im.id,
                im.name,
                im.symbol,
                id.close_price,
                icd.daily_change,
                icd.weekly_change,
                icd.monthly_change,
                icd.yearly_change,
                icd.daily_change_percent,
                icd.weekly_change_percent,
                icd.monthly_change_percent,
                icd.yearly_change_percent,
                icd.calculation_date
            FROM indices_master im
            LEFT JOIN index_data id ON im.id = id.index_id 
                AND id.date = (SELECT MAX(date) FROM index_data WHERE index_id = im.id)
            LEFT JOIN index_calculated_data icd ON im.id = icd.index_id 
                AND icd.calculation_date = (SELECT MAX(calculation_date) FROM index_calculated_data WHERE index_id = im.id)
            WHERE im.is_active = 1
            ORDER BY im.name
        """)
        
        results = cursor.fetchall()
        
        indices = []
        for row in results:
            index_data = {
                "id": row[0],
                "name": row[1],
                "symbol": row[2],
                "current_price": float(row[3]) if row[3] else None,
                "daily_change": float(row[4]) if row[4] else None,
                "weekly_change": float(row[5]) if row[5] else None,
                "monthly_change": float(row[6]) if row[6] else None,
                "yearly_change": float(row[7]) if row[7] else None,
                "daily_change_percent": float(row[8]) if row[8] else None,
                "weekly_change_percent": float(row[9]) if row[9] else None,
                "monthly_change_percent": float(row[10]) if row[10] else None,
                "yearly_change_percent": float(row[11]) if row[11] else None,
                "calculation_date": row[12]
            }
            
            # Get momentum data for this index
            momentum_data = momentum_calc.get_latest_momentum_data(row[0])
            index_data.update({
                "three_week_cumulative_return": momentum_data['three_week_cumulative_return'],
                "three_month_cumulative_return": momentum_data['three_month_cumulative_return']
            })
            
            indices.append(index_data)
        
        calculator.disconnect()
        momentum_calc.disconnect()
        return {"indices": indices}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch indices: {str(e)}"}
        )

@app.get("/api/indices/{index_id}")
async def get_index_details(index_id: int):
    """Get detailed information for a specific index"""
    try:
        calculator = DataCalculator()
        calculator.connect()
        
        cursor = calculator.conn.cursor()
        cursor.execute("""
            SELECT 
                im.id,
                im.name,
                im.symbol,
                im.description,
                im.is_active
            FROM indices_master im
            WHERE im.id = ?
        """, (index_id,))
        
        result = cursor.fetchone()
        if not result:
            return JSONResponse(
                status_code=404,
                content={"error": "Index not found"}
            )
        
        index_info = {
            "id": result[0],
            "name": result[1],
            "symbol": result[2],
            "description": result[3],
            "is_active": bool(result[4])
        }
        
        calculator.disconnect()
        return index_info
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch index details: {str(e)}"}
        )

@app.get("/api/performance/weekly")
async def get_weekly_top_performers():
    """Get top 3 weekly performers based on weekly change percent"""
    try:
        calculator = DataCalculator()
        calculator.connect()
        
        cursor = calculator.conn.cursor()
        cursor.execute("""
            SELECT 
                im.id,
                im.name,
                im.symbol,
                id.close_price,
                icd.weekly_change,
                icd.weekly_change_percent,
                icd.calculation_date
            FROM indices_master im
            LEFT JOIN index_data id ON im.id = id.index_id 
                AND id.date = (SELECT MAX(date) FROM index_data WHERE index_id = im.id)
            LEFT JOIN index_calculated_data icd ON im.id = icd.index_id 
                AND icd.calculation_date = (SELECT MAX(calculation_date) FROM index_calculated_data WHERE index_id = im.id)
            WHERE im.is_active = 1 AND icd.weekly_change_percent IS NOT NULL
            ORDER BY icd.weekly_change_percent DESC
            LIMIT 3
        """)
        
        results = cursor.fetchall()
        
        top_performers = []
        for row in results:
            top_performers.append({
                "id": row[0],
                "name": row[1],
                "symbol": row[2],
                "current_price": float(row[3]) if row[3] else None,
                "weekly_change": float(row[4]) if row[4] else None,
                "weekly_change_percent": float(row[5]) if row[5] else None,
                "calculation_date": row[6]
            })
        
        calculator.disconnect()
        return {"top_performers": top_performers}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch weekly performers: {str(e)}"}
        )

@app.get("/api/momentum/{index_id}")
async def get_index_momentum(index_id: int):
    """Get momentum metrics for a specific index"""
    try:
        momentum_calc = MomentumCalculator()
        momentum_calc.connect()
        
        momentum_data = momentum_calc.get_latest_momentum_data(index_id)
        
        momentum_calc.disconnect()
        return momentum_data
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch momentum data: {str(e)}"}
        )

@app.post("/api/momentum/calculate")
async def calculate_momentum_metrics():
    """Calculate and update momentum metrics for all indices"""
    try:
        momentum_calc = MomentumCalculator()
        momentum_calc.connect()
        
        updated_count = momentum_calc.update_momentum_data_for_all_indices()
        
        momentum_calc.disconnect()
        return {"message": f"Updated momentum data for {updated_count} indices"}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to calculate momentum metrics: {str(e)}"}
        )

@app.get("/api/indices/{index_id}/daily-prices")
async def get_daily_prices(index_id: int, limit: int = 100):
    """Get daily price data for a specific index"""
    try:
        calculator = DataCalculator()
        calculator.connect()
        
        cursor = calculator.conn.cursor()
        
        # Get data ordered by date ascending to calculate previous close properly
        cursor.execute("""
            SELECT 
                date,
                open_price,
                close_price,
                high_price,
                low_price,
                volume
            FROM index_data
            WHERE index_id = ? AND close_price IS NOT NULL
            ORDER BY date ASC
        """, (index_id,))
        
        all_data = cursor.fetchall()
        
        daily_prices = []
        for i, row in enumerate(all_data):
            current_close = row[2]
            previous_close = all_data[i-1][2] if i > 0 else None
            
            daily_change_percent = None
            if previous_close is not None and previous_close != 0:
                daily_change_percent = ((current_close - previous_close) / previous_close) * 100
            
            daily_prices.append({
                "date": row[0],
                "open_price": float(row[1]) if row[1] else None,
                "close_price": float(current_close) if current_close else None,
                "high_price": float(row[3]) if row[3] else None,
                "low_price": float(row[4]) if row[4] else None,
                "volume": int(row[5]) if row[5] else None,
                "daily_change_percent": round(daily_change_percent, 4) if daily_change_percent is not None else None
            })
        
        # Take last 'limit' records and reverse for descending order
        daily_prices = daily_prices[-limit:] if len(daily_prices) > limit else daily_prices
        daily_prices.reverse()
        
        calculator.disconnect()
        return {"daily_prices": daily_prices}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch daily prices: {str(e)}"}
        )

@app.get("/api/performance/monthly")
async def get_monthly_top_performers():
    """Get top 3 monthly performers based on monthly change percent"""
    try:
        calculator = DataCalculator()
        calculator.connect()
        
        cursor = calculator.conn.cursor()
        cursor.execute("""
            SELECT 
                im.id,
                im.name,
                im.symbol,
                id.close_price,
                icd.monthly_change,
                icd.monthly_change_percent,
                icd.calculation_date
            FROM indices_master im
            LEFT JOIN index_data id ON im.id = id.index_id 
                AND id.date = (SELECT MAX(date) FROM index_data WHERE index_id = im.id)
            LEFT JOIN index_calculated_data icd ON im.id = icd.index_id 
                AND icd.calculation_date = (SELECT MAX(calculation_date) FROM index_calculated_data WHERE index_id = im.id)
            WHERE im.is_active = 1 AND icd.monthly_change_percent IS NOT NULL
            ORDER BY icd.monthly_change_percent DESC
            LIMIT 3
        """)
        
        results = cursor.fetchall()
        
        top_performers = []
        for row in results:
            top_performers.append({
                "id": row[0],
                "name": row[1],
                "symbol": row[2],
                "current_price": float(row[3]) if row[3] else None,
                "monthly_change": float(row[4]) if row[4] else None,
                "monthly_change_percent": float(row[5]) if row[5] else None,
                "calculation_date": row[6]
            })
        
        calculator.disconnect()
        return {"top_performers": top_performers}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch monthly performers: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050)


# ============================================================================
# NEW ENDPOINTS FOR GAPS IMPLEMENTATION
# ============================================================================

from date_utils import (
    get_past_weeks, get_upcoming_weeks, get_past_months, get_upcoming_months,
    format_week_display, format_month_display, get_week_from_date, get_month_from_date
)
from niftybees_helper import NiftybeesHelper

@app.get("/api/recommendations/weekly")
async def get_weekly_recommendations(past_weeks: int = 6, include_upcoming: bool = True):
    """Get weekly recommendations with configurable past weeks (Task 2.3)
    
    Parameters:
        past_weeks: Number of past weeks to include (default: 6)
        include_upcoming: Include upcoming week (default: true)
    """
    try:
        calculator = DataCalculator()
        momentum_calc = MomentumCalculator()
        niftybees_helper = NiftybeesHelper()
        
        calculator.connect()
        momentum_calc.connect()
        niftybees_helper.connect()
        
        # Get week lists
        past_week_list = get_past_weeks(past_weeks)
        upcoming_week_list = get_upcoming_weeks(1) if include_upcoming else []
        
        all_weeks = past_week_list + upcoming_week_list
        
        # Process in reverse chronological order (newest first)
        all_weeks = list(reversed(all_weeks))
        
        weeks_data = []
        for week_info in all_weeks:
            week_start = week_info['start_date']
            week_end = week_info['end_date']
            week_str = week_info['week']
            
            # Create fresh cursor for each query
            cursor = calculator.conn.cursor()
            
            # Get all indices with their 3W cumulative return as of week end date
            cursor.execute("SELECT id FROM indices_master WHERE is_active = 1")
            all_indices = cursor.fetchall()
            
            # Calculate 3W return for each index
            index_3w_returns = []
            for idx_row in all_indices:
                index_id = idx_row[0]
                three_week_return = momentum_calc.calculate_three_week_cumulative_return(index_id, week_end)
                if three_week_return is not None:
                    # Also get weekly change for this week
                    cursor.execute("""
                        SELECT MAX(weekly_change_percent) as max_weekly
                        FROM index_calculated_data
                        WHERE index_id = ? AND calculation_date >= ? AND calculation_date <= ?
                    """, (index_id, week_start, week_end))
                    result = cursor.fetchone()
                    weekly_change = result[0] if result else None
                    index_3w_returns.append({
                        'index_id': index_id,
                        'three_week_cumulative_return': three_week_return,
                        'weekly_change_percent': float(weekly_change) if weekly_change else None
                    })
            
            # Sort by 3W cumulative return (descending) and take top 3
            top_indices = sorted(index_3w_returns, key=lambda x: x['three_week_cumulative_return'], reverse=True)[:3]
            
            # Get the full data for each
            recommendations = []
            for rank, index_data in enumerate(top_indices):
                index_id = index_data['index_id']
                cursor.execute("""
                    SELECT id, name, symbol
                    FROM indices_master
                    WHERE id = ? AND is_active = 1
                """, (index_id,))
                row = cursor.fetchone()
                if row:
                    recommendations.append({
                        "rank": rank + 1,
                        "index_id": row[0],
                        "name": row[1],
                        "symbol": row[2],
                        "weekly_change_percent": index_data['weekly_change_percent'],
                        "three_week_cumulative_return": index_data['three_week_cumulative_return']
                    })
                    
                    # Store in weekly_recommendations table
                    cursor.execute("""
                        INSERT OR REPLACE INTO weekly_recommendations 
                        (index_id, week_start_date, week_end_date, rank, weekly_change_percent, 
                         three_week_cumulative_return, recommendation_date)
                        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                    """, (index_id, week_start, week_end, rank + 1, index_data['weekly_change_percent'],
                         index_data['three_week_cumulative_return']))
            
            calculator.conn.commit()
            max_results = top_indices  # For data_available check
            
            # Get Niftybees comparison
            niftybees_data = niftybees_helper.get_weekly_comparison(week_start, week_end)
            
            # Update niftybees columns if we have recommendations
            if recommendations and niftybees_data:
                niftybees_weekly = niftybees_data.get('niftybees_weekly_change_percent')
                niftybees_3w = niftybees_data.get('niftybees_three_week_cumulative_return')
                for rec in recommendations:
                    cursor.execute("""
                        UPDATE weekly_recommendations 
                        SET niftybees_weekly_change_percent = ?, niftybees_three_week_cumulative_return = ?
                        WHERE index_id = ? AND week_start_date = ? AND rank = ?
                    """, (niftybees_weekly, niftybees_3w, rec['index_id'], week_start, rec['rank']))
                calculator.conn.commit()
            
            # Check if data exists
            data_available = len(max_results) > 0
            
            weeks_data.append({
                "week": week_str,
                "week_display": format_week_display(week_str),
                "start_date": week_start,
                "end_date": week_end,
                "is_past": week_info['is_past'],
                "data_available": data_available,
                "recommendations": recommendations,
                "niftybees": {
                    "weekly_change_percent": niftybees_data.get('niftybees_weekly_change_percent'),
                    "three_week_cumulative_return": niftybees_data.get('niftybees_three_week_cumulative_return')
                } if data_available else None
            })
        
        calculator.disconnect()
        momentum_calc.disconnect()
        niftybees_helper.disconnect()
        
        return {"weeks": weeks_data, "count": len(weeks_data)}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch weekly recommendations: {str(e)}"}
        )


@app.get("/api/recommendations/monthly")
async def get_monthly_recommendations(past_months: int = 4, include_upcoming: bool = True):
    """Get monthly recommendations with configurable past months (Task 2.4)
    
    Parameters:
        past_months: Number of past months to include (default: 4)
        include_upcoming: Include upcoming month (default: true)
    """
    try:
        calculator = DataCalculator()
        momentum_calc = MomentumCalculator()
        niftybees_helper = NiftybeesHelper()
        
        calculator.connect()
        momentum_calc.connect()
        niftybees_helper.connect()
        
        # Get month lists
        past_month_list = get_past_months(past_months)
        upcoming_month_list = get_upcoming_months(1) if include_upcoming else []
        
        all_months = past_month_list + upcoming_month_list
        
        # Process in reverse chronological order (newest first)
        all_months = list(reversed(all_months))
        
        months_data = []
        for month_info in all_months:
            month_start = month_info['start_date']
            month_end = month_info['end_date']
            month_str = month_info['month']
            
            # Create fresh cursor for each query
            cursor = calculator.conn.cursor()
            
            # Get all indices with their 3M cumulative return as of month end date
            cursor.execute("SELECT id FROM indices_master WHERE is_active = 1")
            all_indices = cursor.fetchall()
            
            # Calculate 3M return for each index
            index_3m_returns = []
            for idx_row in all_indices:
                index_id = idx_row[0]
                three_month_return = momentum_calc.calculate_three_month_cumulative_return(index_id, month_end)
                if three_month_return is not None:
                    # Also get monthly change for this month
                    cursor.execute("""
                        SELECT MAX(monthly_change_percent) as max_monthly
                        FROM index_calculated_data
                        WHERE index_id = ? AND calculation_date >= ? AND calculation_date <= ?
                    """, (index_id, month_start, month_end))
                    result = cursor.fetchone()
                    monthly_change = result[0] if result else None
                    index_3m_returns.append({
                        'index_id': index_id,
                        'three_month_cumulative_return': three_month_return,
                        'monthly_change_percent': float(monthly_change) if monthly_change else None
                    })
            
            # Sort by 3M cumulative return (descending) and take top 3
            top_indices = sorted(index_3m_returns, key=lambda x: x['three_month_cumulative_return'], reverse=True)[:3]
            
            # Get the full data for each
            recommendations = []
            for rank, index_data in enumerate(top_indices):
                index_id = index_data['index_id']
                cursor.execute("""
                    SELECT id, name, symbol
                    FROM indices_master
                    WHERE id = ? AND is_active = 1
                """, (index_id,))
                row = cursor.fetchone()
                if row:
                    recommendations.append({
                        "rank": rank + 1,
                        "index_id": row[0],
                        "name": row[1],
                        "symbol": row[2],
                        "monthly_change_percent": index_data['monthly_change_percent'],
                        "three_month_cumulative_return": index_data['three_month_cumulative_return']
                    })
                    
                    # Store in monthly_recommendations table
                    cursor.execute("""
                        INSERT OR REPLACE INTO monthly_recommendations 
                        (index_id, month_start_date, month_end_date, rank, monthly_change_percent, 
                         three_month_cumulative_return, recommendation_date)
                        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                    """, (index_id, month_start, month_end, rank + 1, index_data['monthly_change_percent'],
                         index_data['three_month_cumulative_return']))
            
            calculator.conn.commit()
            max_results = top_indices  # For data_available check
            
            # Get Niftybees comparison
            niftybees_data = niftybees_helper.get_monthly_comparison(month_start, month_end)
            
            # Update niftybees columns if we have recommendations
            if recommendations and niftybees_data:
                niftybees_monthly = niftybees_data.get('niftybees_monthly_change_percent')
                niftybees_3m = niftybees_data.get('niftybees_three_month_cumulative_return')
                for rec in recommendations:
                    cursor.execute("""
                        UPDATE monthly_recommendations 
                        SET niftybees_monthly_change_percent = ?, niftybees_three_month_cumulative_return = ?
                        WHERE index_id = ? AND month_start_date = ? AND rank = ?
                    """, (niftybees_monthly, niftybees_3m, rec['index_id'], month_start, rec['rank']))
                calculator.conn.commit()
            
            # Check if data exists
            data_available = len(max_results) > 0
            
            months_data.append({
                "month": month_str,
                "month_display": format_month_display(month_str),
                "start_date": month_start,
                "end_date": month_end,
                "is_past": month_info['is_past'],
                "data_available": data_available,
                "recommendations": recommendations,
                "niftybees": {
                    "monthly_change_percent": niftybees_data.get('niftybees_monthly_change_percent'),
                    "three_month_cumulative_return": niftybees_data.get('niftybees_three_month_cumulative_return')
                } if data_available else None
            })
        
        calculator.disconnect()
        momentum_calc.disconnect()
        niftybees_helper.disconnect()
        
        return {"months": months_data, "count": len(months_data)}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch monthly recommendations: {str(e)}"}
        )


@app.get("/api/recommendations/selected")

@app.get("/api/recommendations/upcoming/weekly")
async def get_upcoming_weekly_recommendation():
    """Get upcoming week recommendation (Task 2.7)"""
    try:
        calculator = DataCalculator()
        momentum_calc = MomentumCalculator()
        
        calculator.connect()
        momentum_calc.connect()
        
        # Get next week
        upcoming_weeks = get_upcoming_weeks(1)
        
        if not upcoming_weeks:
            return {"recommendations": [], "message": "No upcoming week data"}
        
        week_info = upcoming_weeks[0]
        week_start = week_info['start_date']
        week_end = week_info['end_date']
        
        cursor = calculator.conn.cursor()
        cursor.execute("""
            SELECT 
                im.id,
                im.name,
                im.symbol,
                icd.weekly_change_percent
            FROM indices_master im
            LEFT JOIN index_calculated_data icd ON im.id = icd.index_id 
                AND icd.calculation_date >= ? AND icd.calculation_date <= ?
            WHERE im.is_active = 1 AND icd.weekly_change_percent IS NOT NULL
            ORDER BY icd.weekly_change_percent DESC
            LIMIT 3
        """, (week_start, week_end))
        
        results = cursor.fetchall()
        
        recommendations = []
        for i, row in enumerate(results):
            momentum_data = momentum_calc.get_latest_momentum_data(row[0])
            recommendations.append({
                "rank": i + 1,
                "index_id": row[0],
                "name": row[1],
                "symbol": row[2],
                "weekly_change_percent": float(row[3]) if row[3] else None,
                "three_week_cumulative_return": momentum_data.get('three_week_cumulative_return')
            })
        
        calculator.disconnect()
        momentum_calc.disconnect()
        
        return {
            "week": week_info['week'],
            "start_date": week_start,
            "end_date": week_end,
            "recommendations": recommendations,
            "note": "Based on current/past performance for prediction"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch upcoming recommendation: {str(e)}"}
        )


@app.get("/api/recommendations/upcoming/monthly")
async def get_upcoming_monthly_recommendation():
    """Get upcoming month recommendation (Task 2.7)"""
    try:
        calculator = DataCalculator()
        momentum_calc = MomentumCalculator()
        
        calculator.connect()
        momentum_calc.connect()
        
        # Get next month
        upcoming_months = get_upcoming_months(1)
        
        if not upcoming_months:
            return {"recommendations": [], "message": "No upcoming month data"}
        
        month_info = upcoming_months[0]
        month_start = month_info['start_date']
        month_end = month_info['end_date']
        
        cursor = calculator.conn.cursor()
        cursor.execute("""
            SELECT 
                im.id,
                im.name,
                im.symbol,
                icd.monthly_change_percent
            FROM indices_master im
            LEFT JOIN index_calculated_data icd ON im.id = icd.index_id 
                AND icd.calculation_date >= ? AND icd.calculation_date <= ?
            WHERE im.is_active = 1 AND icd.monthly_change_percent IS NOT NULL
            ORDER BY icd.monthly_change_percent DESC
            LIMIT 3
        """, (month_start, month_end))
        
        results = cursor.fetchall()
        
        recommendations = []
        for i, row in enumerate(results):
            momentum_data = momentum_calc.get_latest_momentum_data(row[0])
            recommendations.append({
                "rank": i + 1,
                "index_id": row[0],
                "name": row[1],
                "symbol": row[2],
                "monthly_change_percent": float(row[3]) if row[3] else None,
                "three_month_cumulative_return": momentum_data.get('three_month_cumulative_return')
            })
        
        calculator.disconnect()
        momentum_calc.disconnect()
        
        return {
            "month": month_info['month'],
            "start_date": month_start,
            "end_date": month_end,
            "recommendations": recommendations,
            "note": "Based on current/past performance for prediction"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch upcoming recommendation: {str(e)}"}
        )


@app.get("/api/data/freshness")
async def check_data_freshness():
    """Check data freshness - when each index was last updated (Task 2.8)"""
    try:
        with Database('mysql') as db:
            results = db.fetch_all("""
                SELECT 
                    im.id,
                    im.name,
                    im.symbol,
                    MAX(id.date) as last_data_date,
                    MAX(icd.calculation_date) as last_calc_date
                FROM indices_master im
                LEFT JOIN index_data id ON im.id = id.index_id
                LEFT JOIN index_calculated_data icd ON im.id = icd.index_id
                WHERE im.is_active = 1
                GROUP BY im.id
                ORDER BY im.name
            """)
        
        today = datetime.now().strftime('%Y-%m-%d')
        freshness = []
        
        for row in results:
            last_date = row[3]
            is_fresh = last_date == today if last_date else False
            
            freshness.append({
                "index_id": row[0],
                "name": row[1],
                "symbol": row[2],
                "last_data_date": last_date,
                "last_calculation_date": row[4],
                "is_fresh": is_fresh,
                "needs_refresh": not is_fresh
            })
        
        total_fresh = sum(1 for f in freshness if f['is_fresh'])
        total_needs_refresh = sum(1 for f in freshness if f['needs_refresh'])
        
        return {
            "indices": freshness,
            "summary": {
                "total": len(freshness),
                "fresh": total_fresh,
                "needs_refresh": total_needs_refresh
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to check freshness: {str(e)}"}
        )


@app.post("/api/recommendations/refresh")
async def refresh_data(range: str = "all"):
    """Refresh data for weekly/monthly recommendations (Task 2.5)
    
    Parameters:
        range: "weekly", "monthly", or "all"
    """
    try:
        from datetime import timedelta
        
        loader = DataLoader()
        calculator = DataCalculator()
        momentum_calc = MomentumCalculator()
        
        loader.connect()
        calculator.connect()
        momentum_calc.connect()
        
        refreshed = []
        
        # Get all indices
        cursor = loader.conn.cursor()
        cursor.execute("SELECT id, symbol FROM indices_master WHERE is_active = 1")
        indices = cursor.fetchall()
        
        today = datetime.now()
        yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        for index_id, symbol in indices:
            # Check if data exists
            cursor.execute("SELECT MAX(date) FROM index_data WHERE index_id = ?", (index_id,))
            last_date = cursor.fetchone()[0]
            
            # Fetch missing data if needed
            if last_date != today_str:
                try:
                    loader.load_data_for_specific_indices([symbol])
                    refreshed.append(f"{symbol}: data loaded")
                except Exception as e:
                    refreshed.append(f"{symbol}: failed - {str(e)}")
        
        # Recalculate metrics
        if range in ["weekly", "all"]:
            calculator.calculate_for_all_indices()
            refreshed.append("weekly calculations completed")
        
        if range in ["monthly", "all"]:
            calculator.calculate_for_all_indices()
            refreshed.append("monthly calculations completed")
        
        # Update momentum data
        momentum_calc.update_momentum_data_for_all_indices()
        refreshed.append("momentum data updated")
        
        loader.disconnect()
        calculator.disconnect()
        momentum_calc.disconnect()
        
        return {"message": "Data refresh completed", "details": refreshed}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to refresh data: {str(e)}"}
        )


# What-If Simulation Endpoints

@app.get("/api/whatif/simulate")
async def run_simulation(
    initial_amount: float = 100000,
    start_date: str = None,
    end_date: str = None,
    frequency: str = "weekly",
    allocation_1: float = 50,
    allocation_2: float = 30,
    allocation_3: float = 20,
    save_scenario: bool = False,
    scenario_name: str = None
):
    """Run investment simulation"""
    try:
        simulator = WhatIfSimulator()
        simulator.connect()
        
        # Run simulation
        result = simulator.simulate(
            initial_amount=initial_amount,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            allocation_1=allocation_1,
            allocation_2=allocation_2,
            allocation_3=allocation_3
        )
        
        # Save scenario if requested
        scenario_id = None
        if save_scenario and scenario_name:
            scenario_id = simulator.save_scenario(
                name=scenario_name,
                description=f"{frequency.capitalize()} simulation starting {start_date}",
                initial_amount=initial_amount,
                frequency=frequency,
                allocation_1=allocation_1,
                allocation_2=allocation_2,
                allocation_3=allocation_3,
                start_date=start_date,
                end_date=end_date
            )
            simulator.save_simulation_results(scenario_id, result['results'])
        
        simulator.disconnect()
        
        return {
            "simulation": result,
            "scenario_id": scenario_id
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Simulation failed: {str(e)}"}
        )


@app.get("/api/whatif/scenarios")
async def get_scenarios():
    """Get all saved scenarios"""
    try:
        simulator = WhatIfSimulator()
        simulator.connect()
        scenarios = simulator.get_scenarios()
        simulator.disconnect()
        return {"scenarios": scenarios}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get scenarios: {str(e)}"}
        )


@app.get("/api/whatif/scenarios/{scenario_id}")
async def get_scenario(scenario_id: int):
    """Get a specific scenario with simulation results"""
    try:
        simulator = WhatIfSimulator()
        simulator.connect()
        scenario = simulator.get_scenario(scenario_id)
        results = simulator.get_simulation_results(scenario_id)
        simulator.disconnect()
        
        if not scenario:
            return JSONResponse(status_code=404, content={"error": "Scenario not found"})
        
        return {"scenario": scenario, "results": results}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get scenario: {str(e)}"}
        )


@app.post("/api/whatif/scenarios")
async def create_scenario(
    name: str,
    description: str = "",
    initial_amount: float = 100000,
    frequency: str = "weekly",
    allocation_1: float = 50,
    allocation_2: float = 30,
    allocation_3: float = 20,
    start_date: str = None,
    end_date: str = None
):
    """Create a new scenario"""
    try:
        simulator = WhatIfSimulator()
        simulator.connect()
        scenario_id = simulator.save_scenario(
            name=name, description=description, initial_amount=initial_amount,
            frequency=frequency, allocation_1=allocation_1, allocation_2=allocation_2,
            allocation_3=allocation_3, start_date=start_date, end_date=end_date
        )
        scenario = simulator.get_scenario(scenario_id)
        simulator.disconnect()
        return {"scenario_id": scenario_id, "scenario": scenario}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create scenario: {str(e)}"}
        )


@app.put("/api/whatif/scenarios/{scenario_id}")
async def update_scenario(scenario_id: int, **kwargs):
    """Update a scenario"""
    try:
        simulator = WhatIfSimulator()
        simulator.connect()
        simulator.update_scenario(scenario_id, **kwargs)
        scenario = simulator.get_scenario(scenario_id)
        simulator.disconnect()
        return {"scenario": scenario}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to update scenario: {str(e)}"}
        )


@app.delete("/api/whatif/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: int):
    """Delete a scenario"""
    try:
        simulator = WhatIfSimulator()
        simulator.connect()
        simulator.delete_scenario(scenario_id)
        simulator.disconnect()
        return {"message": "Scenario deleted"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to delete scenario: {str(e)}"}
        )


@app.get("/api/whatif/scenarios/{scenario_id}/export")
async def export_scenario_csv(scenario_id: int):
    """Export simulation results as CSV"""
    try:
        simulator = WhatIfSimulator()
        simulator.connect()
        scenario = simulator.get_scenario(scenario_id)
        results = simulator.get_simulation_results(scenario_id)
        simulator.disconnect()
        
        if not scenario:
            return JSONResponse(status_code=404, content={"error": "Scenario not found"})
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Period", "Start Date", "End Date",
            "Rec 1", "Rec 2", "Rec 3",
            "Allocation 1%", "Allocation 2%", "Allocation 3%",
            "Invested 1", "Invested 2", "Invested 3",
            "Final 1", "Final 2", "Final 3",
            "Return 1%", "Return 2%", "Return 3%",
            "Strategy Start", "Strategy End", "Strategy Return%",
            "Niftybees Start", "Niftybees End", "Niftybees Return%"
        ])
        
        # Write data
        for r in results:
            strategy_return = ((r['strategy_value_end'] - r['strategy_value_start']) / r['strategy_value_start'] * 100) if r['strategy_value_start'] else 0
            niftybees_return = ((r['niftybees_value_end'] - r['niftybees_value_start']) / r['niftybees_value_start'] * 100) if r['niftybees_value_start'] else 0
            
            writer.writerow([
                r['period_number'],
                r['period_start_date'],
                r['period_end_date'],
                r.get('recommendation_1_symbol') or '',
                r.get('recommendation_2_symbol') or '',
                r.get('recommendation_3_symbol') or '',
                r['allocation_1_percent'],
                r['allocation_2_percent'],
                r['allocation_3_percent'],
                r.get('amount_invested_1', 0),
                r.get('amount_invested_2', 0),
                r.get('amount_invested_3', 0),
                r.get('final_amount_1', 0),
                r.get('final_amount_2', 0),
                r.get('final_amount_3', 0),
                r.get('return_percent_1', 0),
                r.get('return_percent_2', 0),
                r.get('return_percent_3', 0),
                r['strategy_value_start'],
                r['strategy_value_end'],
                f"{strategy_return:.2f}",
                r['niftybees_value_start'],
                r['niftybees_value_end'],
                f"{niftybees_return:.2f}"
            ])
        
        output.seek(0)
        
        filename = f"whatif_{scenario['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to export: {str(e)}"}
        )
