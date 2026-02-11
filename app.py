import streamlit as st
import streamlit.components.v1 as components

# 1. ページの設定（タブ名やレイアウト）
st.set_page_config(
    page_title="AI Code Risk Guard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 余白を消して画面いっぱいに表示する設定
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px; height: 100vh;}
    iframe {position: fixed; top: 0; left: 0; width: 100%; height: 100% !important; border: none;}
    </style>
    """, unsafe_allow_html=True)

# 3. Code Checker (v13) のHTMLコードをそのまま移植
# 添付の code_Checker.html の内容を反映
html_code = r'''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Code Risk Guard | v13</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .drop-zone { border: 2px dashed #cbd5e1; transition: all 0.3s ease; border-radius: 1rem; }
        .drop-zone.dragover { border-color: #3b82f6; background: #eff6ff; }
        .editor-container { position: relative; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: #fff; }
        #codeEditor { 
            width: 100%; height: 500px; padding: 1.25rem; font-family: 'Monaco', 'Consolas', monospace; 
            font-size: 13px; line-height: 1.6; outline: none; white-space: pre; overflow: auto;
        }
        .hl-risk { background: rgba(239, 68, 68, 0.15); border-bottom: 2px solid #ef4444; font-weight: bold; }
        .risk-item { animation: slideIn 0.3s ease-out; }
        @keyframes slideIn { from { opacity: 0; transform: translateX(10px); } to { opacity: 1; transform: translateX(0); } }
    </style>
</head>
<body class="p-4 md:p-8">

    <div class="max-w-7xl mx-auto">
        <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
            <div>
                <h1 class="text-3xl font-bold text-slate-900 flex items-center gap-3">
                    <i class="fas fa-shield-virus text-blue-600"></i>
                    AI Code Risk Guard <span class="text-sm font-normal bg-slate-200 px-2 py-1 rounded text-slate-600">v13</span>
                </h1>
                <p class="text-slate-500 mt-1">AIにコードを渡す前に、機密情報や破壊的コマンドを自動検知して無効化します。</p>
            </div>
            <div class="flex items-center gap-3">
                <div id="riskCountBadge" class="px-4 py-2 rounded-full bg-slate-800 text-white font-bold text-sm">READY</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div class="lg:col-span-7 flex flex-col gap-4">
                <div id="dropZone" class="drop-zone p-8 text-center bg-white cursor-pointer hover:bg-slate-50">
                    <i class="fas fa-cloud-upload-alt text-4xl text-slate-300 mb-3"></i>
                    <p class="text-slate-600">ファイルをドラッグ＆ドロップ、または <span class="text-blue-600 font-semibold">ブラウズ</span></p>
                    <p class="text-xs text-slate-400 mt-1">.py, .js, .html, .txt などに対応</p>
                    <input type="file" id="fileInput" class="hidden">
                </div>

                <div class="editor-container shadow-sm">
                    <div class="bg-slate-50 border-bottom px-4 py-2 flex justify-between items-center text-xs font-semibold text-slate-500">
                        <span>SOURCE CODE EDITOR</span>
                        <button onclick="clearEditor()" class="text-slate-400 hover:text-red-500 transition-colors">
                            <i class="fas fa-trash-alt"></i> クリア
                        </button>
                    </div>
                    <div id="codeEditor" contenteditable="true" spellcheck="false" placeholder="ここにコードを貼り付けてください..."></div>
                </div>

                <div class="flex gap-3">
                    <button onclick="runAnalysis()" class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-blue-200 transition-all flex items-center justify-center gap-2">
                        <i class="fas fa-search text-lg"></i> 診断実行
                    </button>
                </div>
            </div>

            <div class="lg:col-span-5 flex flex-col gap-4">
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-full">
                    <div class="bg-slate-900 px-6 py-4 flex justify-between items-center">
                        <h2 class="text-white font-bold flex items-center gap-2">
                            <i class="fas fa-clipboard-list text-blue-400"></i>
                            検出されたリスク
                        </h2>
                    </div>
                    
                    <div id="resultsDiv" class="p-6 overflow-y-auto flex-1 max-h-[600px]">
                        <p class="text-center text-slate-400 italic py-10">診断を開始してください。</p>
                    </div>

                    <div id="actionPanel" class="p-4 bg-slate-50 border-t border-slate-200 hidden">
                        <div class="flex flex-col gap-2">
                            <button id="copyPromptBtn" onclick="copyAIPrompt()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all">
                                <i class="fas fa-robot"></i> AI指示用プロンプトをコピー
                            </button>
                            <button id="copySanitizedBtn" onclick="copySanitizedCode()" class="w-full bg-slate-700 hover:bg-slate-800 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-all text-sm">
                                <i class="fas fa-copy"></i> 安全に加工してコードをコピー
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const editor = document.getElementById('codeEditor');
        const resultsDiv = document.getElementById('resultsDiv');
        const riskCountBadge = document.getElementById('riskCountBadge');
        const actionPanel = document.getElementById('actionPanel');
        const aiBtn = document.getElementById('copyPromptBtn');
        const copyBtn = document.getElementById('copySanitizedBtn');

        // リスク定義
        const RULES = [
            { id: 'env', name: '機密情報 (API KEY/ENV)', regex: /(AIza[0-9A-Za-z-_]{35}|sk-[a-zA-Z0-9]{48}|(?<=PASSWORD\s*[:=]\s*['"])[^'"]+|(?<=SECRET\s*[:=]\s*['"])[^'"]+)/gi, comment: '/* [CONFIDENTIAL REMOVED] ', level: 'CRITICAL', advice: 'APIキーやパスワードが露出しています。環境変数を使用してください。' },
            { id: 'destruct', name: '破壊的コマンド', regex: /(rm\s+-rf\s+\/|DROP\s+TABLE|os\.remove|shutil\.rmtree)/gi, comment: '/* [DESTRUCTIVE COMMAND DISABLED] ', level: 'CRITICAL', advice: 'システムを破壊する恐れのあるコマンドです。実行前に再確認してください。' },
            { id: 'path', name: '絶対パスの露出', regex: /(\/[a-z0-9_-]+\/[a-z0-9_-]+\/[a-z0-9_-]+|C:\\[\w\\]+)/gi, comment: '/* [PATH ANONYMIZED] ', level: 'WARNING', advice: 'ローカルのディレクトリ構造がわかると攻撃のヒントになります。相対パスを推奨。' },
            { id: 'ip', name: 'IPアドレス', regex: /\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/g, comment: '/* [IP ANONYMIZED] ', level: 'WARNING', advice: 'サーバーの場所を特定されるリスクがあります。' }
        ];

        let lastPureCode = "";

        function runAnalysis() {
            const code = editor.innerText;
            lastPureCode = code;
            let highlightedCode = escapeHtml(code);
            let findings = [];

            RULES.forEach(rule => {
                const matches = code.match(rule.regex);
                if (matches) {
                    matches.forEach(m => {
                        findings.push({ ...rule, match: m });
                        highlightedCode = highlightedCode.split(m).join(`<span class="hl-risk">${m}</span>`);
                    });
                }
            });

            editor.innerHTML = highlightedCode;
            renderResults(findings);
        }

        function renderResults(findings) {
            if (findings.length === 0) {
                resultsDiv.innerHTML = '<div class="text-center py-10 text-emerald-500 font-bold"><i class="fas fa-check-circle text-4xl mb-2"></i><p>リスクは見つかりませんでした！</p></div>';
                riskCountBadge.textContent = 'SECURE';
                riskCountBadge.className = 'px-4 py-2 rounded-full bg-emerald-500 text-white font-bold text-sm';
                actionPanel.classList.add('hidden');
                return;
            }

            riskCountBadge.textContent = `${findings.length} RISKS FOUND`;
            riskCountBadge.className = 'px-4 py-2 rounded-full bg-red-600 text-white font-bold text-sm';
            actionPanel.classList.remove('hidden');

            resultsDiv.innerHTML = findings.map(f => `
                <div class="risk-item mb-4 p-4 rounded-xl border-l-4 ${f.level === 'CRITICAL' ? 'border-red-500 bg-red-50' : 'border-amber-500 bg-amber-50'}">
                    <div class="flex justify-between items-start mb-2">
                        <span class="text-xs font-black uppercase tracking-wider ${f.level === 'CRITICAL' ? 'text-red-600' : 'text-amber-600'}">${f.level}</span>
                        <span class="text-[10px] bg-white px-2 py-1 rounded border border-slate-200 text-slate-400 font-mono">${f.id}</span>
                    </div>
                    <h3 class="font-bold text-slate-800 text-sm mb-1">${f.name}</h3>
                    <code class="block bg-white p-2 rounded border border-slate-200 text-xs text-red-500 mb-2 truncate">${f.match}</code>
                    <p class="text-xs text-slate-600 leading-relaxed"><i class="fas fa-lightbulb text-amber-500"></i> ${f.advice}</p>
                </div>
            `).join('');
        }

        function copyAIPrompt() {
            const prompt = `以下のソースコードの「セキュリティ上の問題点」を修正し、「より安全で効率的なコード」に書き換えてください。
【修正の要件】
1. APIキーなどの機密情報は、コードに直書きせず、冒頭の設定エリアに切り出してください。
2. 無限ループやファイル消去などの破壊的な操作は、安全な代替処理に変更してください。
3. 修正した箇所と、その理由を初心者にもわかりやすく解説してください。

【対象のソースコード】
${lastPureCode}`;

            navigator.clipboard.writeText(prompt).then(() => {
                const icon = aiBtn.innerHTML;
                aiBtn.innerHTML = '<i class="fas fa-check"></i> コピーしました！';
                setTimeout(() => { aiBtn.innerHTML = icon; }, 3000);
            });
        }

        function copySanitizedCode() {
            let sanitized = lastPureCode;
            RULES.forEach(rule => { sanitized = sanitized.replace(rule.regex, (match) => `${rule.comment}${match} */`); });
            navigator.clipboard.writeText(sanitized).then(() => {
                const icon = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i> 安全にコピーしました';
                setTimeout(() => { copyBtn.innerHTML = icon; }, 2000);
            });
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function clearEditor() {
            editor.innerText = '';
            resultsDiv.innerHTML = '<p class="text-center text-slate-400 italic py-10">診断を開始してください。</p>';
            riskCountBadge.textContent = 'READY';
            riskCountBadge.className = 'px-4 py-2 rounded-full bg-slate-800 text-white font-bold text-sm';
            actionPanel.classList.add('hidden');
        }

        // ドラッグ＆ドロップ
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        dropZone.onclick = () => fileInput.click();
        fileInput.onchange = (e) => handleFile(e.target.files[0]);
        dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('dragover'); };
        dropZone.ondragleave = () => dropZone.classList.remove('dragover');
        dropZone.ondrop = (e) => { e.preventDefault(); dropZone.classList.remove('dragover'); handleFile(e.dataTransfer.files[0]); };

        function handleFile(file) {
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => { editor.innerText = e.target.result; runAnalysis(); };
            reader.readAsText(file);
        }
    </script>
</body>
</html>
'''

# 4. コンポーネントを表示
components.html(html_code)
