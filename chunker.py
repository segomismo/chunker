version = "0.3.8.08"
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

def main():
    if 'pdf_texts' not in st.session_state:
        st.session_state.pdf_texts = []
        
    if 'pdf_texts_chunk' not in st.session_state:
        st.session_state.pdf_texts_chunk = []
    
    if 'pdf_texts_chunked' not in st.session_state:
        st.session_state.pdf_texts_chunked = []

    st.set_page_config(page_title="ChunkPDF", page_icon=":carpentry_saw:")
    st.title("ChunkPDF")
    st.sidebar.title("Links de los chunks")
    pdf_docs = st.file_uploader("Sube tus PDFs aquí y clicka en 'Procesar'", accept_multiple_files=True)
    max_tokens = st.number_input("Máximo de tokens por chunk", min_value=100, max_value=10000, value=3500, step=100)

    if st.button("Procesar"):
        with st.spinner("Procesando..."):
            st.session_state.pdf_texts = []
            for pdf_doc in pdf_docs:
                pdf_text = extract_text_from_pdf(pdf_doc)
                st.session_state.pdf_texts.append(pdf_text)

            st.session_state.pdf_texts_chunk = []

            for pdf_text in st.session_state.pdf_texts:
                chunks = chunk_text(pdf_text, max_tokens)
                st.session_state.pdf_texts_chunk += chunks
                    
            st.write(len(st.session_state.pdf_texts_chunk))
    
    for i in range(len(st.session_state.pdf_texts_chunk)):
        st.markdown(f"## Chunk {i+1} de {len(st.session_state.pdf_texts_chunk)}")
        st.write(st.session_state.pdf_texts_chunk[i])
        st.write("----")
        st.write("----")
        st.write("----")

    with st.sidebar:
        for i in range(len(st.session_state.pdf_texts_chunk)):
            st.markdown(f"[Chunk {i+1}](#chunk-{i+1}-de-{len(st.session_state.pdf_texts_chunk)})")


if __name__ == "__main__":
    main()