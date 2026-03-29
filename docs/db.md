build the dabase in sqlite in the folder database/index-database.db
The database should have the following tables to store the data:
- indices_master (id, name, symbol,index_type(precious_metal,nifty,sector,thematic,liquid_fund,smallcap,midcap,largecap) description,is_active)
- index_data (id, index_id, date, open_price, close_price, high_price, low_price, volume, upload_date)
- index_calculated_data (id, index_id, calculation_date, daily_change, weekly_change, monthly_change, yearly_change,daily_change_percent,weekly_change_percent,monthly_change_percent,yearly_change_percent)
- user_settings (id, user_id, refresh_interval, theme, language)

insert the following indices in the indices_master table
**Supported Indices:**
- Precious metal ETFs: `SILVERBEES`, `GOLDBEES`
- Nifty ETFs: `NIFTYBEES`, `MONIFTY500`, `MOMENTUM50`
- Sector ETFs: `ITBEES`, `BANKBEES`, `PSUBNKBEES`, `AUTOBEES`, `JUNIORBEES`, `PHARMABEES`, `FMCGIETF`, `MID150BEES`, `OILIETF`, `ALPHA`, `INFRABEES`, `NEXT50IETF`, `HEALTHIETF`, `SMALLCAP`
- Thematic ETFs: `AONETOTAL`, `MOMOMENTUM`, `MONQ50`, `HDFCVALUE`, `HDFCGROWTH`, `HDFCMOMENT`, `MODEFENCE`, `EVINDIA`, `CONSUMIETF`, `GROWWRAIL`, `SELECTIPO`
- Liquid Fund: `LIQUIDBEES`


create a python script to load data from yfinance library for index_data table. It should traverse through all the indices in the indices_master table and load data for each index.

create a python script to calculate the index_calculated_data table. It should traverse through all the indices in the indices_master table and calculate the daily_change, weekly_change, monthly_change, yearly_change, daily_change_percent, weekly_change_percent, monthly_change_percent, yearly_change_percent for each index.

The script should be able to calculate data from a specific date or for a range of dates for the given index or for a list of indices. 


