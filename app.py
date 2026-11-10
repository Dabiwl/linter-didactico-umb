import streamlit as st
import io
import csv
from linter_core import analizar_codigo

st.set_page_config(
    page_title="Linter Didactico UMB",
    layout="wide"
)

# Codigo de prueba representativo de un proyecto universitario
CODIGO_EJEMPLO = '''# Sistema de Gestion Academica y Evaluacion de Estudiantes
# Proyecto de Laboratorio de Programacion en Python

def procesarRegistroEstudiante(codigoId, nombreCompleto, carreraDestino):
    # Mala practica: Variables con nomenclatura camelCase
    primerSemestre = True
    estadoActivo = "Matriculado"
    
    # Mala practica: Variable asignada que nunca se consume en la logica
    fechaRegistroSistema = "2026-11-09"
    codigoSedeFacultad = 104
    
    return {
        "id": codigoId,
        "estudiante": nombreCompleto,
        "programa": carreraDestino,
        "activo": primerSemestre
    }

def generarReporteAcademicoConsolidado(listadoNotas, porcentajeAsistencia):
    # Mala practica: Violacion del principio de modularidad (> 15 lineas continuas)
    notaPrimerCorte = 3.5
    notaSegundoCorte = 4.0
    notaExamenFinal = 2.8
    
    ponderacionUno = 0.30
    ponderacionDos = 0.30
    ponderacionTres = 0.40
    
    calificacionPonderadaUno = notaPrimerCorte * ponderacionUno
    calificacionPonderadaDos = notaSegundoCorte * ponderacionDos
    calificacionPonderadaTres = notaExamenFinal * ponderacionTres
    
    notaDefinitivaTotal = calificacionPonderadaUno + calificacionPonderadaDos + calificacionPonderadaTres
    
    # Mala practica adicional: Variable sin utilizar
    promedioHistoricoCohorte = 3.8
    
    estadoAprobacion = False
    if notaDefinitivaTotal >= 3.0 and porcentajeAsistencia >= 80:
        estadoAprobacion = True
    else:
        estadoAprobacion = False
        
    mensajeFinal = f"Resultado final: {notaDefinitivaTotal} - Aprobado: {estadoAprobacion}"
    return mensajeFinal

def auditoriaRendimientoSedes(sedesUniversitarias):
    # Mala practica: Anidamiento excesivo que satura la carga cognitiva (> 2 niveles)
    for sede in sedesUniversitarias:
        if len(sede) > 0:
            for grupoCurso in sede:
                if grupoCurso.get("activo"):
                    print(f"Grupo evaluado: {grupoCurso.get('nombre')}")

def calcular_promedio_limpio(valores):
    # Funcion disenada con buenas practicas como punto de comparacion
    if not valores:
        return 0.0
    return sum(valores) / len(valores)
'''

# Control de estado de sesion para el aviso flotante y el editor
if "aviso_mostrado" not in st.session_state:
    st.session_state.aviso_mostrado = False

if "texto_editor" not in st.session_state:
    st.session_state.texto_editor = ""

# Cuadro de dialogo flotante al inicio
@st.dialog("Prototipo de Linter Didactico - UMB")
def mostrar_aviso_bienvenida():
    st.markdown(
        "Esta herramienta de analisis estatico asiste a estudiantes de programacion "
        "en la identificacion y correccion de malas practicas en proyectos de Python, "
        "con base en el Abstract Syntax Tree (AST) y normas de calidad de software (ISO 25010)."
    )
    st.markdown("**Instrucciones:**")
    st.markdown(
        "1. Puede cargar un archivo Python (.py) de su preferencia en el panel lateral izquierdo "
        "o escribir directamente en el editor central.\n"
        "2. Si no dispone de un archivo propio, en el panel lateral izquierdo puede "
        "importar o descargar un proyecto de ejemplo completo con malas practicas documentadas.\n"
        "3. Haga clic en 'Ejecutar Analisis' para obtener la evaluacion cuantitativa y la retroalimentacion formativa."
    )
    if st.button("Entendido / Comenzar evaluacion", type="primary", use_container_width=True):
        st.session_state.aviso_mostrado = True
        st.rerun()

if not st.session_state.aviso_mostrado:
    mostrar_aviso_bienvenida()

# --- BARRA LATERAL IZQUIERDA ---
with st.sidebar:
    st.header("Codigo de Ejemplo")
    st.caption("Utilice este proyecto de prueba si no dispone de un archivo propio para analizar:")
    
    # Opcion 1: Importar directamente al editor de texto
    if st.button("Importar codigo al editor", use_container_width=True):
        st.session_state.texto_editor = CODIGO_EJEMPLO
    
    # Opcion 2: Descargar el archivo .py
    st.download_button(
        label="Descargar archivo (.py)",
        data=CODIGO_EJEMPLO,
        file_name="proyecto_prueba_academico.py",
        mime="text/x-python",
        use_container_width=True
    )
    
    st.divider()
    
    st.header("Carga de Archivo")
    archivo_subido = st.file_uploader("Seleccione un archivo (.py)", type=["py"])
    st.caption("Suba el archivo fuente para iniciar la evaluacion estatica.")


# --- AREA PRINCIPAL ---
st.title("Prototipo de Linter Didactico - UMB")
st.markdown("Herramienta de evaluacion de calidad de software y soporte pedagogico para proyectos en Python.")
st.divider()

codigo_a_analizar = ""

if archivo_subido is not None:
    codigo_a_analizar = archivo_subido.getvalue().decode("utf-8")
    st.caption(f"Archivo cargado actualmente: {archivo_subido.name}")
else:
    codigo_a_analizar = st.text_area(
        "Editor de codigo fuente:",
        value=st.session_state.texto_editor,
        height=260,
        placeholder="Ingrese su codigo Python aqui o presione 'Importar codigo al editor' en la barra lateral..."
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
