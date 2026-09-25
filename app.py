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
        # ここで全列名を強制的に小文字に統一します（大文字小文字のエラー回避）
        combined_df.columns = combined_df.columns.str.lower()
        return combined_df
    else:
        return pd.DataFrame(columns=["name", "type"]) 

# ==========================================
# 3. アプリケーションの状態管理
# ==========================================
if "deck" not in st.session_state:
    st.session_state.deck = []

# フォーマット自動切り替え時のリセットを防止するフラグ
if "skip_clear" not in st.session_state:
    st.session_state.skip_clear = False

def clear_deck_on_format_change():
    # インポート機能によって自動で切り替わった場合はリセットを回避
    if st.session_state.skip_clear:
        st.session_state.skip_clear = False
        return
        
    st.session_state.deck = []
    st.toast("フォーマットが変更されたため、デッキをリセットしました。", icon="🔄")

st.title("MTG Deckbuilder")

# ==========================================
# 4. フォーマット選択UI
# ==========================================
selected_format = st.selectbox(
    "フォーマットを選択",
    ["Standard", "Pioneer", "Modern"],
    key="format_selector", # プログラムから動かせるようにキーを設定
    on_change=clear_deck_on_format_change
)

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
        results = df[df["name"].str.contains(search_query, case=False, na=False)]
        
        if not results.empty:
            selected_card = st.selectbox("検索結果", results["name"].tolist())
            
            selected_row = results[results["name"] == selected_card].iloc[0]
            is_basic_land = False
            
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
    deck_details = pd.merge(deck_df, df, on="name", how="left")
    deck_details = deck_details.drop_duplicates(subset=["name"])

    # 【重要】列名が存在しなかった場合のフォールバック（自動検出）
    possible_type_cols = ["type_line", "type", "タイプ", "card_type"]
    type_col = next((col for col in possible_type_cols if col in deck_details.columns), None)

    possible_cmc_cols = ["cmc", "mana value", "manavalue", "マナ総量", "mana_value"]
    cmc_col = next((col for col in possible_cmc_cols if col in deck_details.columns), None)

    possible_cost_cols = ["mana_cost", "manacost", "mana cost", "マナコスト"]
    cost_col = next((col for col in possible_cost_cols if col in deck_details.columns), None)

    # 土地かどうかの判定
    if type_col:
        deck_details["is_land"] = deck_details[type_col].fillna("").astype(str).str.lower().str.contains("land")
    else:
        deck_details["is_land"] = False

    # -----------------------------------
    # KPI計算
    # -----------------------------------
    total_cards = deck_details["count"].sum()
    total_lands = deck_details.loc[deck_details["is_land"], "count"].sum()
    total_spells = total_cards - total_lands

    spells_df = deck_details[~deck_details["is_land"]].copy()
    
    if total_spells > 0 and cmc_col:
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
    # マナカーブグラフ
    # -----------------------------------
    st.subheader("📈 マナカーブ（土地を除く）")
    if cmc_col is None:
        st.error("⚠️ ドライブのCSVデータ内にマナ総量（CMC）を示す列が存在しないため、グラフを描画できません。")
        st.info(f"💡 【デバッグ用】現在読み込んでいるCSVの列名一覧: {', '.join(df.columns)}")
    elif not spells_df.empty:
        # CMCを整数に変換
        spells_df["numeric_cmc"] = spells_df[cmc_col].astype(int)
        
        # 7以上のコストはすべて「7」として扱う
        spells_df["マナ総量"] = spells_df["numeric_cmc"].apply(lambda x: min(x, 7))
        
        # マナ総量ごとの枚数を集計
        curve_data = spells_df.groupby("マナ総量")["count"].sum().to_dict()
        
        # 「0」から「7+」までの固定の枠（ビン）を作成
        fixed_bins = ["0", "1", "2", "3", "4", "5", "6", "7+"]
        fixed_counts = []
        
        for i in range(8):
            # curve_dataに該当のマナ域があればその枚数を、なければ0を追加
            fixed_counts.append(curve_data.get(i, 0))
            
        # グラフ描画用の新しいデータフレームを作成
        mana_curve_df = pd.DataFrame({
            "マナ総量": fixed_bins,
            "count": fixed_counts
        }).set_index("マナ総量")
        
        # st.bar_chartで描画
        st.bar_chart(mana_curve_df)
    else:
        st.info("グラフ化できる呪文がありません。")

    # -----------------------------------
    # デッキリストとエクスポート（編集可能バージョン）
    # -----------------------------------
    st.subheader("📋 デッキリスト（枚数変更・削除）")
    
    # 画面に表示する用の列を用意
    display_cols = ["name", "count"]
    if type_col:
        display_cols.append(type_col)
    if cost_col:
        display_cols.append(cost_col)
        
    # 削除用のチェックボックス列（初期値は全てFalse）を追加
    deck_details["delete"] = False
    
    # ユーザーが編集できるデータグリッド（st.data_editor）を表示
    # - 編集できるのは「count（枚数）」と「delete（削除）」のみに制限
    edited_df = st.data_editor(
        deck_details[["delete", "count", "name"] + ([type_col] if type_col else []) + ([cost_col] if cost_col else [])],
        column_config={
            "delete": st.column_config.CheckboxColumn("削除", default=False),
            "count": st.column_config.NumberColumn("枚数", min_value=1, max_value=99, step=1),
            "name": st.column_config.TextColumn("name", disabled=True), # 名前は編集不可
            type_col: st.column_config.TextColumn(type_col, disabled=True) if type_col else None, # タイプは編集不可
            cost_col: st.column_config.TextColumn(cost_col, disabled=True) if cost_col else None  # コストは編集不可
        },
        disabled=["name", type_col, cost_col], # 万が一のための再ロック
        hide_index=True, # 行番号は不要なので隠す
        use_container_width=True
    )
    
    # 編集された結果（edited_df）をもとに、st.session_state.deck を更新するボタン
    if st.button("更新（枚数変更・削除を反映）", type="primary"):
        new_deck = []
        for index, row in edited_df.iterrows():
            # 削除チェックが入っていないカードだけを残す
            if not row["delete"]:
                new_deck.append({"name": row["name"], "count": int(row["count"])})
        
        # セッションステートを上書きして画面を再描画
        st.session_state.deck = new_deck
        st.rerun()

    # --- (ダッシュボードの表示部分はそのまま) ---

    st.subheader("アリーナ用エクスポート")
    # フォーマット情報を先頭に付与（MTGアリーナ互換）
    export_lines = [f"Format: {selected_format}", "", "Deck"]
    export_lines.extend([f"{row['count']} {row['name']}" for _, row in deck_df.iterrows()])
    export_text = "\n".join(export_lines)
    st.code(export_text, language="text")
    
    if st.button("🗑️ デッキをすべてリセット", use_container_width=True):
        st.session_state.deck = []
        st.rerun()
