import re

with open("templates/index.html", "r") as f:
    html = f.read()

# 1. Add CSS for collapsing
css_inject = """
        /* Collapsible Cards & Toolbar */
        .card-header {
            display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; cursor: pointer;
        }
        .card-header .card-title { margin-bottom: 0; }
        .collapse-icon { font-size: 0.8rem; color: var(--text-muted); transition: transform 0.3s; }
        .card.collapsed .collapse-icon { transform: rotate(-90deg); }
        .card.collapsed > :not(.card-header) { display: none !important; }
        
        .toolbar-wrapper {
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            display: flex; flex-direction: column; align-items: center; z-index: 10;
        }
        .toolbar-toggle {
            background: rgba(255,255,255,0.1); border: 1px solid var(--glass-border); border-radius: 20px;
            color: #fff; padding: 4px 16px; font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase;
            cursor: pointer; margin-bottom: 8px; backdrop-filter: blur(10px); transition: all 0.3s;
        }
        .toolbar-toggle:hover { background: rgba(255,255,255,0.2); }
        .toolbar { position: relative; bottom: 0; left: 0; transform: none; transition: all 0.3s ease; }
        .toolbar.collapsed { opacity: 0; transform: translateY(20px); pointer-events: none; }
"""
html = html.replace("/* Dashboard Stats */", css_inject + "\n        /* Dashboard Stats */")

# 2. Update Toolbar
toolbar_html = """
            <div class="toolbar-wrapper">
                <button class="toolbar-toggle" onclick="document.getElementById('main-toolbar').classList.toggle('collapsed')">Toggle Controls</button>
                <div class="toolbar" id="main-toolbar">
                    <button class="tool-btn" id="ai-vision-btn" onclick="toggleDebug()" title="AI Vision Mode">🤖</button>
                    <button class="tool-btn" onclick="zoomIn()" title="Zoom In">➕</button>
                    <button class="tool-btn" onclick="zoomOut()" title="Zoom Out">➖</button>
                    <button class="tool-btn" onclick="resetZoom()" title="Reset Zoom">🔄</button>
                    <button class="tool-btn" onclick="saveSnapshot()" title="Save Snapshot">💾</button>
                    <button class="tool-btn" onclick="document.getElementById('settings-modal').classList.add('visible')" title="Settings"><i class="fas fa-cog">⚙️</i></button>
                    <button class="tool-btn" style="color: #ff4444;" onclick="endDrive()" title="End Drive">🛑</button>
                </div>
            </div>
"""
# Need to replace the existing toolbar
html = re.sub(r'<div class="toolbar">.*?</div>', toolbar_html, html, flags=re.DOTALL)

# 3. Update Cards to have Card Headers
def replace_card_title(match):
    title = match.group(1)
    return f"""<div class="card-header" onclick="this.parentElement.classList.toggle('collapsed')">
                    <div class="card-title">{title}</div>
                    <div class="collapse-icon">▼</div>
                </div>"""

html = re.sub(r'<div class="card-title">(.*?)</div>', replace_card_title, html)

with open("templates/index.html", "w") as f:
    f.write(html)
