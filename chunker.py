version = "0.5.8.10"
import streamlit as st
from PyPDF2 import PdfReader
import spacy

nlp = spacy.load("es_core_news_sm")

@st.cache_data(ttl=1600)
def extract_text_from_pdf(pdf_path):
    pdf = PdfReader(pdf_path)
    text = ""
    for page in range(len(pdf.pages)):
        text += pdf.pages[page].extract_text()
    return text

@st.cache_data(ttl=1600)
def chunk_text(text, max_tokens):
    doc = nlp(text)
    chunks = []
    current_chunk = []
    current_tokens = 0
    for sentence in doc.sents:
        sentence_tokens = len(sentence)
        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = [str(sentence)]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(str(sentence))
            current_tokens += sentence_tokens
    chunks.append(' '.join(current_chunk)) 
    return chunks

def imprimir_chunks(chunks):
    seguir = ''
    if len(chunks) >= 1:
        st.markdown(f"### :white_check_mark: :green[Consejo:]")
        st.markdown("Clicka sobre cada recuadro de los chunks, :point_right: **'Control + a'** y **'Control + c'** :point_left: para seleccionar todo el contenido del recuadro y para copiar el texto seleccionado del chunk")
        for i in range(len(chunks)):
            st.markdown(f"#### Chunk {i+1} de {len(chunks)}")
            seguir = f"mensaje {i+1} de {len(chunks)}, no digas nada hasta que no llegue al ultimo mensaje \n"
            estadochunk = f" Chunk {i+1} de {len(chunks)}"
            st.text_area(estadochunk, value = seguir + chunks[i], height=200, key=f"chunk {i+1}")
            st.write("----")
    else:
        st.error("No hay chunks para mostrar, carga un PDF y clicka en 'Procesar'")

def procesar_chunks(pdf_docs, max_tokens):
    pdf_texts = []

    for pdf_doc in pdf_docs:
        pdf_text = extract_text_from_pdf(pdf_doc)
        pdf_texts.append(pdf_text)
    
    pdf_texts_chunk = []

    for pdf_text in pdf_texts:
        chunks = chunk_text(pdf_text, max_tokens)
        pdf_texts_chunk += chunks

    st.write(len(pdf_texts_chunk))

    imprimir_chunks(pdf_texts_chunk)

    return pdf_texts_chunk

def main():
    st.set_page_config(page_title="ChunkerPDF", page_icon="🪓")
    st.title("Chunker PDF 🪓")
    st.markdown(f"*Versión: {version}*")

    if 'pdf_texts' not in st.session_state:
        st.session_state.pdf_texts = []
        
    if 'pdf_texts_chunk' not in st.session_state:
        st.session_state.pdf_texts_chunk = []
    
    if 'pdf_texts_chunked' not in st.session_state:
        st.session_state.pdf_texts_chunked = []

    st.markdown("### Carga tus PDFs")
    pdf_docs = st.file_uploader("Sube tus PDFs aquí y clicka en 'Procesar'", accept_multiple_files=True)
    max_tokens = st.number_input("Máximo de tokens por chunk (cantidad de texto)", min_value=100, max_value=10000, value=3500, step=100)
    
    if st.button("Procesar"):
        with st.spinner("Procesando..."):
            st.session_state.pdf_texts_chunk = procesar_chunks(pdf_docs, max_tokens)

    if st.session_state.pdf_texts_chunk:
        st.sidebar.title("Links de los chunks")
        with st.sidebar:
            for i in range(len(st.session_state.pdf_texts_chunk)):
                st.markdown(f"[Chunk {i+1}](#chunk-{i+1}-de-{len(st.session_state.pdf_texts_chunk)})")

if __name__ == "__main__":
    main()