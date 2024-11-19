import streamlit as st
from pdf_processor import PDFProcessor
from ai_handler import AIHandler
import pyperclip

def main():
    st.set_page_config(page_title="Asistente de Artículos Científicos", layout="wide")
    
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = PDFProcessor()
    if 'ai_handler' not in st.session_state:
        st.session_state.ai_handler = AIHandler()
    
    st.title("📚 Asistente de Artículos Científicos")
    
    # Agregar en la sección de documentación (dentro de la función main())
    with st.sidebar:
        st.header("📖 Documentación")
        with st.expander("Guía de Uso", expanded=True):
            st.markdown("""
            ### Cómo usar la aplicación:
            1. Sube tus PDFs en la sección 'Biblioteca'
            2. La aplicación SOLO utilizará la información contenida en los documentos que proporciones
            3. Cada información generada incluirá referencias explícitas a su documento fuente
            4. No se utilizará información externa a los documentos proporcionados
            
            ### Limitaciones:
            - Solo se procesará información contenida en los PDFs subidos
            - La calidad del resultado depende de la calidad y relevancia de los documentos proporcionados
            - Solo se aceptan archivos PDF
            - Tamaño máximo: 200MB por archivo
            - La calidad depende de los PDFs
            
            ### Mejores prácticas:
            - Usa PDFs con texto seleccionable
            - Sube documentos relevantes
            - Personaliza los prompts
            - Revisa y edita el contenido
            """)
        
        st.header("⚙️ Configuración")
        model_options = list(st.session_state.ai_handler.models.keys())
        selected_model = st.selectbox("Modelo de IA", model_options, index=0)
    
    tabs = st.tabs(["📚 Biblioteca", "📝 Generador de Artículos", "✍️ Secciones", "❓ Consultas", "📖 Bibliografía", "📄 LaTeX"])
    
    with tabs[0]:  # Biblioteca
        st.header("Biblioteca de Referencias")
        uploaded_files = st.file_uploader("Sube tus PDFs de referencia", 
                                        type="pdf", 
                                        accept_multiple_files=True)
        
        if uploaded_files:
            for file in uploaded_files:
                if file.name not in st.session_state.pdf_processor.pdf_contents:
                    with st.spinner(f'Procesando {file.name}...'):
                        content = st.session_state.pdf_processor.read_pdf(file)
                        st.session_state.pdf_processor.store_pdf_content(file.name, content)
                        st.success(f"✅ {file.name} procesado correctamente")
        
        if st.session_state.pdf_processor.pdf_contents:
            st.subheader("Documentos disponibles:")
            for filename in st.session_state.pdf_processor.pdf_contents.keys():
                st.write(f"📄 {filename}")
    
    with tabs[1]:  # Generador de Artículos Completos
        st.header("Generador de Artículos Completos")
        
        if not st.session_state.pdf_processor.pdf_contents:
            st.warning("⚠️ Primero debes subir algunos PDFs en la sección Biblioteca")
            return
        
        title = st.text_input("Título del artículo")
        custom_prompt = st.text_area("Personalizar prompt del sistema (opcional)", 
                                   help="Define instrucciones específicas para la generación del artículo")
        
        if st.button("Generar Artículo Completo"):
            if not title:
                st.error("Por favor, ingresa un título para el artículo")
                return
            
            with st.spinner("Generando artículo..."):
                try:
                    result = st.session_state.ai_handler.generate_complete_article(
                        st.session_state.pdf_processor.pdf_contents,
                        title,
                        custom_prompt,
                        selected_model
                    )
                    
                    st.markdown("### Artículo Generado")
                    st.markdown(result["content"])
                    
                    st.markdown("### Fuentes utilizadas")
                    for source in result["sources"]:
                        st.write(f"- {source}")
                    
                    st.download_button(
                        "Descargar artículo",
                        result["content"],
                        "articulo.txt",
                        "text/plain"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tabs[2]:  # Generador de Secciones
        st.header("Generador de Secciones")
        
        if not st.session_state.pdf_processor.pdf_contents:
            st.warning("⚠️ Primero debes subir algunos PDFs en la sección Biblioteca")
            return
        
        title = st.text_input("Título del artículo", key="section_title")
        section_type = st.selectbox(
            "Selecciona la sección a generar",
            ["resumen", "introduccion", "metodologia", "resultados", "discusion", "conclusiones"]
        )
        custom_prompt = st.text_area("Personalizar prompt del sistema (opcional)", 
                                   key="section_prompt",
                                   help="Define instrucciones específicas para esta sección")
        
        if st.button("Generar Sección"):
            if not title:
                st.error("Por favor, ingresa un título para el artículo")
                return
            
            with st.spinner("Generando contenido..."):
                try:
                    result = st.session_state.ai_handler.generate_article_section(
                        st.session_state.pdf_processor.pdf_contents,
                        title,
                        section_type,
                        custom_prompt,
                        selected_model
                    )
                    
                    st.markdown("### Contenido Generado")
                    st.markdown(result["content"])
                    
                    st.markdown("### Fuentes utilizadas")
                    for source in result["sources"]:
                        st.write(f"- {source}")
                    
                    st.download_button(
                        "Descargar sección",
                        result["content"],
                        f"{section_type}.txt",
                        "text/plain"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tabs[3]:  # Consultas
        st.header("Consultas a Documentos")
        
        if not st.session_state.pdf_processor.pdf_contents:
            st.warning("⚠️ Primero debes subir algunos PDFs en la sección Biblioteca")
            return
        
        question = st.text_area("Realiza una pregunta sobre los documentos")
        custom_prompt = st.text_area("Personalizar prompt del sistema (opcional)", 
                                   key="question_prompt",
                                   help="Define instrucciones específicas para la consulta")
        
        if st.button("Consultar"):
            if not question:
                st.error("Por favor, ingresa una pregunta")
                return
            
            with st.spinner("Procesando consulta..."):
                try:
                    result = st.session_state.ai_handler.answer_question(
                        st.session_state.pdf_processor.pdf_contents,
                        question,
                        custom_prompt,
                        selected_model
                    )
                    
                    st.markdown("### Respuesta")
                    st.markdown(result["answer"])
                    
                    st.markdown("### Fuentes consultadas")
                    for source in result["sources"]:
                        st.write(f"- {source}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tabs[4]:  # Bibliografía
        st.header("Generador de Bibliografía")
        
        if not st.session_state.pdf_processor.pdf_contents:
            st.warning("⚠️ Primero debes subir algunos PDFs en la sección Biblioteca")
            return
        
        citation_style = st.selectbox(
            "Estilo de citación",
            list(st.session_state.ai_handler.citation_styles.keys())
        )
        
        if st.button("Generar Bibliografía"):
            with st.spinner("Generando bibliografía..."):
                try:
                    result = st.session_state.ai_handler.generate_bibliography(
                        st.session_state.pdf_processor.pdf_contents,
                        citation_style,
                        selected_model
                    )
                    
                    st.markdown("### Referencias Bibliográficas")
                    st.markdown(result["content"])
                    
                    st.markdown("### Documentos procesados")
                    for source in result["sources"]:
                        st.write(f"- {source}")
                    
                    st.download_button(
                        "Descargar bibliografía",
                        result["content"],
                        "bibliografia.txt",
                        "text/plain"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tabs[5]:  # LaTeX
        st.header("Conversor a LaTeX")
        
        if not st.session_state.pdf_processor.pdf_contents:
            st.warning("⚠️ Primero debes subir algunos PDFs en la sección Biblioteca")
            return
        
        # Información básica del artículo
        st.subheader("Información General")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Título completo del artículo", key="latex_title")
            running_title = st.text_input("Título corto (para cabecera)", key="running_title")
            authors = st.text_input("Autores (separados por comas)")
            keywords = st.text_input("Palabras clave (separadas por comas)")
        
        with col2:
            abstract = st.text_area("Resumen (Abstract)", height=150)
            acknowledgements = st.text_area("Agradecimientos", height=100)
        
        # Contenido principal del artículo
        st.subheader("Contenido del Artículo")
        introduction = st.text_area("Introducción", height=200)
        objectives = st.text_area("Objetivos", height=150)
        methods = st.text_area("Metodología", height=200)
        results = st.text_area("Resultados", height=200)
        discussion = st.text_area("Discusión", height=200)
        conclusions = st.text_area("Conclusiones", height=150)
        
        # Tablas y figuras
        st.subheader("Tablas y Figuras")
        has_tables = st.checkbox("¿Incluir tablas?")
        if has_tables:
            table_data = st.text_area("Datos de las tablas (formato CSV)", height=100,
                help="Ingresa los datos de las tablas en formato CSV")
            table_caption = st.text_input("Título de la tabla")
            table_notes = st.text_input("Notas de la tabla")
        
        has_figures = st.checkbox("¿Incluir figuras?")
        if has_figures:
            figure_path = st.text_input("Ruta de la figura", 
                help="Ingresa la ruta relativa de la figura")
            figure_caption = st.text_input("Título de la figura")
            figure_notes = st.text_input("Notas de la figura")
        
        # Referencias
        st.subheader("Referencias Bibliográficas")
        references_style = st.selectbox(
            "Estilo de referencias",
            ["BibTeX", "APA", "IEEE", "Vancouver"]
        )
        references = st.text_area("Referencias bibliográficas", height=150)
        
        # Botón para generar LaTeX
        if st.button("Generar Código LaTeX"):
            if not all([title, authors, abstract]):
                st.error("Por favor, completa al menos el título, autores y resumen")
                return
            
            with st.spinner("Generando código LaTeX..."):
                try:
                    # Preparar el contenido completo del artículo
                    article_content = f"""
                    Abstract:
                    {abstract}

                    Introduction:
                    {introduction}

                    Objectives:
                    {objectives}

                    Methods:
                    {methods}

                    Results:
                    {results}

                    Discussion:
                    {discussion}

                    Conclusions:
                    {conclusions}

                    Acknowledgements:
                    {acknowledgements}

                    Keywords:
                    {keywords}
                    """

                    latex_code = st.session_state.ai_handler.generate_latex(
                        article_content,
                        title,
                        authors
                    )
                    
                    # Mostrar el código generado
                    st.markdown("### Código LaTeX Generado")
                    st.code(latex_code, language="latex")
                    
                    # Botones de descarga y copiado
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "📥 Descargar código LaTeX",
                            latex_code,
                            "articulo.tex",
                            "text/plain"
                        )
                    with col2:
                        if st.button("📋 Copiar al portapapeles"):
                            pyperclip.copy(latex_code)
                            st.success("¡Código copiado!")
                    
                    # Instrucciones de uso
                    with st.expander("📚 Instrucciones de Uso", expanded=True):
                        st.markdown("""
                        ### Pasos para compilar el documento:
                        
                        1. **Instalación de requisitos**:
                           - Instala una distribución TeX (TeX Live o MiKTeX)
                           - Asegúrate de tener instalada la plantilla cup-ino
                           - Instala los paquetes necesarios:
                             * longtable
                             * blindtext
                             * graphicx
                             * booktabs
                             * rotating
                             * biblatex-chicago
                        
                        2. **Preparación del entorno**:
                           - Guarda el código LaTeX en un archivo con extensión `.tex`
                           - Asegúrate de tener las imágenes en la ruta especificada
                           - Crea un archivo `refs.bib` con las referencias bibliográficas
                        
                        3. **Compilación**:
                           ```bash
                           # Primera compilación
                           pdflatex articulo.tex
                           
                           # Procesar referencias bibliográficas
                           biber articulo
                           
                           # Segunda y tercera compilación
                           pdflatex articulo.tex
                           pdflatex articulo.tex
                           ```
                        
                        4. **Solución de problemas comunes**:
                           - Si hay errores de compilación, revisa los logs
                           - Verifica que todos los paquetes estén instalados
                           - Asegúrate de que las rutas de las imágenes sean correctas
                        
                        5. **Recomendaciones**:
                           - Usa un editor LaTeX como TeXstudio, TeXmaker o VS Code con extensión LaTeX
                           - Compila frecuentemente para detectar errores temprano
                           - Mantén una estructura de carpetas ordenada
                        """)
                    
                    # Mostrar vista previa si es posible
                    st.markdown("### Estructura del Documento")
                    st.markdown("""
                    ```
                    📄 articulo.tex
                    ├── 📑 Título y Autores
                    ├── 📝 Abstract
                    ├── 📚 Introducción
                    ├── 🎯 Objetivos
                    ├── 🔬 Metodología
                    ├── 📊 Resultados
                    ├── 💭 Discusión
                    ├── ✍️ Conclusiones
                    ├── 🙏 Agradecimientos
                    └── 📚 Referencias
                    ```
                    """)
                    
                except Exception as e:
                    st.error(f"Error al generar el código LaTeX: {str(e)}")

if __name__ == "__main__":
    main()