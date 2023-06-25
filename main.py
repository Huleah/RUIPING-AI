import streamlit as st
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import os
import json
import re
from paginator import Paginator
import webbrowser
st.set_page_config(page_title="My Streamlit App", page_icon=":smiley:", layout="wide")

# Render the file uploader
uploaded_file = st.file_uploader("Choose a file")

# If a file was uploaded, read the contents and process the data
if uploaded_file is not None:
    # Read the uploaded file and store the data in a variable
    lines = uploaded_file.read().decode().splitlines() 
    
    @st.cache
    def keyword_extract(lines):
        nltk.download('stopwords')
        nltk.download('punkt')
        with open('/Users/as/Desktop/streamlit/Mesh_term_store.json') as f:
            mesh_terms = json.load(f)['1']
        
        keywords = []

        for text in lines:
            words = word_tokenize(text)
            stop_words = set(stopwords.words('english'))
            filtered_words = [word for word in words if word.lower() not in stop_words]

            pos_tags = nltk.pos_tag(filtered_words)
            noun_tags = ['NN', 'NNS', 'NNP', 'NNPS'] 
            linking_verb_tags = ['is', 'am', 'are', 'was', 'were', 'been', 'being', 'also', 'also', 'may']
            filtered_words = [word for (word, pos) in pos_tags if pos in noun_tags and word.lower() not in linking_verb_tags]
            filtered_text = ' '.join(filtered_words)

            translator = str.maketrans('', '', string.punctuation)
            filtered_text = filtered_text.translate(translator)
            filtered_words = filtered_text.split()

            #filtered_words = [string.lower() for string in filtered_words]
            k = set(filtered_words).intersection(set(mesh_terms))
            keywords.append(k)

        return keywords
    
    # Extract keywords for each line
    keywords = keyword_extract(lines)

    
    
    ## Dashboard
    @st.cache
    def highlight_keywords(text, verbs, nouns):
        for v in verbs:
            text = re.sub(r'\b{}\b'.format(v), f"<mark style='background-color: {'yellow'}'>{v}</mark>", text, flags=re.IGNORECASE)
        for n in nouns:
            text = re.sub(r'\b{}\b'.format(n), f"<mark>{n}</mark>", text, flags=re.IGNORECASE)
        return text

    @st.cache
    def preparation(lines, keywords):
        #show_label = [f"Show{i}" for i in range(1, len(lines)+1)]
        show_key = [f"Button{i}" for i in range(1, len(lines)+1)]
        summary_data = [", ".join(k) for k in keywords]
        result_data = [(f"Result{i}", f"Button{i}") for i in range(1, len(lines)+1)]
        google_search_data= [(f"Search{i}", f"https://scholar.google.com/scholar?q={','.join(keywords[i])}") for i in range(len(lines))]
        return show_key, summary_data, result_data, google_search_data

    show_key, summary_data, result_data, google_search_data = preparation(lines, keywords)

    
    # Define the number of items to display per page
    items_per_page = 20

    # Split the data into pages using Paginator
    paginator = Paginator(result_data, items_per_page)
    page_number = st.sidebar.number_input('Page', 1, len(result_data) // items_per_page + 1, 1, key='page')
    page_data = result_data[(page_number-1)*items_per_page:page_number*items_per_page]
    num_pages = len(result_data) // items_per_page + 1 if len(result_data) % items_per_page != 0 else len(result_data) // items_per_page


    # Render the page selection menu
    start_index = (page_number-1)*items_per_page + 1
    end_index = min(page_number*items_per_page, len(result_data))

    st.sidebar.write(f"Showing {start_index}-{end_index} of {len(result_data)} results")
    st.sidebar.write(f"Total pages: {num_pages}")
    
    
    # Apply the CSS styling to each page
    st.markdown(
        """
        <style>
        .main {
        padding: 0px 0px;
        }   
        
        .block-container {
            margin-top: 0px;
            margin-bottom: 0px;
            margin-left:0px;
            margin-right:0px;
            padding-top: 2rem; 
            padding-bottom: 2rem; 
            padding-left: 2rem; 
            padding-top: 2rem; 
        }
        
        .sidebar-content {
        width: 100px;
        }

        #root {
            max-width: 80%;
            margin-left: auto;
            margin-right: auto;
        }
        body {
        font-size: 16px;
        }        
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f6f6f6;
            text-align: center;
            padding: 5px;
            font-size: 20px;
            font-weight: bold;
            border-top: 1px solid #cccccc;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    
    # Display the results for the current page
    for i, (result, search) in enumerate(page_data):
        st.write('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
        if st.button(f"Google Scholar Search {(page_number-1)*items_per_page+i+1}", key=f"search_{(page_number-1)*items_per_page+i}"):
            webbrowser.open_new_tab(google_search_data[(page_number-1)*items_per_page+i][1])
        #st.write(f'Google Scholar Search: [{search}]({google_search_data[(page_number-1)*items_per_page+i][1]})')
        summary = summary_data[(page_number-1)*items_per_page+i]
        st.write(f'Abstract: {summary}',unsafe_allow_html=True)

        if st.button("Show",key = show_key[(page_number-1)*items_per_page+i]):
            # Highlight the keywords in the text
            text = lines[(page_number-1)*items_per_page+i]
            keywords = keywords[(page_number-1)*items_per_page+i]

            tagged_words = nltk.pos_tag(keywords)
            verbs = [word[0] for word in tagged_words if word[1].startswith("VB")]
            nouns = [word[0] for word in tagged_words if word[1].startswith("NN")]
            highlighted_text = highlight_keywords(text, verbs, nouns)

            # Display the highlighted text
            st.markdown(highlighted_text, unsafe_allow_html=True)
        st.write('---')

    # Display the footer at the bottom of the page
    st.markdown(
        """
        <div class="footer">RUIPING AI - For Internal Evaluation Only</div>
        """,
        unsafe_allow_html=True,
    )


