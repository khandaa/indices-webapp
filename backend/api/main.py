from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
from datetime import datetime

# Add parent directory to path for importing backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_calculator import DataCalculator
from data_loader import DataLoader
from momentum_calculator import MomentumCalculator

app = FastAPI(
    title="Indices Web API",
    description="API for Indices Web Application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'index-database.db'))

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
        calculator = DataCalculator(DB_PATH)
        momentum_calc = MomentumCalculator(DB_PATH)
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
        calculator = DataCalculator(DB_PATH)
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
        calculator = DataCalculator(DB_PATH)
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
        momentum_calc = MomentumCalculator(DB_PATH)
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
        momentum_calc = MomentumCalculator(DB_PATH)
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
        calculator = DataCalculator(DB_PATH)
        calculator.connect()
        
        cursor = calculator.conn.cursor()
        cursor.execute("""
            SELECT 
                date,
                open_price,
                close_price,
                high_price,
                low_price,
                volume,
                ((close_price - open_price) / open_price * 100) as daily_change_percent
            FROM index_data
            WHERE index_id = ? AND close_price IS NOT NULL
            ORDER BY date DESC
            LIMIT ?
        """, (index_id, limit))
        
        results = cursor.fetchall()
        
        daily_prices = []
        previous_close = None
        
        for row in results:
            current_close = row[2]  # close_price
            change_from_previous = None
            
            if previous_close is not None and current_close is not None and previous_close != 0:
                change_from_previous = ((current_close - previous_close) / previous_close) * 100
            
            daily_prices.append({
                "date": row[0],
                "open_price": float(row[1]) if row[1] else None,
                "close_price": float(current_close) if current_close else None,
                "high_price": float(row[3]) if row[3] else None,
                "low_price": float(row[4]) if row[4] else None,
                "volume": int(row[5]) if row[5] else None,
                "daily_change_percent": float(row[6]) if row[6] else None,
                "change_from_previous": round(change_from_previous, 4) if change_from_previous is not None else None
            })
            
            previous_close = current_close
        
        calculator.disconnect()
        return {"daily_prices": daily_prices}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch daily prices: {str(e)}"}
        )

@app.get("/api/recommendations/weekly")
async def get_weekly_recommendations():
    """Get weekly recommendations with 3W cumulative returns"""
    try:
        calculator = DataCalculator(DB_PATH)
        momentum_calc = MomentumCalculator(DB_PATH)
        calculator.connect()
        momentum_calc.connect()
        
        cursor = calculator.conn.cursor()
        cursor.execute("""
            SELECT 
                im.id,
                im.name,
                im.symbol,
                icd.weekly_change,
                icd.weekly_change_percent,
                icd.calculation_date
            FROM indices_master im
            LEFT JOIN index_calculated_data icd ON im.id = icd.index_id 
                AND icd.calculation_date = (SELECT MAX(calculation_date) FROM index_calculated_data WHERE index_id = im.id)
            WHERE im.is_active = 1 AND icd.weekly_change_percent IS NOT NULL
            ORDER BY icd.weekly_change_percent DESC
        """)
        
        results = cursor.fetchall()
        
        recommendations = []
        for row in results:
            # Get momentum data for this index
            momentum_data = momentum_calc.get_latest_momentum_data(row[0])
            
            # Calculate week format (year-month-week)
            calculation_date = row[5]
            if calculation_date:
                date_obj = datetime.strptime(calculation_date, '%Y-%m-%d')
                year = date_obj.year
                month = date_obj.month
                week = date_obj.isocalendar()[1]
                week_str = f"{year}-{month:02d}-W{week:02d}"
            else:
                week_str = "N/A"
            
            recommendations.append({
                "week": week_str,
                "recommendation_date": calculation_date,
                "instrument": row[1],
                "symbol": row[2],
                "one_week_return": float(row[4]) if row[4] else None,
                "three_week_cumulative_return": momentum_data['three_week_cumulative_return']
            })
        
        # Sort by 3W cumulative return in descending order
        recommendations.sort(key=lambda x: x['three_week_cumulative_return'] or 0, reverse=True)
        
        calculator.disconnect()
        momentum_calc.disconnect()
        return {"recommendations": recommendations}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch weekly recommendations: {str(e)}"}
        )

@app.get("/api/recommendations/monthly")
async def get_monthly_recommendations():
    """Get monthly recommendations with 3M cumulative returns"""
    try:
        calculator = DataCalculator(DB_PATH)
        momentum_calc = MomentumCalculator(DB_PATH)
        calculator.connect()
        momentum_calc.connect()
        
        cursor = calculator.conn.cursor()
        cursor.execute("""
            SELECT 
                im.id,
                im.name,
                im.symbol,
                icd.monthly_change,
                icd.monthly_change_percent,
                icd.calculation_date
            FROM indices_master im
            LEFT JOIN index_calculated_data icd ON im.id = icd.index_id 
                AND icd.calculation_date = (SELECT MAX(calculation_date) FROM index_calculated_data WHERE index_id = im.id)
            WHERE im.is_active = 1 AND icd.monthly_change_percent IS NOT NULL
            ORDER BY icd.monthly_change_percent DESC
        """)
        
        results = cursor.fetchall()
        
        recommendations = []
        for row in results:
            # Get momentum data for this index
            momentum_data = momentum_calc.get_latest_momentum_data(row[0])
            
            # Calculate month format (year-month)
            calculation_date = row[5]
            if calculation_date:
                date_obj = datetime.strptime(calculation_date, '%Y-%m-%d')
                month_str = f"{date_obj.year}-{date_obj.month:02d}"
            else:
                month_str = "N/A"
            
            recommendations.append({
                "month": month_str,
                "recommendation_date": calculation_date,
                "instrument": row[1],
                "symbol": row[2],
                "one_month_return": float(row[4]) if row[4] else None,
                "three_month_cumulative_return": momentum_data['three_month_cumulative_return']
            })
        
        # Sort by 3M cumulative return in descending order
        recommendations.sort(key=lambda x: x['three_month_cumulative_return'] or 0, reverse=True)
        
        calculator.disconnect()
        momentum_calc.disconnect()
        return {"recommendations": recommendations}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to fetch monthly recommendations: {str(e)}"}
        )

@app.get("/api/performance/monthly")
async def get_monthly_top_performers():
    """Get top 3 monthly performers based on monthly change percent"""
    try:
        calculator = DataCalculator(DB_PATH)
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
