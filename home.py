import streamlit as st
import openai
from supabase import create_client
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

st.markdown(
    """
<style>
footer {
    visibility: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)

supabase = init_connection()


st.title("Recommend Book Report✍️")
openai.api_key = st.secrets.OPENAI_TOKEN
def generate_prompt(genre,genre2, writer, description, keywords,n):
    prompt =  f""" 
특정 도서 장르에 대한 교수님의 의견을 바탕으로 관련 도서를 추천하는 프롬프트입니다
제공된 정보를 활용하여 관련 도서를 자세히 소개하고, 해당 도서와 연관된 인사이트를 포함해주세요.
{writer}가 입력되었을 때 , 그 저자의 책을 추천합니다.
만약 장르, 작가, 키워드, 도서 설명 등의 정보가 제공되었다면, 해당 정보를 포함하여 작성해주세요.
추천하는 도서의 영문 제목과 한국어 제목을 알려주세요.
 A4 한 장에 작성하고, 추천 도서와 유사한 다른 도서를 총 {n}권 추천해주세요.

---
책의 장르: {genre}
책의 세부 장르:{genre2}
저자 :{writer}
책의 간단한 줄거리: {description}
키워드: {keywords}
---
"""
    return prompt.strip()

def request_chat_completion(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": "당신은 전문 카피라이터입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

st.sidebar.markdown("<h2 style='font-size: 24px;'>Book Search</h2>", unsafe_allow_html=True)
search_query = st.sidebar.text_input("", value="", key="book_search", max_chars=50)
search_button = st.sidebar.button("Search")
with st.form("my_form"):
    genre = st.text_input("장르(필수)", placeholder = "추천받고 싶은 책의 장르를 입력하세요")
    genre2 = st.text_input("세부 장르(선택)", placeholder = "추천받고 싶은 책의 세부 장르를 입력하세요")
    writer = st.text_input("저자(선택)", placeholder = "추천받고 싶은 책의 저자를 입력하세요")
    desc = st.text_input("줄거리(선택)", placeholder="책에 관한 간단한 줄거리를 입력하세요")
    st.text("포함할 키워드(최대 3개까지 허용)")

    col1, col2, col3 = st.columns(3)
    with col1:
        keyword_one = st.text_input(
            placeholder="키워드 1",
            label="keyword_1",
            label_visibility="collapsed"
        )
    with col2:
        keyword_two = st.text_input(
            placeholder="키워드 2",
            label="keyword_2",
            label_visibility="collapsed"
        )
    with col3:
        keyword_three = st.text_input(
            placeholder="키워드 3",
            label="keyword_3",
            label_visibility="collapsed"
        )
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not genre:
            st.error("장르를 입력해주세요.")
        else:
            keywords = [keyword_one,keyword_two, keyword_three]
            keywords = [x for x in keywords if x]
            prompt = generate_prompt(genre,genre2,writer,desc,keywords,n=3 )
            with st.spinner("장르에 맞는 책을 추천해주고 있습니다..."):
                generated_text = request_chat_completion(prompt)
            st.text_area(
                label="독후감 생성 결과",
                value= generated_text,
                height=200
            )

    if 'search_history' not in st.session_state:
        st.session_state.search_history = []

    st.sidebar.markdown("## Search History")
    for item in st.session_state.search_history:
        st.sidebar.write(item)

    if search_button:
        if search_query:
            st.session_state.search_history.append(search_query)

    reset_button = st.sidebar.button("Reset")
    if reset_button:
        st.session_state.search_history = []
