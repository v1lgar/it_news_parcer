import streamlit as st
import pandas as pd
import asyncio
from sqlalchemy import select, func
from app.db.base import AsyncSessionLocal
from app.db.models import Article, Tag, article_tags
import plotly.express as px

st.set_page_config(page_title="IT News Dashboard", layout="wide")

async def get_stats():
    async with AsyncSessionLocal() as session:
        # Top tags
        tag_stmt = (
            select(Tag.name, func.count(article_tags.c.article_id).label("count"))
            .join(article_tags)
            .group_by(Tag.name)
            .order_by(func.count(article_tags.c.article_id).desc())
            .limit(10)
        )
        tag_res = await session.execute(tag_stmt)
        top_tags = tag_res.all()
        
        # Dynamics
        dyn_stmt = (
            select(func.date(Article.published_at).label("date"), func.count(Article.id).label("count"))
            .group_by(func.date(Article.published_at))
            .order_by(func.date(Article.published_at))
        )
        dyn_res = await session.execute(dyn_stmt)
        dynamics = dyn_res.all()
        
        return top_tags, dynamics

def main():
    st.title("IT News Parser Dashboard")
    
    # In Streamlit we run async with a bit of a hack or using a runner
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        top_tags, dynamics = loop.run_until_complete(get_stats())
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Tags")
        if top_tags:
            df_tags = pd.DataFrame(top_tags, columns=["Tag", "Count"])
            fig = px.bar(df_tags, x="Tag", y="Count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available")
            
    with col2:
        st.subheader("Publication Dynamics")
        if dynamics:
            df_dyn = pd.DataFrame(dynamics, columns=["Date", "Count"])
            fig = px.line(df_dyn, x="Date", y="Count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available")

    st.subheader("Recent Articles")
    async def get_recent():
        async with AsyncSessionLocal() as session:
            stmt = select(Article).order_by(Article.published_at.desc()).limit(20)
            res = await session.execute(stmt)
            return res.scalars().all()
    
    recent = loop.run_until_complete(get_recent())
    if recent:
        df_recent = pd.DataFrame([
            {"Title": a.title, "Published At": a.published_at, "URL": a.url}
            for a in recent
        ])
        st.table(df_recent)

if __name__ == "__main__":
    main()
