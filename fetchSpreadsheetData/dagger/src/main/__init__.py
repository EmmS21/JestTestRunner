"""
A generated module for FetchSpreadsheetData functions.

Overview:
This module facilitates the automation of fetching transaction data from Google Spreadsheets that are populated by Tiller. Tiller is a tool that aggregates transactional data from various bank accounts into a single spreadsheet. The module provides a mechanism to programmatically retrieve this data, which can be crucial for applications involving financial analysis, budget tracking, or expense management.

Functionality:
- Securely connects to Google Sheets to retrieve transaction data.
- Parses the spreadsheet data to convert it from raw format to structured JSON.
- Handles errors gracefully to manage cases where the spreadsheet might be empty or the API call fails.


Args:
- `apiKey (Secret)`: The API key required to authenticate requests to the Google Sheets API. It should have the necessary permissions to access the spreadsheet.
- `sheet (Secret)`: The ID of the Google Spreadsheet. This ID is typically found in the URL of the spreadsheet when opened in a web browser.

Return:
- The function returns a JSON formatted string. If transaction data is present, it returns a JSON string representing an array of transactions, where each transaction is a dictionary with column headers as keys. If no data is found, it returns an empty array '[]' in JSON format.

Example Call:
dagger call fetch-data --apiKey=env:[KEY] --sheet=env:[KEY]
"""

from dagger import dag, function, object_type, Secret

@object_type
class FetchSpreadsheetData:
    @function
    async def fetch_data(self, apiKey: Secret, sheet: Secret) -> str:
        """Fetches transaction data from a Google Spreadsheet."""
        python_script = """
import requests
import json
import os

api_key = os.environ.get('API_KEY')
spreadsheet_id = os.environ.get('SPREADSHEET_ID')
url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/Transactions?key={api_key}'
response = requests.get(url)
data = response.json()

if 'values' in data:
    headers = data['values'][0]
    rows = data['values'][1:]
    transactions = [dict(zip(headers, row)) for row in rows]
    print(json.dumps(transactions))
else:
    print('[]')
"""
        container = (
            dag.container()
            .from_("python:3.9-slim")
            .with_exec(["pip", "install", "requests"])
            .with_secret_variable("API_KEY", apiKey)
            .with_secret_variable("SPREADSHEET_ID", sheet)
            .with_exec(["python", "-c", python_script])
        )
        output = await container.stdout()
        return output