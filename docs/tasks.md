# All Tasks

## 03-May-2026

1. Give option to run every script from frontend
2. Give option to review every data table from frontend 
3. Ability to compare local data with nse/tradingview 
4. Show the calculations logic on frontend
5. Move the DB to mysql 
6. Deploy the application online 
7. CI/CD pipeline for auto deployment 
8. CORS support 
9. DB call support 
10. WA integration 




## old
Create scripts to fetch data from yfinance and store it in the database table index_data for daily prices of indices. It should first check the database table to see what data is already present and only fetch the missing data. The list of indices to fetch should be taken from table indices_master.
6. Create another script that will calculate daily, weekly, monthly, and yearly changes for each index and store it in the database table index_calculated_data .It should first look if the data is already present. If it is, it should update the existing data. If not, it should calculate the changes and store it in the database.
8. Provide an option to manually refresh the data from the frontend. Upon using it, it should show the new data added to the tables. It should add data in index_data table and then calculate the changes and store it in index_calculated_data table.

1. Create a settings page to add/remove indices
2. Create a chart to show the indices performance trend and compare it with other indices
on the instrument page if the date is changed, recalculate the weekly , monthly , and yearly changes and niftybees return from the selected date to current date
Weekly dashboard page should show the weekly performance of top 3 indices for all the weeks starting from the selected date. This data should be stored in the database and the page should build a view from the database. The current week should be on top of the table. 

Monthly dashboard page should show the monthly performance of top 3 indices for all the months starting from the selected date. This data should be stored in the database and the page should build a view from the database. The current month should be on top of the table.
