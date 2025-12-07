import streamlit as st
import anthropic
import os
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="あなたの「座右の銘」一緒に紡ぎましょ",
    page_icon="✨",  # ここでアイコン変更可能（絵文字またはURL）
    layout="wide",
    initial_sidebar_state="collapsed"
)

# カスタムCSS（日本的ミニマリズム）
# 背景色の設定（ここで変更可能）
BG_COLOR_START = "#f5f1e8"  # 背景グラデーション開始色
BG_COLOR_END = "#e8dcc8"    # 背景グラデーション終了色
ACCENT_COLOR = "#5a4a3a"    # アクセントカラー（ボタンなど）

st.markdown(f"""
<style>
    /* 背景 */
    .stApp {{{{
        background: linear-gradient(135deg, {BG_COLOR_START} 0%, {BG_COLOR_END} 100%);
    }}}}
    
    /* タイトル */
    .main-title {{{{
        font-family: 'Georgia', serif;
        color: #3a3a3a;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 300;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }}}}
    
    .subtitle {{{{
        text-align: center;
        color: #6b6b6b;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }}}}
    
    /* チャットメッセージ */
    .stChatMessage {{{{
        background-color: white;
        border: 1px solid #d4c4b0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}}}
    
    /* ボタン */
    .stButton>button {{{{
        background-color: {ACCENT_COLOR};
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        border: none;
        font-weight: 500;
        letter-spacing: 0.05em;
    }}}}
    
    .stButton>button:hover {{{{
        background-color: #6b5a4a;
    }}}}
    
    /* 入力欄 */
    .stTextInput>div>div>input {{{{
        background-color: #faf8f5;
        border: 1px solid #d4c4b0;
    }}}}
    
    /* プログレスバー */
    .step-container {{{{
        background-color: white;
        border: 1px solid #d4c4b0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0 2rem 0;
    }}}}
    
    .step-label {{{{
        color: {ACCENT_COLOR};
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }}}}
</style>
""", unsafe_allow_html=True)

# システムプロンプト
SYSTEM_PROMPT = """# あなたの役割
あなたは「座右の銘」を紡ぐ専門ガイドです。
ユーザーが自分だけの座右の銘を見つけるサポートをします。

## 重要な注意事項
- ドキュメントは参考資料として裏で参照するだけで、ユーザーには一切言及しない
- ドキュメント内の事例（Aさんなど）は参考にするが、ユーザーとの会話には登場させない
- あくまでユーザーと1対1の対話として進める

# 対話の進め方

## 最初の挨拶
ユーザーが初めて来たら：
「ようこそ！一緒にあなただけの座右の銘を紡いでいきましょう。
このプロセスは、未来をブレずに進むための羅針盤になります。
30分ほどお時間をいただきます。準備はよろしいですか？」

## 5つのステップを順番に実施

### ステップ1: 今、一番の問題を見つける
- 「今、あなたにとって一番大きな問題は何ですか？」
- 「それを簡単な一言で表現するとしたら？」
- 深掘り質問を3-5個投げかける
- 最終的に「一言」に落とし込む

### ステップ2: 解決方法を考える
- 「その問題を、あなたならどう解決しますか？」
- 「ありのままの自分で考えた答えは？」
- 具体的な手法まで聞き出す

### ステップ3: 理想の生き方を探る
- 「あなたはどんな人間として生きたいですか？」
- 「来世の役所で『あなたはこういう人間でしたね』と言われたい言葉は？」
- さらに深く掘り下げるために、以下のような質問を投げかける：
  * コーヒーって、あなたにとって何ですか？
  * 時計って、あなたにとって何ですか？
  * 仕事って、あなたにとって何ですか？
  * 家族って、あなたにとって何ですか？
  （他にも、その人の状況に応じて適切な質問を作る）
- 複数の角度から質問し、しっくりくるまで探る

### ステップ4: 乖離を見つける
- 「ステップ3の理想の人間が、ステップ2の方法で問題を解決するでしょうか？」
- 乖離点を丁寧に指摘する
- 「何か違和感はありませんか？」

### ステップ5: 座右の銘を紡ぐ
- 乖離点を埋める言葉を一緒に探す
- 複数の候補を出し合う
- 最終的に1つに絞る

## 100点評価（必須）
座右の銘が出たら必ず：
1. 「この言葉は、100点満点中、何点ですか？」
2. 満点でない場合「なぜその点数なのですか？原因は？」
3. 原因を探り、言葉をブラッシュアップ
4. 100点（または限りなく近く）になるまで磨く

# 重要な姿勢
- 決して急がない。ユーザーが納得するまで対話する
- 「普通」「常識」ではなく、その人の感覚を大切にする
- 他人の名言を使わせない。本人の言葉で紡ぐ
- 抽象度が高すぎず、実際の判断に使える言葉にする

# 最後に
完成したら：
- その座右の銘に込められた意味を確認
- 「この言葉と共にどんな未来を創りたいですか？」
- お祝いの言葉を贈る"""

# APIキーの取得（Streamlit Secrets から）
try:
    API_KEY = st.secrets["ANTHROPIC_API_KEY"]
except Exception as e:
    st.error("⚠️ APIキーが設定されていません。管理者に連絡してください。")
    st.stop()

