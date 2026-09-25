import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTG Deckbuilder", layout="centered")

# ==========================================
# 1. ファイルIDの管理辞書
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
        if "のファイルID" in file_id: continue
        try:
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            dfs.append(pd.read_csv(download_url))
        except Exception:
            pass
            
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df.columns = combined_df.columns.str.lower()
        return combined_df
    else:
        return pd.DataFrame(columns=["name", "type"]) 

# ==========================================
# 3. アプリケーションの状態管理
# ==========================================
if "deck" not in st.session_state:
    st.session_state.deck = []

if "pending_format" not in st.session_state:
    st.session_state.pending_format = None

if "current_format" not in st.session_state:
    st.session_state.current_format = "Standard"

if "pending_clear_search" not in st.session_state:
    st.session_state.pending_clear_search = False

if st.session_state.pending_format:
    st.session_state.current_format = st.session_state.pending_format
    st.session_state.pending_format = None

if st.session_state.pending_clear_search:
    if "search_query" in st.session_state:
        st.session_state.search_query = ""
    st.session_state.pending_clear_search = False

def clear_deck_on_format_change():
    st.session_state.pending_clear_search = True
    if st.session_state.get("skip_clear"):
        st.session_state.skip_clear = False
        return
    st.session_state.deck = []
    st.session_state.current_format = st.session_state.format_selector
    st.toast("フォーマットが変更されたため、デッキをリセットしました。", icon="🔄")

st.title("MTG Deckbuilder")

# ==========================================
# 4. フォーマット選択UI
# ==========================================
format_options = ["Standard", "Pioneer", "Modern"]
default_index = format_options.index(st.session_state.current_format)

selected_format = st.selectbox(
    "フォーマットを選択",
    format_options,
    index=default_index,
    key="format_selector",
    on_change=clear_deck_on_format_change
)

df = load_data(selected_format)

# ==========================================
# 5. 検索・追加エリア（サイドボード対応）
# ==========================================
st.header("🔍 カード検索")

if df.empty:
    st.warning("このフォーマットのカードデータが設定されていません。")
else:
    search_input = st.text_input("カード名を入力", key="search_query")

    if search_input:
        results = df[df["name"].str.contains(search_input, case=False, na=False)]
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
            
            # メインとサイドのボタンを並べる
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                add_count = st.number_input("枚数", min_value=1, max_value=max_copies, value=1)
            with col2:
                st.write("")
                st.write("")
                if st.button("メイン追加", use_container_width=True):
                    st.session_state.deck.append({"name": selected_card, "count": add_count, "board": "main"})
                    st.session_state.pending_clear_search = True
                    st.toast(f"メインに {selected_card} を追加しました", icon="✅")
                    st.rerun()
            with col3:
                st.write("")
                st.write("")
                if st.button("サイド追加", use_container_width=True):
                    st.session_state.deck.append({"name": selected_card, "count": add_count, "board": "side"})
                    st.session_state.pending_clear_search = True
                    st.toast(f"サイドに {selected_card} を追加しました", icon="✅")
                    st.rerun()
        else:
            st.warning("見つかりません")

st.divider()

# ==========================================
# 6. デッキダッシュボードエリア
# ==========================================
st.header("📊 ダッシュボード")
deck_df = pd.DataFrame(st.session_state.deck)

# 古いセッションデータとの互換性確保
if not deck_df.empty and "board" not in deck_df.columns:
    deck_df["board"] = "main"

