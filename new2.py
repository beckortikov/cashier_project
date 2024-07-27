import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timezone
import pandas as pd
import plotly.express as px
import pickle
from pathlib import Path
import streamlit_authenticator as stauth

names = ["MobiCenter", "BABOLO-TAXI", "KREDITMARKET", "OBBO", "Dashboard"]
usernames = ["mobicenter", "babolo", "kreditmarket", "obbo", "admin"]

# load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "sales_dashboard", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")


# Функция для авторизации в Google Sheets
def authorize_google_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credits_mobi.json', scope)
    client = gspread.authorize(creds)
    return client
# Функция для записи данных в Google Sheets
def append_to_google_sheets(client, input_date, date, organization, data):
    sheet = client.open("Kassa").sheet1
    column_names = ["Дата ввода", "Дата введения", "Организация", "Касса", "Капиталбанк", "Арванд", "ДС", "ЭСХАТА", "Алиф", "Имон", "ДС_КОШ"]

    # Создаем словарь, сопоставляющий название организации с индексами столбцов
    org_columns = {
        "MobiCenter": ["Касса", "Капиталбанк"],
        "BABOLO-TAXI": ["Касса", "Имон"],
        "KREDITMARKET": ["Касса", "Арванд", "ЭСХАТА"],
        "OBBO": ["Касса", "ДС", "Алиф", "Арванд", "Имон", "ДС_КОШ"]
    }

    if not sheet.row_values(1):
        sheet.append_row(column_names)

    row = [input_date, date, organization] + [""] * (len(column_names) - 3)
    org_column_indices = [column_names.index(col) for col in org_columns[organization]]
    for i, idx in enumerate(org_column_indices):
        if i < len(data):
            row[idx] = data[i]

    sheet.append_row(row)


# Создание функций для каждой организации
def mobi_center(client):
    st.write("# Выбрана организация MobiCenter")
    data = load_data()

    lst_date = data[data["Организация"] == "MobiCenter"]["Дата ввода"].max()
    st.write(f"#### Последняя дата ввода: {lst_date.strftime('%d-%m-%Y')}")
    input_date = st.date_input("Выберите дату", value=datetime.today().date())
    input1 = st.empty()
    input2 = st.empty()
    kassa = input1.number_input("Касса", key="kassa")
    kapitalbank = input2.number_input("Капиталбанк", key="kapitalbank")
    if st.button("Ввод"):
        if kassa == "" or kapitalbank == "":
            st.error("Пожалуйста, заполните все поля")
        else:
            now = datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M:%S")
            input_date = input_date.strftime("%Y-%m-%d")
            st.success("Успешно заполнено")
            append_to_google_sheets(client, input_date, date, "MobiCenter", [kassa, kapitalbank])
            input1.number_input("Касса", key="kassa1")
            input2.number_input("Капиталбанк", key="kapitalbank1")


def babolo_taxi(client):
    st.write("# Выбрана организация BABOLO-TAXI")
    data = load_data()

    lst_date = data[data["Организация"] == "BABOLO-TAXI"]["Дата ввода"].max()
    st.write(f"#### Последняя дата ввода: {lst_date.strftime('%d-%m-%Y')}")
    input_date = st.date_input("Выберите дату", value=datetime.today().date())
    input1 = st.empty()
    input2 = st.empty()
    kassa = input1.number_input("Касса", key="kassa")
    imon = input2.number_input("Имон", key="imon")
    if st.button("Ввод"):
        if kassa == "" or imon == "":
            st.error("Пожалуйста, заполните все поля")
        else:
            now = datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M:%S")
            input_date = input_date.strftime("%Y-%m-%d")
            st.success("Успешно заполнено")
            append_to_google_sheets(client, input_date, date, "BABOLO-TAXI", [kassa, imon])
            input1.number_input("Касса", key="kassa1")
            input2.number_input("Имон", key="imon1")

def kreditmarket(client):
    st.write("# Выбрана организация KREDITMARKET")
    data = load_data()

    lst_date = data[data["Организация"] == "KREDITMARKET"]["Дата ввода"].max()
    st.write(f"#### Последняя дата ввода: {lst_date.strftime('%d-%m-%Y')}")
    input_date = st.date_input("Выберите дату", value=datetime.today().date())
    input1 = st.empty()
    input2 = st.empty()
    input3 = st.empty()
    kassa = input1.number_input("Касса", key="kassa")
    arvand = input2.number_input("Арванд", key="arvand")
    eskhata = input3.number_input("ЭСХАТА", key="eskhata")
    if st.button("Ввод"):
        if kassa == "" or arvand == "" or eskhata =="" :
            st.error("Пожалуйста, заполните все поля")
        else:
            now = datetime.now().astimezone()
            date = now.strftime("%Y-%m-%d %H:%M:%S")
            input_date = input_date.strftime("%Y-%m-%d")
            st.success("Успешно заполнено")
            append_to_google_sheets(client, input_date, date, "KREDITMARKET", [kassa, arvand, eskhata])
            input1.number_input("Касса", key="kassa1")
            input2.number_input("Арванд", key="arvand1")
            input3.number_input("ЭСХАТА", key="eskhata1")