# アプリの設定（ここで変更可能）
APP_TITLE = "あなたの「座右の銘」一緒に紡ぎましょ"
APP_SUBTITLE = "あなただけの言葉で、人生の羅針盤を創ります"

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "started" not in st.session_state:
    st.session_state.started = False
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "is_complete" not in st.session_state:
    st.session_state.is_complete = False

def update_step(message):
    """メッセージ内容からステップを推測"""
    if not st.session_state.started:
        return
    
    msg_lower = message.lower()
    if "問題" in message and st.session_state.current_step < 1:
        st.session_state.current_step = 1
    elif "解決" in message and st.session_state.current_step < 2:
        st.session_state.current_step = 2
    elif "どんな人間" in message and st.session_state.current_step < 3:
        st.session_state.current_step = 3
    elif "乖離" in message and st.session_state.current_step < 4:
        st.session_state.current_step = 4
    elif "100点" in message or "何点" in message:
        st.session_state.current_step = 5
    elif "おめでとう" in message or "完成" in message:
        st.session_state.is_complete = True

def call_claude_api(messages):
    """Claude APIを呼び出す"""
    try:
        client = anthropic.Anthropic(api_key=API_KEY)
        
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            temperature=0.3,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        
        return response.content[0].text
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

def start_conversation():
    """対話を開始"""
    st.session_state.started = True
    st.session_state.current_step = 1
    
    # 直接AIの挨拶から開始（ユーザーメッセージは不要）
    assistant_response = call_claude_api([{"role": "user", "content": "対話を開始してください"}])
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    update_step(assistant_response)

# メインUI
st.markdown(f'<h1 class="main-title">{APP_TITLE}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="subtitle">{APP_SUBTITLE}</p>', unsafe_allow_html=True)

# サイドバー
with st.sidebar:
    st.header("📖 使い方")
    st.markdown("""
    1. 「対話を始める」をクリック
    2. AIの質問に答える
    3. 30分で座右の銘が完成
    
    **5つのステップ：**
    1. 問題を見つける
    2. 解決方法を考える
    3. 理想の生き方を探る
    4. 乖離を見つける
    5. 座右の銘を紡ぐ
    """)
    
    st.markdown("---")
    
    # 保存・再開機能
    if st.session_state.started and not st.session_state.is_complete:
        st.markdown("**💾 対話の保存・再開**")
        
        # 保存ボタン
        if st.session_state.messages:
            import json
            from datetime import datetime
            
            save_data = {
                "messages": st.session_state.messages,
                "current_step": st.session_state.current_step,
                "saved_at": datetime.now().isoformat()
            }
            
            json_str = json.dumps(save_data, ensure_ascii=False, indent=2)
            
            st.download_button(
                label="💾 対話を保存",
                data=json_str,
                file_name=f"motto_guide_save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # 再開ボタン
        uploaded_file = st.file_uploader(
            "📂 保存した対話を再開",
            type=['json'],
            help="以前保存した対話ファイルをアップロード"
        )
        
        if uploaded_file is not None:
            import json
            save_data = json.loads(uploaded_file.read())
            st.session_state.messages = save_data["messages"]
            st.session_state.current_step = save_data["current_step"]
            st.session_state.started = True
            st.success("✅ 対話を再開しました！")
            st.rerun()
        
        st.markdown("---")
    
    if st.button("🔄 最初から始める", use_container_width=True):
        st.session_state.messages = []
        st.session_state.started = False
        st.session_state.current_step = 0
        st.session_state.is_complete = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Hiromi式 - 座右の銘の紡ぎ方**")

# メインエリア
if not st.session_state.started:
    # 開始前
    st.markdown("""
    ### ようこそ！
    
    このアプリでは、AIとの対話を通じて、あなただけの「座右の銘」を紡いでいきます。
    
    **所要時間：** 約30分  
    **準備：** 特になし。リラックスして、正直に答えてください
    
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎋 対話を始める", use_container_width=True):
            start_conversation()
            st.rerun()

else:
    # 対話中
    
    # プログレス表示
    steps = ["開始", "問題発見", "解決方法", "理想の姿", "乖離発見", "座右の銘"]
    
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="step-label">ステップ {st.session_state.current_step} / 5: {steps[st.session_state.current_step]}</div>', unsafe_allow_html=True)
    progress = st.session_state.current_step / 5
    st.progress(progress)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # チャット履歴表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 完成メッセージ
    if st.session_state.is_complete:
        st.success("🎉 座右の銘が完成しました！おめでとうございます！")
        st.balloons()
    
    # 入力欄（対話開始後かつ完成していない場合のみ）
    if st.session_state.started and not st.session_state.is_complete:
        if prompt := st.chat_input("メッセージを入力..."):
            # ユーザーメッセージを追加
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Claude の応答を取得
            with st.chat_message("assistant"):
                with st.spinner("考えています..."):
                    response = call_claude_api(st.session_state.messages)
                    st.markdown(response)
            
            # 応答を履歴に追加
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # ステップ更新
            update_step(response)
            
            st.rerun()

# フッター
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #8a8a8a; font-size: 0.8rem;">Hiromi式 - 座右の銘の紡ぎ方</p>',
    unsafe_allow_html=True
)
