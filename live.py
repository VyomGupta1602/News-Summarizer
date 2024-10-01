import nest_asyncio
from typing import Optional
import streamlit as st
from duckduckgo_search import DDGS
from phi.tools.newspaper4k import Newspaper4k
import os
from dotenv import load_dotenv
import google.generativeai as genai
os.getenv('GOOGLE_API_KEY')
GOOGLE_API_KEY="AIzaSyCvAxSu606yunRA1kevPLY5gz2oaETcbVo"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')



import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
st.set_page_config(page_title="News Articles",)

st.title("News Articles Summarizer")

st.markdown("Built Using Gemini API")

def Truncated_text(text,words):
    return " ".join(text.split()[:words])


def main():
    summary_model = st.sidebar.selectbox("Select Summary Model",options=["gemini-1.5-flash"])
    
    st.sidebar.markdown("## Research Options")

    per_article_summary_length = st.sidebar.slider(
        ":sparkles: Length of Article Summaries",
        min_value=100,
        max_value=2000,
        value=800,
        step=100,
        help="Number of words per article summary",
    )
    

    article_topic = st.text_input(":spiral_calendar_pad: Enter a topic",value="",)
    
    write_article = st.button("Write Article")
    if write_article:
        news_results = []
        news_summary: Optional[str] = None
        with st.status("Reading News", expanded=False) as status:
            with st.container():
                news_container = st.empty()
                ddgs = DDGS()
                newspaper_tools = Newspaper4k()
                results = ddgs.news(keywords=article_topic, max_results=4)
                for r in results:
                    if "url" in r:
                        article_data = newspaper_tools.get_article_data(r["url"])
                        if article_data and "text" in article_data:
                            r["text"] = article_data["text"]
                            news_results.append(r)
                            if news_results:
                                news_container.write(news_results)
            if news_results:
                news_container.write(news_results)
            status.update(label="News Search Complete", state="complete", expanded=False)

        if len(news_results) > 0:
            news_summary = ""
            with st.status("Summarizing News", expanded=False) as status:
                with st.container():
                    summary_container = st.empty()
                    for news_result in news_results:
                        news_summary += f"### {news_result['title']}\n\n"
                        news_summary += f"- Date: {news_result['date']}\n\n"
                        news_summary += f"- URL: {news_result['url']}\n\n"
                        news_summary += f"#### Introduction\n\n{news_result['body']}\n\n"
                        model = genai.GenerativeModel(summary_model)     
                        config=genai.GenerationConfig(max_output_tokens=per_article_summary_length,temperature=0.7)         
                        response = model.generate_content(contents=[news_result["text"],"Summarize the article"],generation_config=config)
                        print(response.text)
                        _summary = response.text.strip()
                        
                        _summary_length = len(_summary.split())
                        if _summary_length > per_article_summary_length:
                            _summary = _summary[:per_article_summary_length]
                        news_summary += "#### Summary\n\n"
                        news_summary += _summary
                        news_summary += "\n\n---\n\n"
                        if news_summary:
                            summary_container.markdown(news_summary)
                        if len(news_summary.split()) > per_article_summary_length:
                            break


                if news_summary:
                    summary_container.markdown(news_summary)
                status.update(label="News Summarization Complete", state="complete", expanded=True)

        if news_summary is None:
            st.write("Sorry could not find any news or web search results. Please try again.")
            return


    st.sidebar.markdown("---")
    if st.sidebar.button("Restart"):
        st.rerun()

main()