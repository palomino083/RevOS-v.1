import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime, timedelta
import io
import plotly.graph_objects as go

# === FUNCIÓN PRINCIPAL ===
def procesar_pdf_orden_servicio(archivo_pdf):
    texto_pdf = ""
    with pdfplumber.open(archivo_pdf) as pdf:
        for pagina in pdf.pages:
            contenido = pagina.extract_text()
            if contenido:
                texto_pdf += contenido + " "
    texto_pdf = re.sub(r"\s+", " ", texto_pdf)

    os_match = re.search(r"ORDEN\s+DE\s+SERVICIO\s*N[°º]?\s*(\d+)", texto_pdf, flags=re.IGNORECASE)
    numero_os = os_match.group(1) if os_match else "No identificado"

    fecha_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto_pdf)
    fecha_os = datetime.strptime(fecha_match.group(1), "%d/%m/%Y") if fecha_match else datetime.today()

    monto_match = re.search(r"S/\s*([\d,]+\.\d{2})", texto_pdf)
    monto_total = float(monto_match.group(1).replace(",", "")) if monto_match else 0.0

    df = pd.DataFrame({
        "N° OS": [numero_os],
        "Monto Total (S/)": [monto_total],
        "Fecha de Notificación": [fecha_os.strftime("%d/%m/%Y")]
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Cronograma")
    buffer.seek(0)

    return df, buffer, numero_os

# === INTERFAZ ===
st.set_page_config(page_title="Procesador OS", page_icon="📘", layout="centered")
st.title("📘 Procesamiento Automático de Órdenes de Servicio")

uploaded_file = st.file_uploader("📂 Cargar archivo PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Procesando archivo..."):
        df, excel_buffer, numero_os = procesar_pdf_orden_servicio(uploaded_file)

    st.success("✅ Procesamiento completado")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        label="⬇️ Descargar Excel",
        data=excel_buffer,
        file_name=f"Cronograma_OS{numero_os}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
