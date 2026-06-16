from fastapi import FastAPI
from pydantic import BaseModel
from db import get_connection
from datetime import date

app = FastAPI()

# Add this model at the top
class Expense(BaseModel):
    title: str
    amount: float
    category: str
    expense_date: date
    description: str

@app.post("/expense")
def add_expense(expense: Expense):  # ← use Expense instead of dict
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO expenses (title, amount, category, expense_date, description)
    VALUES (%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (
        expense.title,
        expense.amount,
        expense.category,
        expense.expense_date,
        expense.description
    ))
    conn.commit()
    conn.close()
    return {"message": "success"}

# GET and DELETE stay the same

@app.get("/expenses")
def get_expenses():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses"
    )

    result = cursor.fetchall()

    conn.close()

    return result

@app.delete("/expense/{expense_id}")
def delete_expense(expense_id: int):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id=%s",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    return {"message": "deleted"}

@app.put("/expense/{expense_id}")
def update_expense(
    expense_id: int,
    expense: dict
):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
    UPDATE expenses
    SET
        title=%s,
        amount=%s,
        category=%s,
        expense_date=%s,
        description=%s
    WHERE id=%s
    """

    cursor.execute(
        query,
        (
            expense["title"],
            expense["amount"],
            expense["category"],
            expense["expense_date"],
            expense["description"],
            expense_id
        )
    )

    conn.commit()

    conn.close()

    return {
        "message": "updated"
    }