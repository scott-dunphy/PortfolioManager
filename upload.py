from loan import Loan
from property import Property
import pandas as pd


def load_properties_and_loans(file_path):
    xls = pd.ExcelFile(file_path)
    properties_df = pd.read_excel(xls, 'Properties')
    loans_df = pd.read_excel(xls, 'Loans')
    
    loans = {}
    for _, row in loans_df.iterrows():
        loan = Loan(
            loan_id=row['Loan ID'],
            origination_date=row['Origination Date'],
            maturity_date=row['Maturity Date'],
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
            purchase_date=row['Purchase Date'],
            analysis_start_date=row['Analysis Start Date'],
            analysis_end_date=row['Analysis End Date'],
            current_value=row.get('Current Value'),
            sale_date=row.get('Sale Date'),
            sale_price=row.get('Sale Price'),
            loan=loan,
 
