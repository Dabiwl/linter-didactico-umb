import streamlit as st
import io
import csv
from linter_core import analizar_codigo

st.set_page_config(
    page_title="Linter Didactico UMB",
    layout="wide"
)

st.title("Prototipo de Linter Didactico - UMB")
st.markdown("Herramienta de evaluacion de calidad de software y soporte pedagogico para proyectos en Python.")
st.divider()

with st.sidebar:
    st.header("Carga de Archivo")
    archivo_subido = st.file_uploader("Seleccione un archivo (.py)", type=["py"])
    st.caption("Suba el archivo fuente para iniciar la evaluacion estatica.")

codigo_a_analizar = ""

if archivo_subido is not None:
    codigo_a_analizar = archivo_subido.getvalue().decode("utf-8")
else:
    codigo_a_analizar = st.text_area(
        "O ingrese el codigo fuente directamente en este panel:",
        height=220,
        placeholder="def calcular_area():\n    pass"
    )

if st.button("Ejecutar Analisis", type="primary"):
    if not codigo_a_analizar.strip():
        st.warning("Debe ingresar codigo o cargar un archivo para realizar el analisis.")
    else:
        errores, puntaje = analizar_codigo(codigo_a_analizar, es_texto=True)
        
        # Panel de metricas numericas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Puntaje de Calidad", f"{puntaje} / 100")
        with col2:
            st.metric("Observaciones Totales", len(errores))
        with col3:
            estado = "Optimo" if puntaje >= 90 else "Aceptable" if puntaje >= 60 else "Deficiente"
            st.metric("Diagnostico", estado)
            
        st.divider()
        
        # Generacion de datos para exportacion CSV
        buffer_csv = io.StringIO()
        writer_csv = csv.writer(buffer_csv)
        writer_csv.writerow(["Linea", "Tipo_Observacion", "Penalizacion", "Hallazgo", "Fundamento_Teorico", "Sugerencia"])
        
        for e in errores:
            writer_csv.writerow([
                e["linea"],
                e["tipo"],
                e.get("penalizacion", 0),
                e["hallazgo"],
                e["porque"],
                e["sugerencia"]
            ])
            
        csv_data = buffer_csv.getvalue().encode("utf-8")
        
        # Boton de descarga para investigacion
        st.download_button(
            label="Descargar Reporte de Metricas (CSV)",
            data=csv_data,
            file_name="reporte_calidad_linter_umb.csv",
            mime="text/csv"
        )
        
        st.subheader("Resultados y Retroalimentacion Didactica")
        
        if not errores:
            st.success("Analisis completado: El codigo cumple con los estandares de modularidad y estilo evaluados.")
        else:
            for i, e in enumerate(errores, 1):
                with st.expander(f"[Linea {e['linea']}] {e['tipo']} - {e['hallazgo']}", expanded=True):
                    st.markdown(f"**Hallazgo:** {e['hallazgo']}")
                    st.markdown(f"**Fundamento:** {e['porque']}")
                    st.info(f"**Accion correctiva:** {e['sugerencia']}")