def obbo(client):
    st.write("# Выбрана организация OBBO")
    data = load_data()

    lst_date = data[data["Организация"] == "OBBO"]["Дата ввода"].max()
    st.write(f"#### Последняя дата ввода: {lst_date.strftime('%d-%m-%Y')}")
    input_date = st.date_input("Выберите дату", value=datetime.today().date())
    input1 = st.empty()
    input2 = st.empty()
    input3 = st.empty()
    input4 = st.empty()
    input5 = st.empty()
    input6 = st.empty()
    kassa = input1.number_input("Касса", key="kassa")
    ds = input2.number_input("ДС", key="ds")
    alif = input3.number_input("Алиф", key="alif")
    arvand = input4.number_input("Арванд", key="arvand")
    imon = input5.number_input("Имон", key="imon")
    dc_cash = input6.number_input("ДС_КОШ", key="dc_cash")
    if st.button("Ввод"):
        if kassa == "" or ds == "" or alif == "" :
            st.error("Пожалуйста, заполните все поля")
        else:
            now = datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M:%S")
            input_date = input_date.strftime("%Y-%m-%d")
            st.success("Успешно заполнено")
            append_to_google_sheets(client, input_date, date, "OBBO", [kassa, ds, alif, arvand, imon, dc_cash])
            input1.number_input("Касса", key="kassa1")
            input2.number_input("ДС", key="ds1")
            input3.number_input("Алиф", key="alif1")
            input4.number_input("Арванд", key="arvand1")
            input5.number_input("Имон", key="imon1")
            input6.number_input("ДС_КОШ", key="dc_cash1")

# Авторизация в Google Sheets
client = authorize_google_sheets()


def load_data():
    client = authorize_google_sheets()
    sheet = client.open("Kassa").sheet1
    data = pd.DataFrame(sheet.get_all_records())
    data['Дата ввода'] = pd.to_datetime(data['Дата ввода'])
    data.iloc[:, 3:] = data.iloc[:, 3:].replace(regex={',': '.', "": 0})
    return data

# Функция для создания дашборда
# Функция для создания графика по выбранной организации
def create_chart(data, organization, chart_type):
    filtered_data = data[data['Организация'] == organization]
    if chart_type == 'Недельный':
        chart_data = filtered_data.resample('W-Mon', on='Дата ввода').sum().reset_index()
        chart_title = f'Недельные значения для {organization}'
    else:
        chart_data = filtered_data.resample('M', on='Дата ввода').sum().reset_index()
        chart_title = f'Месячные значения для {organization}'

    fig = px.line(chart_data, x='Дата ввода', y='Касса', title=chart_title, labels={'Касса': 'Сумма'})
    return fig

# Функция для создания дашборда
def main():
    # Загрузка данных
    data = load_data()
    # Выбор даты
    min_date = data['Дата ввода'].min().date()
    max_date = data['Дата ввода'].max().date()
    selected_date = st.sidebar.date_input("Выберите дату", min_value=min_date, max_value=max_date, value=min_date)

    # Выбор организации
    # organizations = data['Организация'].unique()
    # selected_org = st.selectbox("Выберите организацию", organizations)

    # Фильтрация данных по выбранной дате и организации
    filtered_data = data[(data['Дата ввода'].dt.date == selected_date)]

    filtered_data = filtered_data.dropna(axis=1)
    # Отображение отфильтрованных данных
    total_metrics = {}
    for org in filtered_data['Организация'].unique():
        org_data = filtered_data[filtered_data['Организация'] == org]
        total_metrics[org] = {
            "Касса": org_data['Касса'].sum(),
            "Капиталбанк": org_data['Капиталбанк'].sum(),
            "Арванд": org_data['Арванд'].sum(),
            "ЭСХАТА": org_data['ЭСХАТА'].sum(),
            "Имон": org_data['Имон'].sum(),
            "ДС": org_data['ДС'].sum(),
            "Алиф": org_data['Алиф'].sum(),
            "ДС_КОШ": org_data['ДС_КОШ'].sum(),
        }

    # Отображение сумм метрик для каждой организации
    st.write("### Сумма метрик на выбранную дату для каждой организации:")
    for org, metrics in total_metrics.items():
        st.write(f"#### {org}")
        row_metrics = []
        total_value = 0.0
        for metric, value in metrics.items():
            if isinstance(value, str):
                try:
                    value = float(value)  # Convert value to float
                except ValueError:
                    import re
                    number_str_cleaned = re.sub(r'[^\d.]', '', value)
                    value = float(number_str_cleaned)  # Skip if value cannot be converted to float
            if isinstance(value, float):
                row_metrics.append((metric, '{:,.2f}'.format(value)))
                total_value += value
        row_metrics.append(("Итого", '{:,.2f}'.format(total_value)))
        num_metrics = len(row_metrics)
        num_cols = 3
        num_rows = (num_metrics + num_cols - 1) // num_cols
        for i in range(num_rows):
            cols = st.columns(num_cols)
            for j in range(num_cols):
                idx = i * num_cols + j
                if idx < num_metrics:
                    metric, value = row_metrics[idx]
                    with cols[j]:
                        st.metric(label=metric, value=value)

# В зависимости от выбранной организации вызываем соответствующую функцию
if authentication_status:
    # Главная часть приложения Streamlit
    st.sidebar.title("Выбор организации")
    authenticator.logout("Выход", "sidebar")
    if username == "mobicenter":
        mobi_center(client)
    elif username == "babolo":
        babolo_taxi(client)
    elif username == "kreditmarket":
        kreditmarket(client)
    elif  username == "obbo":
        obbo(client)
    elif username == "admin":
        main()
