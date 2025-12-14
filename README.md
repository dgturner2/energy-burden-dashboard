# Energy Burden Dashboard

This project collects and updates labor market and energy service data
from the Bureau of Labor Statistics (BLS) to support analysis of energy
burden among U.S. households.

## Data Output

The main dataset created by this project will be:

data/bls_monthly.csv

Each row represents one month of data for one BLS time series.

### Columns in bls_monthly.csv

- date: Month of data (YYYY-MM-01)
- series_id: BLS time series identifier
- series_name: Descriptive name
- category: Energy services or unemployment
- area_type: Urban or suburban
- value: Numeric value
- units: Index or percent
- source: BLS

