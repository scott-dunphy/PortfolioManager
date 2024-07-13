def load_cashflows(file_path):
    df = pd.read_excel(file_path, sheet_name='Cashflows')
    noi = {}
    capex = {}

    for _, row in df.iterrows():
        property_id = row['Property ID']
        cashflow_date = row['Date'].date().isoformat()  # Convert date to ISO format string
        amount = row['Amount']
        if row['Type'].lower() == 'noi':
            if property_id not in noi:
                noi[property_id] = {}
            noi[property_id][cashflow_date] = amount
        elif row['Type'].lower() == 'capex':
            if property_id not in capex:
                capex[property_id] = {}
            capex[property_id][cashflow_date] = amount

    return noi, capex
