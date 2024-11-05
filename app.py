import streamlit as st
import pandas as pd

# CSVファイルを読み込む
data = pd.read_csv("combined_output.csv")
search_index = pd.read_csv("search_index.csv", header=None, names=["検査項目"], encoding='shift_jis')

# 検索機能
def to_half_width(text):
    return text.translate(str.maketrans('！-～', '!-~', '。'))  # 全角から半角への変換

承認等番号 = st.text_input("体外診薬-承認等番号")
販売名 = st.text_input("体外診薬-販売名")
一般的名称 = st.text_input("体外診薬-一般的名称")
製造販売業者 = st.text_input("体外診薬-製造販売業者")

# 検索ボタン
if st.button("検索"):
    filtered_data = data.copy()

    # フィルタリング（全角半角、大文字小文字を区別しない）
    if 承認等番号:
        承認等番号_normalized = to_half_width(承認等番号).lower()
        filtered_data = filtered_data[filtered_data['体外診薬-承認等番号'].astype(str).apply(lambda x: to_half_width(x).lower().find(承認等番号_normalized) != -1)]
    if 販売名:
        販売名_normalized = to_half_width(販売名).lower()
        filtered_data = filtered_data[filtered_data['体外診薬-販売名'].astype(str).apply(lambda x: to_half_width(x).lower().find(販売名_normalized) != -1)]
    if 一般的名称:
        一般的名称_normalized = to_half_width(一般的名称).lower()
        filtered_data = filtered_data[filtered_data['体外診薬-一般的名称'].astype(str).apply(lambda x: to_half_width(x).lower().find(一般的名称_normalized) != -1)]
    if 製造販売業者:
        製造販売業者_normalized = to_half_width(製造販売業者).lower()
        filtered_data = filtered_data[filtered_data['体外診薬-製造販売業者'].astype(str).apply(lambda x: to_half_width(x).lower().find(製造販売業者_normalized) != -1)]

    # セッションステートにフィルタリングされたデータを保存
    st.session_state.filtered_data = filtered_data

if 'filtered_data' in st.session_state and not st.session_state.filtered_data.empty:
    st.write("検索結果:")
    
    # 詳細情報の列を追加
    st.session_state.filtered_data['詳細情報'] = st.session_state.filtered_data[['JLAC11-測定物（名称）', 
                                                                                  'JLAC11-識別（名称）', 
                                                                                  'JLAC11-材料（名称）', 
                                                                                  'JLAC11-測定法（名称）', 
                                                                                  'JLAC11-結果単位（名称）']].agg(' | '.join, axis=1)

    selected_rows = []
    for index, row in st.session_state.filtered_data.iterrows():
        # JLAC11-17と詳細情報を表示
        checkbox_label = f"{row['JLAC11-17']} - detail: {row['詳細情報']}"
        checkbox = st.checkbox(checkbox_label, key=index)
        if checkbox:
            selected_rows.append(row)

    # マッピングに移行ボタン
    if st.button("マッピングに移行する"):
        if len(selected_rows) == 1:  # 1件だけ選択されているか確認
            selected_row = selected_rows[0]
            st.write("選択された項目:")
            st.write(f"JLAC11-17: {selected_row['JLAC11-17']}")
            st.write(f"詳細情報: {selected_row['詳細情報']}")
            
            # search_index.csvの項目をチェックボックス付きで表示
            st.write("登録が必要な検査項目:")
            selected_index = st.selectbox("検査項目を選択:", search_index["検査項目"].tolist())
            st.checkbox(selected_index)

        else:
            st.warning("チェックボックスを一つだけ選択してください。")
else:
    st.warning("検索結果がありません。")
