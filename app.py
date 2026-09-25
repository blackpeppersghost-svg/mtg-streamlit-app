import streamlit as st
import pandas as pd

# layoutをwideからcenteredに変更するとスマホで中央にまとまって見やすくなります
st.set_page_config(page_title="MTG Deckbuilder", layout="centered")


@st.cache_data
def load_data():
    return pd.read_csv("Pioneer_Legal.csv")


df = load_data()

if "deck" not in st.session_state:
    st.session_state.deck = []

st.title("MTG Deckbuilder")

# ==========================================
# 1. 検索・追加エリア（メイン画面の上部に配置）
# ==========================================
st.header("🔍 カード検索")
search_query = st.text_input("カード名を入力")

if search_query:
    results = df[df["Name"].str.contains(search_query, case=False, na=False)]
    if not results.empty:
        selected_card = st.selectbox("検索結果", results["Name"].tolist())

        selected_row = results[results["Name"] == selected_card].iloc[0]
        is_basic_land = False
        if pd.notna(selected_row["Type"]) and "Basic" in selected_row[
            "Type"] and "Land" in selected_row["Type"]:
            is_basic_land = True

        max_copies = 99 if is_basic_land else 4

        # スマホの縦幅を節約するため、枚数入力と追加ボタンを横並びに配置
        col1, col2 = st.columns([2, 1])
        with col1:
            add_count = st.number_input("枚数", min_value=1,
                                        max_value=max_copies, value=1)
        with col2:
            st.write("")  # 高さ調整用の空行
            st.write("")
            if st.button("追加", use_container_width=True):
                st.session_state.deck.append(
                    {"name": selected_card, "count": add_count})
                st.success(f"{selected_card}を追加しました")
    else:
        st.warning("見つかりません")

st.divider()  # 画面の区切り線

# ==========================================
# 2. デッキダッシュボードエリア（画面の下部に配置）
# ==========================================
st.header("📊 現在のデッキ")
deck_df = pd.DataFrame(st.session_state.deck)

if not deck_df.empty:
    total_cards = deck_df["count"].sum()
    st.metric("Total Cards", total_cards)

    st.dataframe(deck_df, use_container_width=True)

    st.subheader("デッキのエクスポート")
    export_text = "\n".join(
        [f"{row['count']} {row['name']}" for _, row in deck_df.iterrows()])
    st.code(export_text, language="text")

    if st.button("デッキをリセット"):
        st.session_state.deck = []
        st.rerun()
else:
    st.info("上の検索バーからカードを追加してください。")