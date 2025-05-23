from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/alice", tags=["spreadsheet"])
async def alice_webhook(request: Request):
    body = await request.json()

    try:
        intent = body["request"]["nlu"]["intents"]
        slots = intent.get("add_expense", {}).get("slots", {})

        amount = slots.get("amount", {}).get("value")
        category = slots.get("category", {}).get("value")

        if amount and category:
            text = f"Добавил расход {amount} рублей на {category}"
        else:
            text = "Не удалось распознать сумму или категорию. Повтори, пожалуйста."

    except Exception:
        text = "Произошла ошибка при обработке запроса."

    return JSONResponse(content={
        "response": {
            "text": text,
            "end_session": True
        },
        "version": "1.0"
    })