import streamlit as st
import streamlit.components.v1 as components

# 1. ページの設定
st.set_page_config(
    page_title="AI Code Risk Guard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 余白を消して画面いっぱいに表示
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px; height: 100vh;}
    iframe {position: fixed; top: 0; left: 0; width: 100%; height: 100% !important; border: none;}
    </style>
    """, unsafe_allow_html=True)

# 3. HTMLコード (HTML版の全リスクカテゴリ・チェック機能を完全移植)
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
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; overflow: hidden; height: 100vh; }
        .editor-container { position: relative; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: #fff; }
        #codeEditor { 
            width: 100%; height: calc(100vh - 350px); padding: 1.25rem; font-family: 'Monaco', 'Consolas', monospace; 
            font-size: 13px; line-height: 1.6; outline: none; white-space: pre; overflow: auto;
        }
        .hl-risk { background: rgba(239, 68, 68, 0.2); border-bottom: 2px solid #ef4444; font-weight: bold; }
        .status-badge { transition: all 0.3s ease; }
        /* スクロールバー装飾 */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
    </style>
</head>
<body class="p-4">

    <div class="max-w-[1600px] mx-auto h-full flex flex-col">
        <div class="flex items-center justify-between mb-4 flex-shrink-0">
            <div>
                <h1 class="text-2xl font-bold text-slate-900 flex items-center gap-2">
                    <i class="fas fa-shield-halved text-blue-600"></i>
                    AI Code Risk Guard <span class="text-xs font-normal bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">v13 PRO</span>
                </h1>
            </div>
            <div id="riskCountBadge" class="px-4 py-1.5 rounded-full bg-slate-800 text-white font-bold text-xs">STANDBY</div>
        </div>

        <div class="grid grid-cols-12 gap-6 flex-1 overflow-hidden">
            <div class="col-span-7 flex flex-col gap-4 h-full">
                <div class="editor-container shadow-sm flex-1 flex flex-col">
                    <div class="bg-slate-50 border-b px-4 py-2 flex justify-between items-center text-[10px] font-bold text-slate-400 tracking-widest">
                        <span>SOURCE CODE</span>
                        <div class="flex gap-4">
                             <button onclick="document.getElementById('fileInput').click()" class="hover:text-blue-600"><i class="fas fa-file-upload"></i> 読み込み</button>
                             <button onclick="clearEditor()" class="hover:text-red-500"><i class="fas fa-trash-alt"></i> クリア</button>
                        </div>
                    </div>
                    <div id="codeEditor" contenteditable="true" spellcheck="false"></div>
                    <input type="file" id="fileInput" class="hidden">
                </div>
                
                <button onclick="runAnalysis()" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg flex items-center justify-center gap-2 flex-shrink-0">
                    <i class="fas fa-sync-alt"></i> リスクスキャンを実行
                </button>
            </div>

            <div class="col-span-5 flex flex-col gap-4 h-full overflow-hidden">
                <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-4 flex-shrink-0">
                    <h3 class="text-xs font-bold text-slate-500 mb-3 tracking-tighter uppercase">Risk Category Checklist</h3>
                    <div id="checklist" class="grid grid-cols-2 gap-2 text-[11px]">
                        </div>
                </div>

                <div class="bg-slate-900 rounded-xl shadow-inner flex-1 flex flex-col overflow-hidden">
                    <div class="px-4 py-2 border-b border-slate-800 flex justify-between items-center">
                        <span class="text-[10px] text-slate-500 font-bold">DETECTION LOGS</span>
                        <span id="logCount" class="text-blue-400 text-[10px]">0 issues</span>
                    </div>
                    <div id="resultsDiv" class="p-4 overflow-y-auto flex-1 space-y-3">
                        <p class="text-slate-600 text-xs italic text-center mt-10">コードを入力してスキャンを開始してください</p>
                    </div>
                    
                    <div id="actionPanel" class="p-3 bg-slate-800 hidden">
                         <button onclick="copyAIPrompt()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold py-3 rounded-lg flex items-center justify-center gap-2">
                            <i class="fas fa-robot"></i> AI指示用プロンプトを生成
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const editor = document.getElementById('codeEditor');
        const resultsDiv = document.getElementById('resultsDiv');
        const checklistDiv = document.getElementById('checklist');
        
        // HTML版の全リスクカテゴリ定義
        const CATEGORIES = [
            { id: 'env', name: 'APIキー/機密情報', icon: 'fa-key', regex: /(AIza[0-9A-Za-z-_]{35}|sk-[a-zA-Z0-9]{48}|password\s*[:=]|secret\s*[:=])/gi, msg: 'APIキーやパスワードのハードコーディング', advice: '環境変数(dotenv)を使用してください。' },
            { id: 'comm', name: '外部通信/漏洩', icon: 'fa-network-wired', regex: /(requests\.|fetch\(|axios\.|socket|http:\/\/)/gi, msg: '外部サーバーへのデータ送信', advice: '送信先URLが意図したものか確認してください。' },
            { id: 'billing', name: '課金発生リスク', icon: 'fa-credit-card', regex: /(gpt-4|claude-3|billing|payment|subscription)/gi, msg: '高額なAPI利用料の発生', advice: 'ループ内での呼び出しやリトライ設定に注意。' },
            { id: 'rights', name: '権利侵害', icon: 'fa-copyright', regex: /(copyright|license|pirated|unauthorized)/gi, msg: '著作権・ライセンス違反の懸念', advice: 'OSSライセンスの表記義務を確認してください。' },
            { id: 'config', name: '環境設定変更', icon: 'fa-sliders', regex: /(sys\.path|os\.environ|chmod|chown)/gi, msg: 'システム設定の意図しない変更', advice: '実行環境の権限設定に影響します。' },
            { id: 'loop', name: '無限ループ', icon: 'fa-infinity', regex: /(while\s+True|for\s+.*in\s+repeat)/gi, msg: 'リソースの枯渇・ハングアップ', advice: '必ず脱出条件(break)を設定してください。' },
            { id: 'delete', name: 'ファイル消去', icon: 'fa-eraser', regex: /(rm\s+-rf|os\.remove|shutil\.rmtree|DROP\s+TABLE)/gi, msg: 'データの永久的な削除', advice: '削除前に確認ダイアログやバックアップが必要です。' },
            { id: 'path', name: '絶対パス/環境露出', icon: 'fa-folder-open', regex: /(\/[a-z0-9_-]+\/[a-z0-9_-]+|C:\\[\w\\]+)/gi, msg: 'サーバー構造の露出', advice: '相対パスを使用してください。' }
        ];

        // 初期状態でチェックリストを生成
        function initChecklist() {
            checklistDiv.innerHTML = CATEGORIES.map(c => `
                <div id="check-${c.id}" class="flex items-center gap-2 p-2 rounded bg-slate-50 text-slate-400 border border-transparent">
                    <i class="fas ${c.icon} w-4 text-center"></i>
                    <span class="flex-1 font-medium">${c.name}</span>
                    <i class="fas fa-minus-circle opacity-30"></i>
                </div>
            `).join('');
        }
        initChecklist();

        function runAnalysis() {
            const code = editor.innerText;
            if(!code.trim()) return;
            
            let findings = [];
            let highlightedCode = escapeHtml(code);

            // スキャンのリセット
            initChecklist();

            CATEGORIES.forEach(cat => {
                const matches = code.match(cat.regex);
                const badge = document.getElementById(`check-${cat.id}`);
                
                if (matches) {
                    badge.classList.remove('bg-slate-50', 'text-slate-400');
                    badge.classList.add('bg-red-50', 'text-red-600', 'border-red-100');
                    badge.querySelector('.fa-minus-circle').className = 'fas fa-exclamation-triangle';
                    
                    matches.forEach(m => {
                        findings.push({ ...cat, match: m });
                        highlightedCode = highlightedCode.split(m).join(`<span class="hl-risk">${m}</span>`);
                    });
                } else {
                    badge.classList.remove('text-slate-400');
                    badge.classList.add('bg-emerald-50', 'text-emerald-600', 'border-emerald-100');
                    badge.querySelector('.fa-minus-circle').className = 'fas fa-check-circle';
                }
            });

            editor.innerHTML = highlightedCode;
            renderLogs(findings);
        }

        function renderLogs(findings) {
            const badge = document.getElementById('riskCountBadge');
            const logCount = document.getElementById('logCount');
            const actionPanel = document.getElementById('actionPanel');

            if (findings.length === 0) {
                resultsDiv.innerHTML = '<div class="text-center py-10"><i class="fas fa-shield-check text-emerald-500 text-3xl mb-2"></i><p class="text-emerald-400 text-xs">リスクは見つかりませんでした</p></div>';
                badge.className = 'px-4 py-1.5 rounded-full bg-emerald-600 text-white font-bold text-xs';
                badge.textContent = 'SECURE';
                logCount.textContent = '0 issues';
                actionPanel.classList.add('hidden');
                return;
            }

            badge.className = 'px-4 py-1.5 rounded-full bg-red-600 text-white font-bold text-xs';
            badge.textContent = `${findings.length} RISKS`;
            logCount.textContent = `${findings.length} issues detected`;
            actionPanel.classList.remove('hidden');

            resultsDiv.innerHTML = findings.map(f => `
                <div class="bg-slate-800 p-3 rounded-lg border-l-2 border-red-500">
                    <div class="flex justify-between items-start mb-1">
                        <span class="text-[9px] font-bold text-red-400 uppercase tracking-tighter">${f.name}</span>
                    </div>
                    <div class="text-slate-200 text-xs font-bold mb-1">${f.msg}</div>
                    <code class="block text-[10px] text-red-300 bg-red-900/30 p-1 rounded truncate mb-2">${f.match}</code>
                    <p class="text-[10px] text-slate-400 leading-tight"><i class="fas fa-info-circle"></i> ${f.advice}</p>
                </div>
            `).join('');
        }

        function copyAIPrompt() {
            const prompt = `以下のソースコードをレビューし、セキュリティリスクを排除した修正版を作成してください。特にAPIキーの秘匿化、例外処理の追加、リソース消費の最適化を重点的に行ってください。\n\n【対象コード】\n${editor.innerText}`;
            navigator.clipboard.writeText(prompt);
            alert("AI指示用プロンプトをコピーしました。ChatGPTやClaudeに貼り付けてください。");
        }

        function clearEditor() {
            editor.innerText = '';
            initChecklist();
            resultsDiv.innerHTML = '<p class="text-slate-600 text-xs italic text-center mt-10">コードを入力してスキャンを開始してください</p>';
            document.getElementById('riskCountBadge').textContent = 'STANDBY';
            document.getElementById('riskCountBadge').className = 'px-4 py-1.5 rounded-full bg-slate-800 text-white font-bold text-xs';
            document.getElementById('actionPanel').classList.add('hidden');
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        document.getElementById('fileInput').onchange = (e) => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (e) => { editor.innerText = e.target.result; runAnalysis(); };
            reader.readAsText(file);
        };
    </script>
</body>
</html>
'''

# 4. 表示
components.html(html_code)
