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
# ==========================================
@st.cache_data
def load_data(format_name):
    file_ids = FILE_IDS.get(format_name, {})
    dfs = []
    
    for key, file_id in file_ids.items():
        if "のファイルID" in file_id:
            continue
            
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        try:
            df_temp = pd.read_csv(download_url)
            dfs.append(df_temp)
        except Exception as e:
            st.error(f"{key} のファイル読み込みに失敗しました。IDを確認してください。")
            
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # ★最強の解決策：ここで全列名を強制的に小文字に統一します
        combined_df.columns = combined_df.columns.str.lower()
        
        return combined_df
    else:
        return pd.DataFrame(columns=["name", "type"]) 

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
        # 列名が小文字に統一されたので、常に "name" で安全に検索できます
        results = df[df["name"].str.contains(search_query, case=False, na=False)]
        
        if not results.empty:
            selected_card = st.selectbox("検索結果", results["name"].tolist())
            
            selected_row = results[results["name"] == selected_card].iloc[0]
            is_basic_land = False
            
            # Type列の名前揺れ（type または type_line）にも完璧に対応
            type_col_name = "type_line" if "type_line" in df.columns else "type"
            if type_col_name in df.columns:
                type_val = str(selected_row[type_col_name]).lower()
                if "basic" in type_val and "land" in type_val:
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
st.header("📊 ダッシュボード")
deck_df = pd.DataFrame(st.session_state.deck)

if not deck_df.empty:
    # 修正ポイント: right_on を小文字の "name" に変更（CSVの列名に合わせる）
    deck_details = pd.merge(deck_df, df, on="name", how="left")
    deck_details = deck_details.drop_duplicates(subset=["name"])

    # 列名の揺れを小文字ベースで判定
    type_col = "type_line" if "type_line" in deck_details.columns else "type"
    cmc_col = "cmc"

    # 土地かどうかの判定（NaNエラーを回避して小文字変換後に "land" を含むか）
    deck_details["is_land"] = deck_details[type_col].fillna("").astype(str).str.lower().str.contains("land")

    # -----------------------------------
    # KPI（主要指標）の計算
    # -----------------------------------
    total_cards = deck_details["count"].sum()
    total_lands = deck_details.loc[deck_details["is_land"], "count"].sum()
    total_spells = total_cards - total_lands

    spells_df = deck_details[~deck_details["is_land"]].copy()
    
    if total_spells > 0 and cmc_col in spells_df.columns:
        # CMCを確実に数値化
        spells_df[cmc_col] = pd.to_numeric(spells_df[cmc_col], errors='coerce').fillna(0)
        avg_cmc = (spells_df[cmc_col] * spells_df["count"]).sum() / total_spells
    else:
        avg_cmc = 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("総枚数", int(total_cards))
    col2.metric("土地", int(total_lands))
    col3.metric("呪文", int(total_spells))
    col4.metric("平均マナ総量", f"{avg_cmc:.2f}")

    # -----------------------------------
    # マナカーブ（グラフ）の描画
    # -----------------------------------
    st.subheader("📈 マナカーブ（土地を除く）")
    if not spells_df.empty and cmc_col in spells_df.columns:
        spells_df["マナ総量"] = spells_df[cmc_col].astype(int).astype(str) # 棒グラフのX軸用に文字列化
        mana_curve = spells_df.groupby("マナ総量")["count"].sum().reset_index()
        mana_curve = mana_curve.set_index("マナ総量")
        
        st.bar_chart(mana_curve)
    else:
        st.info("グラフ化できる呪文がありません。")

    # -----------------------------------
    # デッキリストとエクスポート
    # -----------------------------------
    st.subheader("📋 デッキリスト")
    display_cols = ["name", "count"]
    if type_col in deck_details.columns:
        display_cols.append(type_col)
    if "mana_cost" in deck_details.columns:
        display_cols.append("mana_cost") # マナコストのテキストも表示に追加
        
    st.dataframe(deck_details[display_cols], use_container_width=True)
    
    st.subheader("アリーナ用エクスポート")
    export_text = "\n".join([f"{row['count']} {row['name']}" for _, row in deck_df.iterrows()])
    st.code(export_text, language="text")
    
    if st.button("🗑️ デッキをリセット", type="primary", use_container_width=True):
        st.session_state.deck = []
        st.rerun()
else:
    st.info("上の検索バーからカードを追加してください。")
