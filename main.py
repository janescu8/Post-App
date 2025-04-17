import streamlit as st
from datetime import datetime
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase
if not firebase_admin._apps:
    firebase_key_dict = json.loads(st.secrets["FIREBASE_JSON"])
    cred = credentials.Certificate(firebase_key_dict)  # ✅
    firebase_admin.initialize_app(cred)

# 建立 Firestore 客戶端
db = firestore.client()

# 預設 admin 清單
ADMIN_USERS = ["Arfaa", "Sanny"]

# 使用者登入名稱
if 'username' not in st.session_state:
    st.session_state.username = st.text_input("請輸入你的名稱 / Enter your name")
    st.stop()

# 判斷是否為 Admin
is_admin = st.session_state.username in ADMIN_USERS

# Sidebar 顯示登入者資訊
st.sidebar.success(f"👤 使用者：{st.session_state.username}")
if is_admin:
    st.sidebar.info("🛠️ 你是 Admin！")

# Header
st.title("📝 Mini Social Media / 迷你社群平台")
st.subheader("發佈你的貼文 / Share Your Thoughts")

# 分類清單（中英文對照）
categories = {
    "生活 Life": "生活 Life",
    "學習 Study": "學習 Study",
    "工作 Work": "工作 Work",
    "娛樂 Fun": "娛樂 Fun",
    "其他 Others": "其他 Others"
}

# 發文表單
with st.form("post_form"):
    content = st.text_area("你在想什麼？ / What's on your mind?", max_chars=280)
    category = st.selectbox("選擇分類 / Select Category", list(categories.values()))
    image = st.file_uploader("上傳圖片（選填）/ Upload Image (Optional)", type=["png", "jpg", "jpeg"])
    submitted = st.form_submit_button("發佈 / Post")

    if submitted and content:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_path = None
        if image is not None:
            image_folder = "uploaded_images"
            os.makedirs(image_folder, exist_ok=True)
            image_path = os.path.join(image_folder, f"{timestamp.replace(':', '-')}_{image.name}")
            with open(image_path, "wb") as f:
                f.write(image.read())

        post_ref = db.collection("posts").document()
        post_ref.set({
            "content": content,
            "author": st.session_state.username,
            "timestamp": timestamp,
            "likes": 0,
            "comments": [],
            "category": category,
            "image_path": image_path
        })
        st.rerun()

st.markdown("---")
st.subheader("📬 所有貼文 / All Posts")

search_keyword = st.text_input("🔍 搜尋貼文 / Search posts")

# 讀取所有貼文（由新到舊）
posts_ref = db.collection("posts").order_by("timestamp", direction=firestore.Query.DESCENDING)
docs = posts_ref.stream()

for doc in docs:
    post = doc.to_dict()
    post_id = doc.id
    content = post["content"]
    author = post["author"]
    timestamp = post["timestamp"]
    likes = post.get("likes", 0)
    comments = post.get("comments", [])
    category = post.get("category", "未分類")
    image_path = post.get("image_path")

    if search_keyword and search_keyword.lower() not in content.lower():
        continue

    st.markdown(f"**🗓 {timestamp}**")
    author_label = "👑 " + author if author in ADMIN_USERS else author
    st.markdown(f"👤 {author_label} ｜ 🏷️ {category}")
    st.markdown(f"💬 {content}")

    if image_path and os.path.exists(image_path):
        st.image(image_path, use_column_width=True)

    col1, col2 = st.columns(2)

    # Like 按鈕
    if col1.button(f"👍 {likes}", key=f"like_{post_id}"):
        db.collection("posts").document(post_id).update({"likes": likes + 1})
        st.rerun()

    # 留言區
    comment_count = len(comments)
    with col2.expander(f"💭 留言 / Comments ({comment_count})"):
        with st.form(f"comment_form_{post_id}"):
            comment_text = st.text_input("留言內容 / Your comment", key=f"comment_input_{post_id}")
            send = st.form_submit_button("送出留言 / Submit")
            if send and comment_text:
                comments.append({"author": st.session_state.username, "content": comment_text})
                db.collection("posts").document(post_id).update({"comments": comments})
                st.rerun()

        for j, cmt in enumerate(comments):
            author_tag = "👑 " + cmt['author'] if cmt['author'] in ADMIN_USERS else cmt['author']
            st.markdown(f"- {author_tag}: {cmt['content']}")
            if is_admin:
                if st.button(f"刪除留言 / Delete", key=f"del_comment_{post_id}_{j}"):
                    comments.pop(j)
                    db.collection("posts").document(post_id).update({"comments": comments})
                    st.rerun()

    # 刪除貼文（作者本人或 Admin）
    if is_admin or st.session_state.username == author:
        if st.button("🗑️ 刪除這則貼文 / Delete this post", key=f"delete_{post_id}"):
            db.collection("posts").document(post_id).delete()
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            st.rerun()

    st.markdown("---")
