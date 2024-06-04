import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def resaltar_celda(valor):
    if '-' in str(valor):
        return "color: black"
    else:
        return "color: yellow"

st.set_page_config(page_title = 'Mi contabilidad', page_icon = '💸', layout = "centered", initial_sidebar_state = "collapsed")
st.logo('Logotext.gif', icon_image = 'Logotext.gif')
with st.sidebar:
    st.header("Hola Junior 👋")
    contraseña = st.text_input(
        "Credenciales",
        value = "",
        type = "password",
        label_visibility = "collapsed",
        placeholder = "Contraseña",
    )
    url = 'https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/149268728&color=%23ff5500&auto_play=true&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true'
    st.markdown(f'<iframe height="100" width="100%" scrolling="no" frameborder="no" allow="autoplay" src={url}></iframe>', unsafe_allow_html = True)

page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #000000, #ff0080);
    color: #ffcc00;
    font-family: 'Courier New', Courier, monospace;
    text-shadow: 0 0 5px #ffcc00, 0 0 10px #ffcc00, 0 0 15px #ffcc00;
}
[data-testid="stHeader"] {
    background: rgba(0, 0, 0, 0.0);
}
[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0.25);
    color: #ffcc00;
    text-shadow: 0 0 5px #ffcc00, 0 0 10px #ffcc00, 0 0 15px #ffcc00;
}
[data-testid="stSidebarNav"] {
    color: #ffcc00;
    text-shadow: 0 0 5px #ffcc00, 0 0 10px #ffcc00, 0 0 15px #ffcc00;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html = True)
hide_streamlit_style = """
            <style>

            footer {visibility: hidden;}
            footer:after {
            	content:'Desarrollado por Junior Aguilar'; 
            	visibility: visible;
            	display: block;
            	position: relative;
            	#background-color: red;
            	padding: 5px;
            	top: 2px;
            }            
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html = True)
st.markdown("<h1 style='text-align: center; color: white;'>💰 Registro Financiero</h1>", unsafe_allow_html = True)
password = st.secrets["password"]

if 'client' not in st.session_state:
    try:
        scope     = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']
        file_name = 'gsheetkeys.json'
        creds     = ServiceAccountCredentials.from_json_keyfile_name(file_name, scope)
        client    = gspread.authorize(creds)
        st.session_state.client  = client
        st.toast('Conexión exitosa')
        st.balloons()
    except:
        st.toast('Conexión fallida')
        st.snow()
        
if 'client' in st.session_state:
    ggsheet = st.session_state.client.open('Registro de entradas y salidas').worksheet('Hoja 1')
    content = ggsheet.get_all_records()
    content = pd.DataFrame(content)
    content['DIA'] = pd.to_datetime(content['DIA'])
    with st.form('form1', border = False):
        data_editor1 = st.data_editor(content, hide_index = True, num_rows = "dynamic", use_container_width = True)
        form_submit_button1 = st.form_submit_button('Actualizar registro contable', use_container_width = True)
        if form_submit_button1:
            if contraseña == password:
                content = data_editor1
                content['DIA'] = content['DIA'].apply(lambda x: str(x))
                content = [content.columns.values.tolist()] + content.values.tolist()
                ggsheet.update(content)
                st.toast('Registro actualizado !')
                st.rerun()
            else:
                st.toast('Registro no actualizado !')

meses = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]
data1 = []
data2 = []
data6 = []
cntdr = -1
for i in data_editor1['DIA']:
    mes = str(i).split('-')[1]
    año = str(i).split('-')[0]
    ing = 0
    egr = 0
    cntdr = cntdr + 1
    if mes + año not in data2:
        data6.append(cntdr)
        for j in data_editor1['DIA']:
            if str(j).split('-')[1] == mes and str(j).split('-')[0] == año:
                ing = ing + data_editor1[data_editor1['DIA'] == j]['INGRESOS'].iat[0]
                egr = egr + data_editor1[data_editor1['DIA'] == j]['EGRESOS'].iat[0]
        data2.append(mes + año)
        if mes[0] == '0':
            mes = mes[1:]
        data1.append([meses[int(mes) - 1] + ' - ' + año, ing, egr, ing - egr])
data1 = pd.DataFrame(data1, columns = ['FECHAS', 'INGRESOS', 'EGRESOS', 'TOTALES'])
data3 = pd.DataFrame([['TOTAL', data1['INGRESOS'].sum(), data1['EGRESOS'].sum(), data1['TOTALES'].sum()]], columns = ['FECHAS', 'INGRESOS', 'EGRESOS', 'TOTALES'])
data1 = pd.concat([data1, data3], axis = 0, ignore_index = True)
st.dataframe(data1.style.applymap(resaltar_celda, subset = ["TOTALES"]), use_container_width = True, hide_index = True)

fig, axe = plt.subplots()
fig.patch.set_alpha(0)
axe.patch.set_alpha(0)
data4 = np.arange(data_editor1.shape[0])
data5 = (data_editor1['INGRESOS'] - data_editor1['EGRESOS']).cumsum()
axe.plot(data4, data5, color = "yellow", linestyle = 'dashed', linewidth = 1, alpha = 1.0)
axe.plot(data4, data5, color = "yellow", linestyle = 'solid', linewidth = 3, alpha = 0.4)
axe.plot(data4, data5, color = "yellow", linestyle = 'solid', linewidth = 6, alpha = 0.2)
axe.plot([0, data_editor1.shape[0] - 1], [data5.iat[0], data5.iat[0]], color = "white", linestyle = 'solid', linewidth = 1, alpha = 1.0)
axe.plot([0, data_editor1.shape[0] - 1], [data5.iat[0], data5.iat[0]], color = "white", linestyle = 'solid', linewidth = 3, alpha = 0.4)
axe.plot([0, data_editor1.shape[0] - 1], [data5.iat[0], data5.iat[0]], color = "white", linestyle = 'solid', linewidth = 6, alpha = 0.2)
axe.scatter(data4, data5, s = 5, color = "yellow", alpha = 1)
for i in range(len(data6)):
    axe.text(data6[i], -5 * data5.min(), f"${data1['FECHAS'].iat[i]}$", horizontalalignment = 'center', rotation = 90)
    axe.plot([data6[i], data6[i]], [data5.min(), data5.max()], color = "black", linestyle = 'dotted', linewidth = 1, alpha = 1.0)
axe.set_frame_on(False)
if contraseña == password:
    axe.tick_params(axis = 'y', colors = 'white')
else:
    axe.set_yticks([])
axe.set_xticks([])
st.pyplot(fig)

if data5.iat[-1] > data5.iat[0]:
    msg = 'Tu capital se ha incrementado en ' + str(round(data5.iat[-1] / data5.iat[0], 1)) + ' veces, en ' + str(len(data6)) + ' meses'
elif data5.iat[-1] == data5.iat[0]:
    msg = 'Tu capital se ha mantenido constante en ' + str(len(data6)) + ' meses'
else:
    msg = 'Tu capital se ha disminuido en ' + str(round(data5.iat[-1] / data5.iat[0], 1)) + ' veces, en ' + str(len(data6)) + ' meses'
color = 'white'
if contraseña == password:
    st.markdown(f'<marquee style="font-size: 50px; width: 100%; color: {color}" scrollamount="20"><b>{msg}</b></marquee>', unsafe_allow_html = True)
    st.toast('Tu capital actual es de ' + str(round(data5.iat[-1], 2)) + ' soles')
