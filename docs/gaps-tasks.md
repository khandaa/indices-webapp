# What-If Investment Simulator - Implementation Tasks

## Overview
Create a what-if page where users can simulate investment scenarios comparing:
- Strategy: Following weekly/monthly recommendations
- Benchmark: Buy-and-hold Niftybees

---

## Database Schema

- [x] Create `whatif_scenarios` table to store user scenarios
  - `id`, `name`, `description`, `initial_amount`, `frequency` (weekly/monthly), `allocation_1`, `allocation_2`, `allocation_3`, `created_at`, `updated_at`
  - `investment_start_date`, `investment_end_date`

- [x] Create `whatif_simulation_results` table for storing simulation data
  - `id`, `scenario_id`, `name`, `period_number`, `period_start_date`, `period_end_date`, `recommendations_used`, `strategy_value`, `niftybees_value`, `created_at`, 

---

## Backend API

### Task 1: Create Scenario Management Endpoints
- [x] `POST /api/whatif/scenarios` - Create a new scenario
- [x] `GET /api/whatif/scenarios` - List all scenarios for user
- [x] `GET /api/whatif/scenarios/{id}` - Get scenario details
- [x] `PUT /api/whatif/scenarios/{id}` - Update scenario
- [x] `DELETE /api/whatif/scenarios/{id}` - Delete scenario

### Task 2: Create Simulation Logic
- [x] Implement `calculate_weekly_simulation()` - Simulate weekly recommendation strategy
  - Use stored `weekly_recommendations` data
  - Apply allocation % to each recommendation (rank 1, 2, 3)
  - Calculate portfolio value after each week
  - Use next week's starting value as current week's ending value

- [x] Implement `calculate_monthly_simulation()` - Simulate monthly recommendation strategy
  - Use stored `monthly_recommendations` data
  - Apply same allocation logic per month

- [x] Implement `calculate_niftybees_benchmark()` 
  - Buy and hold Niftybees for the same period
  - Track value based on Niftybees price changes

- [x] `GET /api/whatif/simulate` - Run simulation
  - Accept scenario parameters
  - Return simulation results with periodic breakdown
  - Calculate final returns for both strategies

### Task 3: Add CSV Export Endpoint
- [x] `GET /api/whatif/scenarios/{id}/export` - Export simulation results as CSV

---

## Frontend

### Task 4: Create What-If Page Component
**Location:** `frontend/src/pages/WhatIf.tsx`

- [x] Layout with two sections: Scenario Configuration and Results

### Task 5: Scenario Configuration Form
- [x] Initial investment amount input (default: 100000)
- [x] Frequency selector: Weekly / Monthly
- [x] Start date picker
- [x] End date picker
- [x] Allocation inputs:
  - Top recommendation: ___% (default: 50%)
  - Second recommendation: ___% (default: 30%)
  - Third recommendation: ___% (default: 20%)
  - (Should validate to 100% total)
- [x] Scenario name input (for saving)
- [x] Buttons: Run Simulation | Save Scenario | Load Scenario

### Task 6: Simulation Results Display
- [x] Summary cards:
  - Initial Investment
  - Final Strategy Value
  - Final Niftybees Value
  - Strategy Return %
  - Niftybees Return %
  - Outperformance (Strategy vs Niftybees)

- [x] Line chart showing:
  - Strategy value over time
  - Niftybees value over time
  - Both lines on same chart (normalized or absolute)

- [x] Detailed table:
  - Period | Start Date | End Date | Recommendations | Strategy Value | Niftybees Value

### Task 7: Saved Scenarios Management
- [x] Dropdown/modal to load saved scenarios
- [x] List view of saved scenarios
- [x] Delete scenario option

### Task 8: Export Functionality
- [x] "Export CSV" button
- [x] Download simulation results as CSV file

### Task 9: Navigation
- [x] Add route in `App.tsx` for `/whatif`
- [x] Add link in navigation menu

---

## Backend Implementation Details

### Simulation Algorithm (Weekly)

```
For each week in range:
  1. Get top 3 recommendations for this week from database
  2. Allocate investment:
     - amount_1 = initial_value * allocation_1
     - amount_2 = initial_value * allocation_2
     - amount_3 = initial_value * allocation_3
  3. Calculate returns:
     - value_1 = amount_1 * (1 + recommendation_1.weekly_change_percent / 100)
     - value_2 = amount_2 * (1 + recommendation_2.weekly_change_percent / 100)
     - value_3 = amount_3 * (1 + recommendation_3.weekly_change_percent / 100)
  4. Total strategy value = value_1 + value_2 + value_3
  5. Record period data
  6. Set initial_value = total strategy value for next week
```

### Niftybees Benchmark

```
For each week in range:
  1. Get Niftybees weekly change for this week
  2. niftybees_value = niftybees_value * (1 + weekly_change_percent / 100)
  3. Record period data
```

---

## Files Created/Modified

- `backend/setup_database.py` - Added whatif_scenarios and whatif_simulation_results tables
- `backend/whatif_simulator.py` - Simulation logic class
- `backend/api/main.py` - API endpoints for whatif
- `frontend/src/services/api.ts` - API service methods
- `frontend/src/pages/WhatIf.tsx` - What-If page component
- `frontend/src/App.tsx` - Added navigation route

---

## Testing

- [x] Test weekly simulation with sample data
- [x] Test monthly simulation with sample data
- [x] Verify allocation percentages sum to 100%
- [ ] Test CSV export
- [x] Test scenario save/load functionality

---

## Priority Order

1. **Database Schema** - Foundation ✓
2. **Backend API: Scenario CRUD** - Basic operations ✓
3. **Backend: Simulation Logic** - Core feature ✓
4. **Frontend: What-If Page** - UI implementation ✓
5. **Frontend: Results Display** - Charts and tables ✓
6. **CSV Export** - Data export ✓
7. **Saved Scenarios** - Persistence ✓