if not deck_df.empty:
    deck_details = pd.merge(deck_df, df, on="name", how="left")
    # 同じカードが複数回追加された場合の合算処理
    deck_details = deck_details.groupby(["name", "board"]).first().reset_index()
    
    # 既存の枚数合算ロジック
    counts = deck_df.groupby(["name", "board"])["count"].sum().reset_index()
    deck_details = pd.merge(deck_details.drop(columns=["count"]), counts, on=["name", "board"])

    possible_type_cols = ["type_line", "type", "タイプ", "card_type"]
    type_col = next((col for col in possible_type_cols if col in deck_details.columns), None)
    possible_cmc_cols = ["cmc", "mana value", "manavalue", "マナ総量", "mana_value"]
    cmc_col = next((col for col in possible_cmc_cols if col in deck_details.columns), None)
    possible_cost_cols = ["mana_cost", "manacost", "mana cost", "マナコスト"]
    cost_col = next((col for col in possible_cost_cols if col in deck_details.columns), None)

    # ★ 追加：マナ総量（CMC）と名前順でソートする処理 ★
    if cmc_col:
        # CMCを数値化（数値変換できないエラー値は0扱い）
        deck_details["sort_cmc"] = pd.to_numeric(deck_details[cmc_col], errors='coerce').fillna(0)
    else:
        deck_details["sort_cmc"] = 0
        
    # マナ総量（昇順） -> 名前（アルファベット順）の優先順位で並び替え
    deck_details = deck_details.sort_values(by=["sort_cmc", "name"]).reset_index(drop=True)

    # カードタイプの分類（土地・クリーチャー・その他）
    deck_details["category"] = "other"
    if type_col:
        type_str = deck_details[type_col].fillna("").astype(str).str.lower()
        deck_details.loc[type_str.str.contains("creature"), "category"] = "creature"
        deck_details.loc[type_str.str.contains("land"), "category"] = "land"

    # メインとサイドを分割
    main_df = deck_details[deck_details["board"] == "main"]
    side_df = deck_details[deck_details["board"] == "side"]
    
    # --- 機能③: デッキ適正（バリデーション）チェック ---
    st.subheader("⚖️ デッキ適正チェック")
    main_count = main_df["count"].sum() if not main_df.empty else 0
    side_count = side_df["count"].sum() if not side_df.empty else 0
    
    over_limit = []
    if type_col:
        deck_details["is_basic"] = deck_details[type_col].fillna("").astype(str).str.lower().apply(lambda x: "basic" in x and "land" in x)
        # メイン・サイド合算での同名カード枚数チェック
        totals = deck_details.groupby(["name", "is_basic"])["count"].sum().reset_index()
        over_limit = totals[(~totals["is_basic"]) & (totals["count"] > 4)]["name"].tolist()

    if main_count > 0 and main_count < 60:
        st.warning(f"⚠️ メインボードが60枚未満です（現在 {main_count}枚）")
    elif side_count > 15:
        st.warning(f"⚠️ サイドボードが15枚を超えています（現在 {side_count}枚）")
    elif over_limit:
        st.error(f"🚫 同名カードの4枚制限を超えています: {', '.join(over_limit)}")
    else:
        st.success("✅ デッキはリーガル（適正）です！")

    # --- KPIとマナカーブ（メインボードのみ集計） ---
    total_lands = main_df.loc[main_df["category"] == "land", "count"].sum() if not main_df.empty else 0
    total_spells = main_count - total_lands
    
    spells_df = main_df[main_df["category"] != "land"].copy() if not main_df.empty else pd.DataFrame()
    if total_spells > 0 and cmc_col and not spells_df.empty:
        spells_df[cmc_col] = pd.to_numeric(spells_df[cmc_col], errors='coerce').fillna(0)
        avg_cmc = (spells_df[cmc_col] * spells_df["count"]).sum() / total_spells
    else:
        avg_cmc = 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("メイン枚数", int(main_count))
    col2.metric("土地", int(total_lands))
    col3.metric("呪文", int(total_spells))
    col4.metric("平均マナ総量", f"{avg_cmc:.2f}")

    st.subheader("📈 マナカーブ（メインボード / 土地を除く）")
    if not spells_df.empty and cmc_col:
        spells_df["numeric_cmc"] = spells_df[cmc_col].astype(int)
        spells_df["マナ総量"] = spells_df["numeric_cmc"].apply(lambda x: min(x, 7))
        curve_data = spells_df.groupby("マナ総量")["count"].sum().to_dict()
        fixed_bins = ["0", "1", "2", "3", "4", "5", "6", "7+"]
        fixed_counts = [curve_data.get(i, 0) for i in range(8)]
        st.bar_chart(pd.DataFrame({"マナ総量": fixed_bins, "count": fixed_counts}).set_index("マナ総量"))

    # --- 機能②: デッキリストの「タイプ別」分割表示と編集 ---
    st.subheader("📋 デッキリスト（枚数変更・削除）")
    
    # 編集用グリッドを描画する共通関数
    def draw_editor(df_subset):
        if df_subset.empty: return pd.DataFrame()
        df_subset = df_subset.copy()
        df_subset["delete"] = False
        cols_to_show = ["delete", "count", "name"] + ([type_col] if type_col else []) + ([cost_col] if cost_col else [])
        return st.data_editor(
            df_subset[cols_to_show],
            column_config={
                "delete": st.column_config.CheckboxColumn("削除", default=False),
                "count": st.column_config.NumberColumn("枚数", min_value=1, max_value=99, step=1),
                "name": st.column_config.TextColumn("name", disabled=True)
            },
            disabled=["name", type_col, cost_col],
            hide_index=True,
            use_container_width=True
        )

    # タブでメインとサイドを分割
    tab_main, tab_side = st.tabs(["メインボード", "サイドボード"])
    
    with tab_main:
        if main_df.empty:
            st.info("メインボードにカードがありません。")
            edited_creatures = edited_others = edited_lands = pd.DataFrame()
        else:
            st.write("🌿 **土地**")
            edited_lands = draw_editor(main_df[main_df["category"] == "land"])
            st.write("👹 **クリーチャー**")
            edited_creatures = draw_editor(main_df[main_df["category"] == "creature"])
            st.write("🔥 **その他の呪文**")
            edited_others = draw_editor(main_df[main_df["category"] == "other"])
            
    with tab_side:
        if side_df.empty:
            st.info("サイドボードにカードがありません。")
            edited_side = pd.DataFrame()
        else:
            edited_side = draw_editor(side_df)

    # 編集結果を回収する関数
    def collect_edits(df_editor, board_name):
        res = []
        if not df_editor.empty:
            for _, row in df_editor.iterrows():
                if not row.get("delete", False):
                    res.append({"name": row["name"], "count": int(row["count"]), "board": board_name})
        return res

    if st.button("更新（枚数変更・削除を反映）", type="primary"):
        new_deck = []
        new_deck.extend(collect_edits(edited_lands, "main"))
        new_deck.extend(collect_edits(edited_creatures, "main"))
        new_deck.extend(collect_edits(edited_others, "main"))
        new_deck.extend(collect_edits(edited_side, "side"))
        st.session_state.deck = new_deck
        st.rerun()

    # --- エクスポート（サイドボード対応） ---
    st.subheader("アリーナ用エクスポート")
    export_lines = [f"Format: {selected_format}", "", "Deck"]
    for _, row in main_df.iterrows():
        export_lines.append(f"{row['count']} {row['name']}")
        
    if not side_df.empty:
        export_lines.extend(["", "Sideboard"])
        for _, row in side_df.iterrows():
            export_lines.append(f"{row['count']} {row['name']}")
            
    export_text = "\n".join(export_lines)
    st.code(export_text, language="text")
    
    if st.button("🗑️ デッキをすべてリセット", use_container_width=True):
        st.session_state.deck = []
        st.session_state.pending_clear_search = True
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
        st.download_button(
            label="テキストファイルとして保存",
            data=export_text, # 組み立て済みのエクスポートテキストを流用
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
    import_text = st.text_area("テキストを貼り付け", height=150)
    
    if st.button("テキストからデッキを復元", use_container_width=True):
        if import_text.strip():
            new_deck = []
            detected_format = None
            current_board = "main" # 読み込み時のボード判定用
            
            for line in import_text.split('\n'):
                line = line.strip()
                if not line: continue
                
                # フォーマットタグの検知
                if line.lower().startswith("format:"):
                    fmt_str = line.split(":", 1)[1].strip().lower()
                    if "standard" in fmt_str: detected_format = "Standard"
                    elif "pioneer" in fmt_str: detected_format = "Pioneer"
                    elif "modern" in fmt_str: detected_format = "Modern"
                    continue
                    
                # ボード切り替えタグの検知
                if line.lower() in ["deck", "commander"]:
                    current_board = "main"
                    continue
                if line.lower() == "sideboard":
                    current_board = "side"
                    continue
                
                parts = line.split(" ", 1)
                if len(parts) == 2 and parts[0].isdigit():
                    new_deck.append({"name": parts[1].strip(), "count": int(parts[0]), "board": current_board})
            
            if new_deck:
                if not detected_format:
                    card_names = [card["name"].lower() for card in new_deck]
                    for check_fmt in ["Standard", "Pioneer", "Modern"]:
                        temp_df = load_data(check_fmt)
                        if not temp_df.empty:
                            temp_cards = set(temp_df["name"].str.lower().tolist())
                            if all(name in temp_cards for name in card_names):
                                detected_format = check_fmt
                                break
                                
                if detected_format and detected_format != st.session_state.current_format:
                    st.session_state.pending_format = detected_format
                    
                st.session_state.deck = new_deck
                st.success(f"デッキを読み込みました！ (自動判定: {detected_format or '不明'})")
                st.session_state.pending_clear_search = True
                st.rerun()
            else:
                st.error("読み込めるカードが見つかりませんでした。")
