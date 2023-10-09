import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import time
from PyPDF2 import PdfReader
from PIL import Image
import openai
import os
import pickle
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document



st.set_page_config(page_title="Sumquiry ", page_icon=":robot:")
from dotenv import load_dotenv
def get_vectorstore(text_chunks, cache_file = "knowledge_base.pkl"):
    try:
        # Try to load the knowledge base from the pickle file
        with open(cache_file, 'rb') as file:
            knowledge_base = pickle.load(file)
        print("Loaded knowledge_base from file:", cache_file)
    except FileNotFoundError:
        # If the pickle file doesn't exist, compute the knowledge base
        start_time = time.time()
        embeddings = HuggingFaceEmbeddings()
        knowledge_base = FAISS.from_texts(text_chunks, embeddings)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Computed knowledge_base in:", elapsed_time)
        
        # Save the computed knowledge_base to the pickle file
        with open(cache_file, 'wb') as file:
            pickle.dump(knowledge_base, file)
        print("Saved knowledge_base to file:", cache_file)

    return knowledge_base

load_dotenv()  # take environment variables from .env.

openai.api_key = os.environ["OPENAI_API_KEY"]

page_bg = f"""
<style>
[data-testid="stSidebar"] {{
background-color:#0d0d0c;

}}

[data-testid="stToolbar"] {{
background-color:#FCFCFC;

}}
</style>
"""
st.markdown(page_bg,unsafe_allow_html=True)

# Sidebar contents
with st.sidebar:

    image = Image.open('download.jpeg')
    st.image(image)
    st.markdown("<h3 style='text-align: left'> Intelligent PDF Summarizer and Inquiry Companion </h3>", unsafe_allow_html= True)
    st.markdown("""
            <br><p style='text-align: left;'>With Sumquiry, you can quickly obtain concise and accurate summaries of lengthy documents, saving valuable time. \
            But that's not all - you can ask detailed questions about the content and receive insightful responses, \
            transforming your research experience into an interactive and efficient journey. Say goodbye to information overload \
            and hello to a seamless exploration of knowledge with Sumquiry as your trusted companion.</p>
    """, unsafe_allow_html=True)
    
    add_vertical_space(5)
    st.markdown("<p> Made by <a href='https://nikshingadiya.github.io/'>nikhil shingadiya</a> </p>", unsafe_allow_html=True)

# Clear input text
def clear_text():
    st.session_state["input"] = ""

st.header("Sumquiry")
# upload file
pdf = st.file_uploader("Upload your PDF", type="pdf")

# extract the text
if pdf is not None:
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    # split into chunks
    text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
    )

    chunks = text_splitter.split_text(text)
      
    # create docs
    docs = [Document(page_content=t) for t in chunks[:3]]
    llm = OpenAI(temperature=0, openai_api_key=os.environ["OPENAI_API_KEY"])

    # show summarize doc
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summarized_docs = chain.run(docs)
    st.write("Summary")
    st.write(summarized_docs)

    # create embeddings
    # embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    knowledge_base =get_vectorstore(chunks)

    # show user input
    user_question = st.text_input("Ask a question about your PDF", key="input")

    # show button for clear question
    st.button("Clear Text", on_click=clear_text)

    if user_question:
        docs = knowledge_base.similarity_search(user_question)
        chain = load_qa_chain(llm, chain_type="stuff")
        with get_openai_callback() as cb:
            response = chain.run(input_documents=docs, question=user_question)
            print(type(cb))
            st.write(response)
            st.write(f"Total Tokens: {cb.total_tokens}" f", Prompt Tokens: {cb.prompt_tokens}" f", Completion Tokens: {cb.completion_tokens}" f", Total Cost (USD): ${cb.total_cost}")

            # response_tokens = cb['usage']['total_tokens']
            # st.write(f"User Token Limit: {user_question_tokens}")
            # st.write(f"Total Tokens Used in Response: {response_tokens}")