else:
    st.info("上の検索バーからカードを追加してください。")

st.divider()

# ==========================================
# 7. デッキの保存・読み込みエリア
# ==========================================
st.header("💾 デッキの保存・読み込み")

col_import, col_export = st.columns(2)

with col_export:
    st.subheader("📤 保存 (ダウンロード)")
    if not deck_df.empty:
        save_lines = [f"Format: {selected_format}", "", "Deck"]
        save_lines.extend([f"{row['count']} {row['name']}" for _, row in deck_df.iterrows()])
        save_text = "\n".join(save_lines)
        
        st.download_button(
            label="テキストファイルとして保存",
            data=save_text,
            file_name="my_deck.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )
        st.info("MTGアリーナ互換の形式で保存されます。")
    else:
        st.info("デッキが空です。")

with col_import:
    st.subheader("📥 読み込み (自動判定)")
    import_text = st.text_area(
        "テキストを貼り付け", 
        height=150, 
        placeholder="Format: Standard\n\nDeck\n4 Dark Matter Manipulator\n22 Swamp"
    )
    
    if st.button("テキストからデッキを復元", use_container_width=True):
        if import_text.strip():
            new_deck = []
            detected_format = None
            lines = import_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 1. フォーマット指定タグの読み取り
                if line.lower().startswith("format:"):
                    fmt_str = line.split(":", 1)[1].strip().lower()
                    if "standard" in fmt_str:
                        detected_format = "Standard"
                    elif "pioneer" in fmt_str:
                        detected_format = "Pioneer"
                    elif "modern" in fmt_str:
                        detected_format = "Modern"
                    continue
                    
                # "Deck" や "Sideboard" などのヘッダーはスキップ
                if line.lower() in ["deck", "commander", "sideboard"]:
                    continue
                
                # 2. カードの抽出
                parts = line.split(" ", 1)
                if len(parts) == 2 and parts[0].isdigit():
                    count = int(parts[0])
                    name = parts[1].strip()
                    new_deck.append({"name": name, "count": count})
            
            if new_deck:
                # 3. 最強機能：タグが無かった場合の「カードプールからの逆引き判定」
                if not detected_format:
                    card_names = [card["name"].lower() for card in new_deck]
                    for check_fmt in ["Standard", "Pioneer", "Modern"]:
                        temp_df = load_data(check_fmt)
                        if not temp_df.empty:
                            temp_cards = set(temp_df["name"].str.lower().tolist())
                            # すべてのカードがそのフォーマットに存在するかチェック
                            if all(name in temp_cards for name in card_names):
                                detected_format = check_fmt
                                break
                                
                # フォーマットの自動切り替え（現在と違う場合のみ）
                if detected_format and detected_format != st.session_state.format_selector:
                    st.session_state.skip_clear = True
                    st.session_state.format_selector = detected_format
                    
                st.session_state.deck = new_deck
                st.success(f"デッキを読み込みました！ (自動判定: {detected_format or '不明'})")
                st.rerun()
            else:
                st.error("読み込めるカードが見つかりませんでした。")
