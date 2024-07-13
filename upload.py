from loan import Loan
from property import Property
import pandas as pd
from datetime import date

def load_properties_and_loans(file_path):
    properties_df = pd.read_excel(file_path, sheet_name='Properties')
    loans_df = pd.read_excel(file_path, sheet_name='Loans')

    loans = {}
    for _, row in loans_df.iterrows():
        loan = Loan(
            loan_id=row['Loan ID'],
            origination_date=row['Origination Date'].date(),
            maturity_date=row['Maturity Date'].date(),
            original_balance=row['Original Balance'],
            note_rate=row['Note Rate'],
            interest_only_period=row.get('Interest Only Period'),
            amortization_period=row.get('Amortization Period'),
            day_count_method=row.get('Day Count Method', '30/360')
        )
        loans[loan.loan_id] = loan

    properties = []
    for _, row in properties_df.iterrows():
        loan = loans.get(row['Loan ID'])
        property_obj = Property(
            property_id=row['Property ID'],
            name=row['Name'],
            address=row['Address'],
            property_type=row['Property Type'],
            square_footage=row['Square Footage'],
            year_built=row['Year Built'],
            purchase_price=row['Purchase Price'],
            purchase_date=row['Purchase Date'].date(),
            analysis_start_date=row['Analysis Start Date'].date(),
            analysis_end_date=row['Analysis End Date'].date(),
            current_value=row.get('Current Value'),
            sale_date=row['Sale Date'].date() if pd.notna(row['Sale Date']) else None,
            sale_price=row.get('Sale Price'),
            loan=loan,
            ownership_share=row.get('Ownership Share', 1),
            buyout_date=row['Buyout Date'].date() if pd.notna(row['Buyout Date']) else date(2100, 12, 1),
            buyout_amount=row.get('Buyout Amount', 0)
        )
        properties.append(property_obj)

    return properties, loans

def load_cashflows(file_path):
    df = pd.read_excel(file_path, sheet_name='Cashflows')
    # Convert the Date column to datetime.date
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df = df[['Property ID','Date','Net Operating Income','Capital Expenditures']]
    return df

# Example usage:
# properties, loans = load_properties_and_loans("/path/to/properties_loans.xlsx")
# noi_df, capex_df = load_cashflows("/path/to/properties_loans_cashflows.xlsx")

# Now you have the noi_df and capex_df DataFrames which you can use directly
