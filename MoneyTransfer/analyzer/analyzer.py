import re
from itertools import chain

from pathlib import Path

import pandas as pd
from django.conf import settings

ACCOUNT_NAME_PATTERN = r'account #\d+'


def parse_file(file_path: Path | str) -> list:
    excel_data = pd.read_excel(Path(file_path), header=None)

    # find accounts
    account_locations = []
    for row in range(excel_data.shape[0]):
        for col in range(excel_data.shape[1]):
            cell_value = str(excel_data.iloc[row, col])
            if re.search(ACCOUNT_NAME_PATTERN, cell_value, re.IGNORECASE):
                account_locations.append((row, col))

    # find accounts data
    accounts_data = {}
    for location in account_locations:
        row, col = location
        account_id = int(re.findall(r'\d+', excel_data.iloc[row, col])[0])
        account_data = excel_data.iloc[row + 2:, col:col + 3]
        account_data = account_data.dropna(how='all')
        accounts_data[account_id] = account_data

    # prepare accounts data
    prepared_accounts_data = [
        [(account, item[0].date(), *item[1:]) for item in data.where(pd.notnull(data), 0).values.tolist()]
        for account, data in accounts_data.items()
    ]

    return list(chain.from_iterable(prepared_accounts_data))


def prepare_data(data):
    credit_transactions = []
    debit_transactions = []
    for account_id, date, credit, debit in data:
        if credit > 0:
            credit_transactions.append((account_id, date, credit))
        if debit > 0:
            debit_transactions.append((account_id, date, debit))
    return credit_transactions, debit_transactions


def analyze_transfers(credits, debits) -> list:
    result = []
    for credit_account, credit_date, credit in credits:
        for debit_account, debit_date, debit in debits:
            if credit_date == debit_date and credit == debit and credit_account != debit_account:
                result.append((credit_date, credit, credit_account, debit_account))

    return result


if __name__ == "__main__":
    data = parse_file(settings.TMP_XLSX_FILEPATH)
    data = prepare_data(data)
    print(analyze_transfers(*data))