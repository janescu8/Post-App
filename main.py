import streamlit as st
from datetime import datetime

# 預設 admin 清單（可擴充）
ADMIN_USERS = ["Arfaa", "Sanny"]

# 使用者登入名稱（模擬登入）
if 'username' not in st.session_state:
    st.session_state.username = st.text_input("請輸入你的名稱 / Enter your name")
    st.stop()

# 判斷是否為 Admin
is_admin = st.session_state.username in ADMIN_USERS

# 初始化貼文資料
if 'posts' not in st.session_state:
    st.session_state.posts = []

# Sidebar 顯示登入者資訊
st.sidebar.success(f"👤 使用者：{st.session_state.username}")
if is_admin:
    st.sidebar.info("🛠️ 你是 Admin！")

# Header / 標題
st.title("📝 Mini Social Media / 迷你社群平台")
st.subheader("發佈你的貼文 / Share Your Thoughts")

# Post form / 發文表單
with st.form("post_form"):
    content = st.text_area("你在想什麼？ / What's on your mind?", max_chars=280)
    submitted = st.form_submit_button("發佈 / Post")
    if submitted and content:
        post = {
            "content": content,
            "author": st.session_state.username,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "likes": 0,
            "comments": []
        }
        st.session_state.posts.insert(0, post)  # Add new post to top

st.markdown("---")
st.subheader("📬 所有貼文 / All Posts")

# Display posts / 顯示貼文
for i, post in enumerate(st.session_state.posts):
    st.markdown(f"**🗓 {post['timestamp']}**")
    author_label = "👑 " + post['author'] if post['author'] in ADMIN_USERS else post['author']
    st.markdown(f"👤 {author_label}")
    st.markdown(f"💬 {post['content']}")
    col1, col2 = st.columns(2)

    # Like button / 按讚按鈕
    if col1.button(f"👍 {post['likes']}", key=f"like_{i}"):
        st.session_state.posts[i]['likes'] += 1

    # Comment section / 留言區
    with col2.expander("💭 留言 / Comments"):
        with st.form(f"comment_form_{i}"):
            comment = st.text_input("留言內容 / Your comment", key=f"comment_input_{i}")
            send = st.form_submit_button("送出留言 / Submit")
            if send and comment:
                st.session_state.posts[i]["comments"].append({
                    "author": st.session_state.username,
                    "content": comment
                })

        # Display comments / 顯示留言
        for j, c in enumerate(post["comments"]):
            author_tag = "👑 " + c['author'] if c['author'] in ADMIN_USERS else c['author']
            st.markdown(f"- {author_tag}: {c['content']}")
            if is_admin:
                if st.button(f"刪除留言 / Delete", key=f"del_comment_{i}_{j}"):
                    st.session_state.posts[i]["comments"].pop(j)
                    st.experimental_rerun()

    # 刪除貼文按鈕（限 Admin）
    if is_admin:
        if st.button("🗑️ 刪除這則貼文 / Delete this post", key=f"delete_{i}"):
            st.session_state.posts.pop(i)
            st.experimental_rerun()

    st.markdown("---")
