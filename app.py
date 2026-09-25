import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTG Deckbuilder", layout="centered")

# ==========================================
# 1. ファイルIDの管理辞書（21ファイル分）
# ==========================================
FILE_IDS = {
    "Standard": {
        "w": "1HHl4CyA5l5V6pI_pWn1ErzlEtKfwtbTI",
        "u": "1bFt3xcSLzjMC_btaBlcxPGJLUGo6MT-X",
        "b": "1UyifeB-Zci-2Yy8FlHbY9ma-eONLhH_7",
        "r": "1YcGpnANbRSUZvd2BzTqF0X1sdhCJhI4n",
        "g": "1Tm34l9xgvF_YL6MWDq6ySXm4qF9BQ65a",
        "multi": "1bvLgUHiNsWOQJ6oSfpuyUDg_M9ERjjgJ",
        "colorless_lands": "1o0BpPmmFSFR_sFNuuWY_pKrBArR0tRYH"
    },
    "Pioneer": {
        "w": "1dOSpbW02jTLuf9yt2qFAFhMxgMSQzz0i",
        "u": "1pDozcxPXBadaT08bHXHl1AGgce8Ce6Qo",
        "b": "1u2hW3XjvX6S7MdCfumNsjXJBqR6Xc7z1",
        "r": "1C3L3kUAXbT5dJ5xH7oeyhaH_ww3bYclh",
        "g": "1zcuj7QitpFkxzLoyZh9jdlVxU9aF8ttU",
        "multi": "15EHV5AjN2aZ3OBGcGXZi5U31sYernqC6",
        "colorless_lands": "1T_rbgVqsgGEi95GufujvQqT8v3toor2m"
    },
    "Modern": {
        "w": "1p7Mr6AgDOX-AwIquH0h1XwwRgDdHd-bI",
        "u": "1Z_0oS2sPBCiSBSyc-HaWBdjg2E4xp2ff",
        "b": "1Hpz42xcULx-lEVypEeZyqAwYv3mCVy-n",
        "r": "1YYM8HlZpaK10C1EC3EbRittZw-6CfOEV",
        "g": "14fmAi912qt_naJfYyADoy5rDGJrQPmoy",
        "multi": "1zzNcq_BTZR7cL1d92q69S3DoFjSbClqJ",
        "colorless_lands": "1aC9ajINQ4tu62b0x05EHHyUmwVYGWuKJ"
    }
}

# ==========================================
# 2. データの読み込み関数
# 引数にフォーマット名を受け取るように変更
# ==========================================
@st.cache_data
def load_data(format_name):
    file_ids = FILE_IDS.get(format_name, {})
    dfs = []
    
    for key, file_id in file_ids.items():
        # IDが未入力のものはスキップする処理（エラー回避用）
        if "のファイルID" in file_id:
            continue
            
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        try:
            df = pd.read_csv(download_url)
            dfs.append(df)
        except Exception as e:
            st.error(f"{key} のファイル読み込みに失敗しました。IDを確認してください。")
            
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        # 読み込めるデータがない場合は空のデータフレームを返す
        return pd.DataFrame(columns=["Name", "Type"]) 

# ==========================================
# 3. アプリケーションの状態管理
# ==========================================
if "deck" not in st.session_state:
    st.session_state.deck = []

# フォーマットが変更されたときにデッキを空にする関数
def clear_deck_on_format_change():
    st.session_state.deck = []
    st.toast("フォーマットが変更されたため、デッキをリセットしました。", icon="🔄")

st.title("MTG Deckbuilder")

# ==========================================
# 4. フォーマット選択UI
# ==========================================
selected_format = st.selectbox(
    "フォーマットを選択",
    ["Standard", "Pioneer", "Modern"],
    on_change=clear_deck_on_format_change # 選択が切り替わった瞬間にリセットを実行
)

# 選択されたフォーマットのデータを読み込む
df = load_data(selected_format)

# ==========================================
# 5. 検索・追加エリア
# ==========================================
st.header("🔍 カード検索")

if df.empty:
    st.warning("このフォーマットのカードデータが設定されていません。コード内のファイルIDを入力してください。")
else:
    search_query = st.text_input("カード名を入力")

    if search_query:
        results = df[df["Name"].str.contains(search_query, case=False, na=False)]
        if not results.empty:
            selected_card = st.selectbox("検索結果", results["Name"].tolist())
            
            selected_row = results[results["Name"] == selected_card].iloc[0]
            is_basic_land = False
            if pd.notna(selected_row["Type"]) and "Basic" in selected_row["Type"] and "Land" in selected_row["Type"]:
                is_basic_land = True
                
            max_copies = 99 if is_basic_land else 4
            
            col1, col2 = st.columns([2, 1])
            with col1:
                add_count = st.number_input("枚数", min_value=1, max_value=max_copies, value=1)
            with col2:
                st.write("")
                st.write("")
                if st.button("追加", use_container_width=True):
                    st.session_state.deck.append({"name": selected_card, "count": add_count})
                    st.success(f"{selected_card}を追加しました")
        else:
            st.warning("見つかりません")

st.divider()

# ==========================================
# 6. デッキダッシュボードエリア
# ==========================================
st.header("📊 現在のデッキ")
deck_df = pd.DataFrame(st.session_state.deck)

if not deck_df.empty:
    total_cards = deck_df["count"].sum()
    st.metric("Total Cards", total_cards)
    
    st.dataframe(deck_df, use_container_width=True)
    
    st.subheader("デッキのエクスポート")
    export_text = "\n".join([f"{row['count']} {row['name']}" for _, row in deck_df.iterrows()])
    st.code(export_text, language="text")
    
    if st.button("デッキをリセット"):
        st.session_state.deck = []
        st.rerun()
else:
    st.info("上の検索バーからカードを追加してください。")
