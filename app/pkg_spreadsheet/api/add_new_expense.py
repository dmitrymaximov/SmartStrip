from fastapi import APIRouter

from app.pkg_spreadsheet.models.Spreadsheet import table, Worksheets
from app.pkg_spreadsheet.models.Budget import BudgetRecord, BudgetTitles
from app.general.utils.logger import logger

router = APIRouter()


@router.post("/add_new_expense", tags=["spreadsheet"])
async def add_new_expense(record: BudgetRecord):
    try:
        page = Worksheets.BUDGET
        titles = table.get_titles(Worksheets.BUDGET)

        logger.debug(titles)

        row = table.get_last_row(page=page) + 1

        for title in titles:
            if title.value == BudgetTitles.DATE:
                table.update_cell(page=page, row=row, col=title.col, value=record.date)

            if title.value == BudgetTitles.TYPE:
                table.update_cell(page=page, row=row, col=title.col, value=record.type)

            if title.value == BudgetTitles.COUNT:
                table.update_cell(page=page, row=row, col=title.col, value=record.count)


        #table.update_cell(data.page, data.row, data.col, data.value)
        return {"status": "success", "written": record}
    except Exception as e:
        return {"status": "error", "details": str(e)}
