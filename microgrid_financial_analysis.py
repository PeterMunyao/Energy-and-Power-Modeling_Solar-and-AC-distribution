import numpy as np
import pandas as pd
from scipy.optimize import fsolve
from fpdf import FPDF  # Import the FPDF library

# Define parameters for the microgrid system
electricity_price = 0.08  # USD per kWh
discount_rate = 0.08        # 8% discount rate
project_lifetime = 25       # Years

# Component costs (example values)
data = {
    'Component': ['Solar Panels', 'Battery', 'Inverter', 'DC Conductors'],
    'Initial_Cost': [11000, 28000, 2500, 8000],  # Example costs in USD
    'O&M_Cost_Annual': [100, 300, 150, 150],      # Example annual O&M costs
    'Lifespan': [25, 10, 15, 20]                 # Lifespan in years
}
df = pd.DataFrame(data)

# User input for subsidies and tax reliefs
subsidy_amount = float(input("Enter the total subsidy amount (USD): "))
tax_relief_percentage = float(input("Enter the tax relief percentage (as a decimal, e.g., 0.15 for 15%): "))

# Calculate total initial investment and annual operating costs
initial_investment = df['Initial_Cost'].sum()  # Total initial cost of all components
initial_investment_after_subsidy = initial_investment - subsidy_amount  # Adjust for subsidy
annual_om_cost = df['O&M_Cost_Annual'].sum()   # Total annual O&M costs

# Calculate tax relief amount
tax_relief_amount = initial_investment_after_subsidy * tax_relief_percentage

# Yearly energy production (example value)
yearly_energy_production = 13712  # kWh

# Calculate annual revenue from selling electricity
annual_revenue = yearly_energy_production * electricity_price

# Calculate net cash flow, accounting for tax relief
net_cash_flow = annual_revenue - annual_om_cost + tax_relief_amount

# Define the NPV function
def calculate_npv(initial_investment, cash_flows, discount_rate):
    """Calculates the Net Present Value (NPV) of a project."""
    npv = -initial_investment
    for year, cash_flow in enumerate(cash_flows, 1):
        npv += cash_flow / (1 + discount_rate)**year
    return npv

# Define the function to find IRR
def calculate_irr(initial_investment, cash_flows):
    """Calculates the Internal Rate of Return (IRR)."""
    def npv_equation(rate):
        npv = -initial_investment
        for year, cash_flow in enumerate(cash_flows, 1):
            npv += cash_flow / (1 + rate)**year
        return npv

    irr_value = fsolve(npv_equation, 0.1)[0]  # Initial guess is 0.1 (10%)
    return irr_value

# Prepare cash flows for NPV and IRR calculations
cash_flows = [net_cash_flow] * project_lifetime  # Assume constant cash flow each year

# Calculate NPV and IRR
npv_value = calculate_npv(initial_investment_after_subsidy, cash_flows, discount_rate)
irr_value = calculate_irr(initial_investment_after_subsidy, cash_flows)

# Calculate Levelized Cost of Energy (LCOE)
total_annualized_cost = annual_om_cost + (initial_investment_after_subsidy / project_lifetime)
lcoe_value = total_annualized_cost / yearly_energy_production

# Calculate years required to break even
break_even_years = initial_investment_after_subsidy / net_cash_flow

# Calculate total profits after balance of system capital cost
total_profit_after_break_even = (net_cash_flow * project_lifetime) - initial_investment_after_subsidy

# --- Create PDF Table ---
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Table header
header = ['Metric', 'Value']
pdf.cell(95, 10, header[0], 1)
pdf.cell(95, 10, header[1], 1)
pdf.ln()  # Move to the next line

# Table data
data = [
    ['Net Present Value (NPV)', f'${npv_value:,.2f}'],
    ['Internal Rate of Return (IRR)', f'{irr_value * 100:.2f}%'],
    ['Levelized Cost of Energy (LCOE)', f'${lcoe_value:.3f} / kWh'],
    ['Years Required to Break Even', f'{break_even_years:.2f} years'],
    ['Total Profit After Break Even', f'${total_profit_after_break_even:,.2f}'],
    ['Subsidy Amount', f'${subsidy_amount:,.2f}'],
    ['Tax Relief Amount', f'${tax_relief_amount:,.2f}']
]

# Add data rows to the table
for row in data:
    pdf.cell(95, 10, row[0], 1)
    pdf.cell(95, 10, row[1], 1)
    pdf.ln()

# Output the PDF to a file
pdf.output("microgrid_financial_analysis.pdf")

print("Financial analysis completed and results saved to microgrid_financial_analysis.pdf")
