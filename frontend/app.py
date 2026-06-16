"""
Expense Tracker Frontend
Features:
- Add Expense
- View Expenses
- Update Expense (checkbox select one row)
- Delete Expense (checkbox select one or more rows)
- Analytics Dashboard
"""

import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)


def get_expenses():
    try:
        response = requests.get(f"{BASE_URL}/expenses")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except Exception as ex:
        st.error(str(ex))

    return pd.DataFrame()


def add_expense(payload):
    response = requests.post(
        f"{BASE_URL}/expense",
        json=payload
    )
    return response.status_code == 200


def update_expense(expense_id, payload):
    response = requests.put(
        f"{BASE_URL}/expense/{expense_id}",
        json=payload
    )
    return response.status_code == 200


def delete_expense(expense_id):
    response = requests.delete(
        f"{BASE_URL}/expense/{expense_id}"
    )
    return response.status_code == 200


@st.dialog("Update Expense")
def update_dialog(expense):

    title = st.text_input(
        "Title",
        value=expense["title"]
    )

    amount = st.number_input(
        "Amount",
        min_value=0.0,
        value=float(expense["amount"])
    )

    categories = [
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Entertainment",
        "Others"
    ]

    category = st.selectbox(
        "Category",
        categories,
        index=categories.index(expense["category"])
        if expense["category"] in categories
        else 0
    )

    expense_date = st.date_input(
        "Expense Date",
        value=pd.to_datetime(
            expense["expense_date"]
        )
    )

    description = st.text_area(
        "Description",
        value=expense["description"]
    )

    if st.button("💾 Save Changes"):

        payload = {
            "title": title,
            "amount": amount,
            "category": category,
            "expense_date": str(expense_date),
            "description": description
        }

        success = update_expense(
            int(expense["id"]),
            payload
        )

        if success:
            st.success("Expense Updated")
            st.rerun()


st.title("💰 Expense Tracker")

tab1, tab2 = st.tabs(
    ["Expense Management", "Analytics"]
)

with tab1:

    st.subheader("Add Expense")

    c1, c2 = st.columns(2)

    with c1:

        title = st.text_input("Title")

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=10.0
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Shopping",
                "Bills",
                "Entertainment",
                "Others"
            ]
        )

    with c2:

        expense_date = st.date_input(
            "Expense Date"
        )

        description = st.text_area(
            "Description"
        )

    if st.button("Add Expense"):

        payload = {
            "title": title,
            "amount": amount,
            "category": category,
            "expense_date": str(expense_date),
            "description": description
        }

        if add_expense(payload):
            st.success("Added Successfully")
            st.rerun()

    st.divider()

    df = get_expenses()

    st.subheader("Expense Records")

    if not df.empty:

        display_df = df.copy()

        display_df.insert(
            0,
            "Select",
            False
        )

        edited_df = st.data_editor(
            display_df,
            hide_index=True,
            use_container_width=True
        )

        selected_rows = edited_df[
            edited_df["Select"] == True
        ]

        st.info(
            f"Selected Rows : {len(selected_rows)}"
        )

        col1, col2 = st.columns(2)

        with col1:

            if len(selected_rows) == 1:

                selected_expense = (
                    selected_rows.iloc[0]
                    .to_dict()
                )

                if st.button(
                    "✏ Update Selected Expense",
                    use_container_width=True
                ):
                    update_dialog(
                        selected_expense
                    )

            elif len(selected_rows) > 1:

                st.warning(
                    "Select only one row to update."
                )

        with col2:

            if st.button(
                "🗑 Delete Selected Expenses",
                use_container_width=True
            ):

                for expense_id in selected_rows["id"]:
                    delete_expense(
                        int(expense_id)
                    )

                st.success(
                    f"Deleted {len(selected_rows)} expense(s)"
                )

                st.rerun()

    else:

        st.info(
            "No Expenses Available"
        )

with tab2:

    df = get_expenses()

    if df.empty:

        st.warning(
            "No expense data available."
        )

    else:

        df["expense_date"] = pd.to_datetime(
            df["expense_date"]
        )

        min_date = (
            df["expense_date"]
            .min()
            .date()
        )

        max_date = (
            df["expense_date"]
            .max()
            .date()
        )

        c1, c2 = st.columns(2)

        with c1:
            start_date = st.date_input(
                "Start Date",
                value=min_date
            )

        with c2:
            end_date = st.date_input(
                "End Date",
                value=max_date
            )

        filtered_df = df[
            (df["expense_date"] >= pd.Timestamp(start_date))
            &
            (df["expense_date"] <= pd.Timestamp(end_date))
        ]

        st.metric(
            "Total Expense",
            f"₹ {filtered_df['amount'].sum():,.2f}"
        )

        category_df = (
            filtered_df
            .groupby("category")["amount"]
            .sum()
            .reset_index()
        )

        if not category_df.empty:

            col1, col2 = st.columns(2)

            with col1:

                fig, ax = plt.subplots()

                sns.barplot(
                    data=category_df,
                    x="category",
                    y="amount",
                    ax=ax
                )

                plt.xticks(rotation=45)

                st.pyplot(fig)

            with col2:

                fig2, ax2 = plt.subplots()

                ax2.pie(
                    category_df["amount"],
                    labels=category_df["category"],
                    autopct="%1.1f%%"
                )

                st.pyplot(fig2)

        trend_df = (
            filtered_df
            .groupby("expense_date")
            ["amount"]
            .sum()
            .reset_index()
        )

        if not trend_df.empty:

            fig3, ax3 = plt.subplots()

            sns.lineplot(
                data=trend_df,
                x="expense_date",
                y="amount",
                marker="o",
                ax=ax3
            )

            st.pyplot(fig3)

        st.subheader(
            "Filtered Expense Data"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True
        )
