import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
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
def append_to_google_sheets(client, date, organization, data):
    sheet = client.open("Kassa").sheet1
    column_names = ["Дата введения", "Организация", "Касса", "Капиталбанк", "Арванд", "ДС", "ЭСХАТА", "Алиф", "Имон"]

    # Создаем словарь, сопоставляющий название организации с индексами столбцов
    org_columns = {
        "MobiCenter": ["Касса", "Капиталбанк"],
        "BABOLO-TAXI": ["Касса", "Имон"],
        "KREDITMARKET": ["Касса", "Арванд", "ЭСХАТА"],
        "OBBO": ["Касса", "ДС", "Алиф"]
    }

    if not sheet.row_values(1):
        sheet.append_row(column_names)

    row = [date, organization] + [""] * (len(column_names) - 2)
    org_column_indices = [column_names.index(col) for col in org_columns[organization]]
    for i, idx in enumerate(org_column_indices):
        if i < len(data):
            row[idx] = data[i]

    sheet.append_row(row)


# Создание функций для каждой организации
def mobi_center(client):
    st.write("# Выбрана организация MobiCenter")
    kassa = st.text_input("Касса")
    kapitalbank = st.text_input("Капиталбанк")
    if st.button("Ввод"):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        append_to_google_sheets(client, date, "MobiCenter", [kassa, kapitalbank])

def babolo_taxi(client):
    st.write("# Выбрана организация BABOLO-TAXI")
    kassa = st.text_input("Касса")
    imon = st.text_input("Имон")
    if st.button("Ввод"):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        append_to_google_sheets(client, date, "BABOLO-TAXI", [imon, kassa])

def kreditmarket(client):
    st.write("# Выбрана организация KREDITMARKET")
    kassa = st.text_input("Касса")
    arvand = st.text_input("Арванд")
    eskhata = st.text_input("ЭСХАТА")
    if st.button("Ввод"):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        append_to_google_sheets(client, date, "KREDITMARKET", [kassa, arvand, eskhata])

def obbo(client):
    st.write("# Выбрана организация OBBO")
    kassa = st.text_input("Касса")
    ds = st.text_input("ДС")
    alif = st.text_input("Алиф")
    if st.button("Ввод"):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        append_to_google_sheets(client, date, "OBBO", [kassa, ds, alif])

# Авторизация в Google Sheets
client = authorize_google_sheets()


def load_data():
    client = authorize_google_sheets()
    sheet = client.open("Kassa").sheet1
    data = pd.DataFrame(sheet.get_all_records())
    data['Дата введения'] = pd.to_datetime(data['Дата введения'])
    return data

# Функция для создания дашборда
# Функция для создания графика по выбранной организации
def create_chart(data, organization, chart_type):
    filtered_data = data[data['Организация'] == organization]
    if chart_type == 'Недельный':
        chart_data = filtered_data.resample('W-Mon', on='Дата введения').sum().reset_index()
        chart_title = f'Недельные значения для {organization}'
    else:
        chart_data = filtered_data.resample('M', on='Дата введения').sum().reset_index()
        chart_title = f'Месячные значения для {organization}'

    fig = px.line(chart_data, x='Дата введения', y='Касса', title=chart_title, labels={'Касса': 'Сумма'})
    return fig

# Функция для создания дашборда
def main():
    # Загрузка данных
    data = load_data()

    # Отображение дневных значений
    st.write("## Дневные значения")

    # Выбор даты
    min_date = data['Дата введения'].min().date()
    max_date = data['Дата введения'].max().date()
    selected_date = st.date_input("Выберите дату", min_value=min_date, max_value=max_date, value=min_date)

    # Выбор организации
    organizations = data['Организация'].unique()
    selected_org = st.selectbox("Выберите организацию", organizations)

    # Фильтрация данных по выбранной дате и организации
    filtered_data = data[(data['Дата введения'].dt.date == selected_date)]

    filtered_data = filtered_data.dropna(axis=1)
    # Отображение отфильтрованных данных
    st.write(filtered_data)

    # Преобразование даты в формат datetime
    data['Дата введения'] = pd.to_datetime(data['Дата введения'])

    # Выбор типа графика
    chart_type = st.radio("Выберите тип графика", ["Недельный", "Месячный"])

    # Отображение графика только для выбранной организации
    st.write("## График")
    fig = create_chart(data, selected_org, chart_type)
    st.plotly_chart(fig)

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

