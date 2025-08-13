import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
from fpdf import FPDF

# Файл с данными
DATA_FILE = "data.csv"

# Загружаем или создаем пустую таблицу
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(
        columns=["Дата", "Магазин", "Статус оплаты", "Поставленные донеры", "Возвраты"])

# Списки значений
stores = ["Magnum", "Small", "Anvar", "Green", "Барыс", "Султан"]
statuses = ["Оплатил", "Конкатенация", "Не оплатил"]

st.title("Учёт поставок донеров")

# Форма ввода
with st.form("add_form"):
    col1, col2 = st.columns(2)
    date_val = col1.date_input("Дата", value=date.today())
    store_val = col2.selectbox("Магазин", stores)

    col3, col4 = st.columns(2)
    status_val = col3.selectbox("Статус оплаты", statuses)
    doners_val = col4.number_input("Поставленные донеры", min_value=0, step=1)

    returns_val = st.number_input("Возвраты", min_value=0, step=1)

    submitted = st.form_submit_button("Сохранить")
    if submitted:
        new_row = pd.DataFrame([[date_val, store_val, status_val, doners_val, returns_val]],
                               columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("Запись добавлена!")

st.divider()

# Фильтр по дате
st.subheader("Фильтр и отчет")
col1, col2 = st.columns(2)
from_date = col1.date_input("От", value=date.today().replace(day=1))
to_date = col2.date_input("До", value=date.today())

filtered_df = df[(pd.to_datetime(df["Дата"]) >= pd.to_datetime(from_date)) &
                 (pd.to_datetime(df["Дата"]) <= pd.to_datetime(to_date))]

st.dataframe(filtered_df)

# Генерация PDF


def generate_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Отчет по поставкам донеров", ln=True)
    pdf.cell(0, 10, f"Период: {from_date} — {to_date}", ln=True)

    pdf.ln(5)
    for i, row in dataframe.iterrows():
        pdf.cell(0, 8, f"{row['Дата']} | {row['Магазин']} | {row['Статус оплаты']} | "
                 f"{row['Поставленные донеры']} | {row['Возвраты']}", ln=True)

    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes


if st.button("Скачать PDF"):
    if filtered_df.empty:
        st.warning("Нет данных за выбранный период")
    else:
        pdf_file = generate_pdf(filtered_df)
        st.download_button(
            label="Скачать отчет в PDF",
            data=pdf_file,
            file_name=f"report_{from_date}_{to_date}.pdf",
            mime="application/pdf"
        )
