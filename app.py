import streamlit as st
import streamlit.components.v1 as components

# 1. ページの設定
st.set_page_config(
    page_title="AI Code Risk Guard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Streamlitのデフォルト余白を消去
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px; height: 100vh;}
    iframe {position: fixed; top: 0; left: 0; width: 100%; height: 100% !important; border: none;}
    </style>
    """, unsafe_allow_html=True)

# 3. ご提示いただいたHTMLコードをそのまま変数に格納
# デザイン・ロジック・RULES（API、外部通信、課金、権利、設定、ループ、環境変数、消去、eval）を完全維持
html_content = r'''
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
        body { font-family: 'Inter', sans-serif; }
        .drop-zone { border: 2px dashed #cbd5e1; transition: all 0.3s ease; border-radius: 1rem; }
        .drop-zone.dragover { border-color: #3b82f6; background: #eff6ff; }
        .editor-container { position: relative; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: #fff; }
        #codeEditor { 
            width: 100%; height: 500px; padding: 1.25rem; font-family: 'Monaco', 'Consolas', monospace; 
            font-size: 13px; line-height: 1.6; outline: none; white-space: pre; overflow: auto;
        }
        .hl-risk { background: #fee2e2; color: #b91c1c; font-weight: 800; border-bottom: 2px solid #ef4444; padding: 0 2px; }
        .status-badge { font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 4px; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <header class="mb-8 text-center">
            <h1 class="text-3xl font-bold text-slate-900 flex justify-center items-center gap-3">
                <i class="fas fa-shield-alt text-blue-600"></i> AI Code Risk Guard <span class="text-sm bg-blue-100 text-blue-600 px-2 py-1 rounded">v13</span>
            </h1>
            <p class="text-slate-500 mt-2 text-lg">全項目チェックリスト形式の診断レポート</p>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <div class="lg:col-span-7 space-y-6">
                <div id="dropZone" class="drop-zone bg-white p-6 text-center cursor-pointer hover:bg-slate-50 transition shadow-sm border border-slate-200">
                    <input type="file" id="fileInput" class="hidden" accept=".html,.js,.txt">
                    <i class="fas fa-file-code text-3xl text-slate-300 mb-2"></i>
                    <h3 class="text-md font-semibold text-slate-700">ファイルを読み込む</h3>
                </div>

                <div class="editor-container shadow-sm border border-slate-200">
                    <div class="bg-slate-800 text-slate-400 px-4 py-2 text-xs font-mono flex justify-between items-center">
                        <span>SOURCE CODE</span>
                        <button onclick="clearEditor()" class="text-[10px] hover:text-white transition">CLEAR</button>
                    </div>
                    <div id="codeEditor" contenteditable="true" spellcheck="false" placeholder="ここにコードを貼り付けてください..."></div>
                </div>
                
                <div class="space-y-4">
                    <button onclick="analyzeCode()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-5 rounded-xl transition shadow-lg flex items-center justify-center gap-3 text-xl">
                        <i class="fas fa-search"></i> リスクを診断する
                    </button>

                    <div class="grid grid-cols-2 gap-4">
                        <button onclick="copyAIPrompt()" id="aiBtn" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl transition shadow-md flex items-center justify-center gap-2 opacity-50 cursor-not-allowed" disabled>
                            <i class="fas fa-magic"></i> AI修正用プロンプトをコピー
                        </button>
                        <button onclick="copySanitizedCode()" id="copyBtn" class="bg-slate-600 hover:bg-slate-700 text-white font-bold py-4 rounded-xl transition shadow-md flex items-center justify-center gap-2 opacity-50 cursor-not-allowed" disabled>
                            <i class="fas fa-ban"></i> 指記箇所を無効化してコピー
                        </button>
                    </div>
                </div>
            </div>

            <div class="lg:col-span-5">
                <div class="bg-white rounded-xl shadow-sm border border-slate-200 sticky top-8 overflow-hidden">
                    <div class="bg-slate-900 text-white px-6 py-4 flex justify-between items-center border-b border-slate-700">
                        <h2 class="font-bold flex items-center gap-2 text-sm">
                            <i class="fas fa-list-check text-blue-400"></i> 診断チェックリスト
                        </h2>
                        <span id="riskCount" class="text-[10px] px-2 py-1 rounded font-bold bg-slate-700 tracking-widest uppercase">READY</span>
                    </div>
                    <div id="results" class="divide-y divide-slate-100 max-h-[700px] overflow-y-auto">
                        <div class="p-12 text-center text-slate-400 italic">
                            コードを貼り付けて診断を開始してください。
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const editor = document.getElementById('codeEditor');
        const resultsDiv = document.getElementById('results');
        const riskCountBadge = document.getElementById('riskCount');
        const aiBtn = document.getElementById('aiBtn');
        const copyBtn = document.getElementById('copyBtn');
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        let lastPureCode = "";
        let currentFindings = [];

        dropZone.onclick = () => fileInput.click();
        fileInput.onchange = (e) => handleFiles(e.target.files);
        dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('dragover'); };
        dropZone.ondragleave = () => dropZone.classList.remove('dragover');
        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        };

        function handleFiles(files) {
            if (files.length === 0) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                editor.innerText = e.target.result;
                analyzeCode();
            };
            reader.readAsText(files[0]);
        }

        const RULES = [
            { id: 'api', label: 'APIキーの直書き', level: 'danger', regex: /(sk-[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9_-]{35})/g, advice: 'APIキーが露出しています。環境変数への移行が必要です。', comment: '/* [DISABLED:API_KEY] ' },
            { id: 'network', label: '外部通信・漏洩', level: 'warn', regex: /(fetch\(|XMLHttpRequest|axios\.|(?:\$|jQuery)\.ajax)/g, advice: '外部へのデータ送信が行われます。送信先を確認してください。', comment: '/* [CHECK:NETWORK] ' },
            { id: 'billing', label: '課金発生リスク', level: 'warn', regex: /(stripe|paypal|charge|payment|checkout)/gi, advice: '決済に関連する処理が含まれています。', comment: '/* [CHECK:BILLING] ' },
            { id: 'copyright', label: '権利侵害リスク', level: 'warn', regex: /(iframe|copyright|license)/gi, advice: '外部コンテンツの埋め込みや権利表記を確認してください。', comment: '/* [CHECK:RIGHTS] ' },
            { id: 'config', label: '環境設定変更', level: 'warn', regex: /(Object\.defineProperty|setAttribute\(['"]id|document\.title)/g, advice: '環境やDOMの基本設定を変更する処理です。', comment: '/* [CHECK:CONFIG] ' },
            { id: 'loop', label: '無限ループ', level: 'danger', regex: /while\s*\(\s*(true|1)\s*\)/g, advice: 'ブラウザがフリーズする恐れがあります。', comment: '/* [DISABLED:LOOP] ' },
            { id: 'env', label: '環境変数', level: 'warn', regex: /process\.env|dotenv/g, advice: '環境変数の参照を検知。実行環境での設定が必要です。', comment: '/* [CHECK:ENV] ' },
            { id: 'delete', label: 'ファイル・フォルダ消去', level: 'danger', regex: /\.(unlink|rmdir|remove|deleteFile)\(/g, advice: '破壊的なファイル操作命令が含まれています。', comment: '/* [DISABLED:DELETE] ' },
            { id: 'eval', label: '危険な実行(eval)', level: 'danger', regex: /eval\(|new Function\(/g, advice: 'セキュリティ上の脆弱性となります。', comment: '/* [DISABLED:EVAL] ' }
        ];

        function analyzeCode() {
            let code = editor.innerText;
            if (!code.trim()) return;
            lastPureCode = code;
            currentFindings = [];

            let findingsHtml = '';
            let totalRisks = 0;
            let highlightedCode = escapeHtml(code);

            RULES.forEach(rule => {
                const matches = code.match(rule.regex);
                const isFound = matches && matches.length > 0;
                
                if (isFound) {
                    totalRisks += matches.length;
                    currentFindings.push(`${rule.label}: ${rule.advice}`);
                    highlightedCode = highlightedCode.replace(rule.regex, (match) => `<span class="hl-risk">${match}</span>`);
                }

                findingsHtml += `
                    <div class="p-4 ${isFound ? 'bg-orange-50' : 'bg-white'} border-b border-slate-100">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-xs font-bold ${isFound ? 'text-slate-900' : 'text-slate-400'}">
                                <i class="fas fa-circle text-[6px] mr-2 align-middle ${isFound ? (rule.level === 'danger' ? 'text-red-500' : 'text-amber-500') : 'text-slate-200'}"></i>
                                ${rule.label}
                            </span>
                            ${isFound ? 
                                `<span class="bg-red-100 text-red-700 text-[10px] px-2 py-0.5 rounded font-bold">${matches.length}件のリスク</span>` : 
                                `<span class="bg-emerald-50 text-emerald-600 text-[10px] px-2 py-0.5 rounded font-bold tracking-tighter">SAFE</span>`
                            }
                        </div>
                        ${isFound ? `<p class="text-[11px] text-slate-600 leading-relaxed mt-1"><strong>指摘：</strong>${rule.advice}</p>` : ''}
                    </div>
                `;
            });

            editor.innerHTML = highlightedCode;
            resultsDiv.innerHTML = findingsHtml;
            riskCountBadge.textContent = totalRisks > 0 ? `${totalRisks} RISKS FOUND` : 'ALL CLEAR';
            riskCountBadge.className = totalRisks > 0 ? 'bg-red-600 text-[10px] px-2 py-1 rounded text-white font-bold' : 'bg-emerald-600 text-[10px] px-2 py-1 rounded text-white font-bold';
            
            [aiBtn, copyBtn].forEach(btn => {
                btn.disabled = false;
                btn.classList.remove('opacity-50', 'cursor-not-allowed');
            });
        }

        function copyAIPrompt() {
            const riskList = currentFindings.length > 0 ? currentFindings.map(f => `・${f}`).join('\n') : '特になし（全体的なブラッシュアップ）';
            const prompt = `以下のHTML/JavaScriptコードについて、セキュリティ診断を行ったところ、いくつかのリスクが検出されました。
機能を維持したまま、これらを解消した「修正済みの完成コード」を1ファイルのHTML形式で作成してください。

【検出されたリスク】
${riskList}

【修正の条件】
1. APIキーなどの機密情報は、コードに直書きせず、冒頭の設定エリアに切り出してください。
2. 無限ループやファイル消去などの破壊的な操作は、安全な代替処理に変更してください。
3. 修正した箇所と、その理由を初心者にもわかりやすく解説してください。

【対象のソースコード】
${lastPureCode}`;

            navigator.clipboard.writeText(prompt).then(() => {
                const icon = aiBtn.innerHTML;
                aiBtn.innerHTML = '<i class="fas fa-check"></i> プロンプトをコピーしました！';
                setTimeout(() => { aiBtn.innerHTML = icon; }, 3000);
            });
        }

        function copySanitizedCode() {
            let sanitized = lastPureCode;
            RULES.forEach(rule => { sanitized = sanitized.replace(rule.regex, (match) => `${rule.comment}${match} */`); });
            navigator.clipboard.writeText(sanitized).then(() => {
                const icon = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i> 無効化してコピーしました';
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
            [aiBtn, copyBtn].forEach(btn => { btn.disabled = true; btn.classList.add('opacity-50', 'cursor-not-allowed'); });
        }
    </script>
</body>
</html>
'''

# 4. コンポーネントで表示（全画面表示）
components.html(html_content, height=1000, scrolling=True)
