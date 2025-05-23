import gspread
from google.oauth2.service_account import Credentials
from enum import StrEnum

from app.general.utils.config import app_config


class DocName(StrEnum):
    DATA = "Data"


class Worksheets(StrEnum):
    BUDGET = "budget"
    AQUA = "aqua"
    STORAGE = "storage"


class Title:
    def __init__(self, value: str, col: int, row: int = 1):
        self.row = row
        self.col = col
        self.value = value


class Spreadsheet:
    def __init__(self, table: str = DocName.DATA):
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = Credentials.from_service_account_file(app_config.file_gcp_sheets_key, scopes=scope)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open(table)


    def update_cell(self, page, row, col, value):
        worksheet = self.spreadsheet.worksheet(page)
        worksheet.update_cell(row, col, str(value))


    def get_last_row(self, page: str, col: int = 1) -> int:
        worksheet = self.spreadsheet.worksheet(page)
        count = len(worksheet.col_values(col))
        return count


    def get_titles(self, page: str) -> list[Title]:
        worksheet = self.spreadsheet.worksheet(page)
        cols = worksheet.row_values(1)
        titles = [Title(cols[i], i+1) for i in range(len(cols))]
        return titles


table = Spreadsheet()
