import re

with open('templates/index.html', 'r') as f:
    html = f.read()

# 1. Add Chart.js to head
head_inject = """
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-color: #0f172a;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.5);
            --danger: #ef4444;
            --danger-glow: rgba(239, 68, 68, 0.5);
            --glass-bg: rgba(30, 41, 59, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
        }
        body.theme-night {
            --bg-color: #0a0000;
            --text-main: #ff4444;
            --text-muted: #882222;
            --accent: #ff0000;
            --accent-glow: rgba(255, 0, 0, 0.5);
            --glass-bg: rgba(20, 0, 0, 0.8);
            --glass-border: rgba(255, 0, 0, 0.2);
        }
        body.theme-day {
            --bg-color: #f1f5f9;
            --text-main: #0f172a;
            --text-muted: #475569;
            --accent: #2563eb;
            --accent-glow: rgba(37, 99, 235, 0.5);
            --glass-bg: rgba(255, 255, 255, 0.9);
            --glass-border: rgba(0, 0, 0, 0.1);
            --danger: #dc2626;
            --danger-glow: rgba(220, 38, 38, 0.5);
        }
        
        body { background-color: var(--bg-color); color: var(--text-main); transition: background-color 0.5s ease, color 0.5s ease; }
        .glass-panel, .card, .toolbar { background: var(--glass-bg) !important; border-color: var(--glass-border) !important; transition: all 0.5s ease; }
        .card-title, .stat-label { color: var(--text-muted) !important; }
        
        /* Particle Canvas */
        #particles-canvas {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none;
        }
        
        /* 3D Button */
        .btn-3d {
            transition: transform 0.1s ease-out;
            transform-style: preserve-3d;
        }
        
        /* Draggable Cards */
        .card { cursor: grab; }
        .card:active { cursor: grabbing; }
        .card.dragging { opacity: 0.5; transform: scale(0.95); }
        
        /* Settings Modal */
        #settings-modal {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) scale(0.9);
            background: var(--glass-bg); backdrop-filter: blur(20px); border: 1px solid var(--glass-border);
            padding: 30px; border-radius: 20px; z-index: 200; width: 400px; max-width: 90%;
            opacity: 0; visibility: hidden; transition: all 0.3s ease;
        }
        #settings-modal.visible { opacity: 1; visibility: visible; transform: translate(-50%, -50%) scale(1); }
        .settings-input { width: 100%; padding: 10px; margin-top: 5px; margin-bottom: 15px; border-radius: 8px; border: 1px solid var(--glass-border); background: rgba(0,0,0,0.2); color: var(--text-main); }
        
        /* Chart Containers */
        .chart-container { width: 100%; height: 120px; margin-top: 10px; }
"""

html = html.replace('    <style>', head_inject + '\n    <style>')

# 2. Add Settings Button to Toolbar
toolbar_inject = """
            <button class="tool-btn" onclick="zoomOut()" title="Zoom Out"><i class="fas fa-search-minus"></i></button>
            <button class="tool-btn" onclick="document.getElementById('settings-modal').classList.add('visible')" title="Settings"><i class="fas fa-cog"></i></button>
"""
html = html.replace('<button class="tool-btn" onclick="zoomOut()" title="Zoom Out"><i class="fas fa-search-minus"></i></button>', toolbar_inject)


# 3. Add Settings Modal HTML and Particles to Landing Page
landing_page_replacement = """
    <!-- Particle Background -->
    <canvas id="particles-canvas"></canvas>
    
    <!-- Settings Modal -->
    <div id="settings-modal">
        <h2 style="margin-bottom: 20px; border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">System Settings</h2>
        
        <label>UI Theme</label>
        <select id="theme-select" class="settings-input" onchange="changeTheme()">
            <option value="glass">Glassmorphism (Default)</option>
            <option value="night">Night Drive (Red/Black)</option>
            <option value="day">Day Drive (High Contrast)</option>
        </select>
        
        <label>Smart Cabin IoT Webhook URL</label>
        <input type="text" id="iot-url" class="settings-input" value="http://127.0.0.1:5000/api/smart_car">
        
        <div style="display: flex; gap: 10px; margin-top: 20px;">
            <button class="btn btn-primary" onclick="saveSettings()" style="flex: 1;">Save & Apply</button>
            <button class="btn btn-secondary" onclick="document.getElementById('settings-modal').classList.remove('visible')" style="flex: 1; background: transparent; border: 1px solid var(--glass-border); color: var(--text-main);">Cancel</button>
        </div>
    </div>

    <!-- Landing Page -->
    <div class="landing-page" id="landing-page" style="z-index: 10;">
"""
html = html.replace('    <!-- Landing Page -->\n    <div class="landing-page" id="landing-page">', landing_page_replacement)

# Make init button 3d
html = html.replace('<button class="btn btn-primary" onclick="initializeSystem()">', '<button class="btn btn-primary btn-3d" id="init-btn" onclick="initializeSystem()">')

# 4. Add Charts and Draggability to Dashboard Cards
dashboard_replacement = """
            <div class="dashboard" id="dashboard-container">
                <div class="card" draggable="true">
                    <div class="card-title">Drowsiness Score</div>
                    <div class="score-value" id="score-val">0</div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" id="score-bar"></div>
                    </div>
                    <div class="chart-container"><canvas id="scoreChart"></canvas></div>
                </div>

                <div class="card" draggable="true">
                    <div class="card-title">Driver Heart Rate</div>
                    <div class="score-value" id="bpm-val" style="color: #ef4444; display: flex; align-items: center; gap: 10px;">
                        0 <span style="font-size: 1rem; color: #ffcccc;">BPM</span>
                    </div>
                    <div class="chart-container"><canvas id="bpmChart"></canvas></div>
                </div>

                <div class="card" draggable="true">
"""
html = html.replace("""
            <div class="dashboard">
                <div class="card">
                    <div class="card-title">Drowsiness Score</div>
                    <div class="score-value" id="score-val">0</div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" id="score-bar"></div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">Driver Heart Rate</div>
                    <div class="score-value" id="bpm-val" style="color: #ef4444; display: flex; align-items: center; gap: 10px;">
                        0 <span style="font-size: 1rem; color: #ffcccc;">BPM</span>
                    </div>
                </div>

                <div class="card">
""", dashboard_replacement)

# Fix the third card missing draggable
html = html.replace('<div class="card">\n                    <div class="card-title">Session Stats</div>', '<div class="card" draggable="true">\n                    <div class="card-title">Session Stats</div>')

# 5. Append JS at the end
js_inject = """
        // --- 1. Draggable Dashboard Layout ---
        const dashboard = document.getElementById('dashboard-container');
        const cards = dashboard.querySelectorAll('.card');
        
        cards.forEach(card => {
            card.addEventListener('dragstart', () => {
                card.classList.add('dragging');
            });
            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
            });
        });
        
        dashboard.addEventListener('dragover', e => {
            e.preventDefault();
            const afterElement = getDragAfterElement(dashboard, e.clientY);
            const draggable = document.querySelector('.dragging');
            if (afterElement == null) {
                dashboard.appendChild(draggable);
            } else {
                dashboard.insertBefore(draggable, afterElement);
            }
        });
        
        function getDragAfterElement(container, y) {
            const draggableElements = [...container.querySelectorAll('.card:not(.dragging)')];
            return draggableElements.reduce((closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = y - box.top - box.height / 2;
                if (offset < 0 && offset > closest.offset) {
                    return { offset: offset, element: child };
                } else {
                    return closest;
                }
            }, { offset: Number.NEGATIVE_INFINITY }).element;
        }

        // --- 2. Chart.js Data Visualizations ---
        const ctxScore = document.getElementById('scoreChart').getContext('2d');
        const ctxBpm = document.getElementById('bpmChart').getContext('2d');
        
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = "'Inter', sans-serif";
        
        const chartOptions = {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 0 },
            scales: {
                x: { display: false },
                y: { display: false, min: 0 }
            },
            plugins: { legend: { display: false }, tooltip: { enabled: false } }
        };

        const scoreChart = new Chart(ctxScore, {
            type: 'bar',
            data: {
                labels: Array(30).fill(''),
                datasets: [{
                    data: Array(30).fill(0),
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderRadius: 4
                }]
            },
            options: chartOptions
        });

        const bpmChart = new Chart(ctxBpm, {
            type: 'line',
            data: {
                labels: Array(50).fill(''),
                datasets: [{
                    data: Array(50).fill(0),
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: chartOptions
        });

        // --- 3. Dynamic Themes & Settings ---
        function changeTheme() {
            const theme = document.getElementById('theme-select').value;
            document.body.className = '';
            if (theme !== 'glass') {
                document.body.classList.add(`theme-${theme}`);
            }
            localStorage.setItem('aura_theme', theme);
        }
        
        // Load saved theme
        const savedTheme = localStorage.getItem('aura_theme');
        if (savedTheme) {
            document.getElementById('theme-select').value = savedTheme;
            changeTheme();
        }

        function saveSettings() {
            const url = document.getElementById('iot-url').value;
            fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ iot_webhook_url: url })
            }).then(() => {
                document.getElementById('settings-modal').classList.remove('visible');
            });
        }

        // --- 4. 3D Tilt Button ---
        const initBtn = document.getElementById('init-btn');
        initBtn.addEventListener('mousemove', (e) => {
            const rect = initBtn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width/2;
            const y = e.clientY - rect.top - rect.height/2;
            initBtn.style.transform = `perspective(1000px) rotateY(${x/5}deg) rotateX(${-y/5}deg) scale(1.05)`;
        });
        initBtn.addEventListener('mouseleave', () => {
            initBtn.style.transform = 'perspective(1000px) rotateY(0deg) rotateX(0deg) scale(1)';
        });

        // --- 5. Vanilla JS Particles ---
        const canvas = document.getElementById('particles-canvas');
        const ctx = canvas.getContext('2d');
        let width, height, particles = [];

        function initParticles() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
            particles = [];
            for (let i = 0; i < 100; i++) {
                particles.push({
                    x: Math.random() * width, y: Math.random() * height,
                    vx: (Math.random() - 0.5) * 1.5, vy: (Math.random() - 0.5) * 1.5,
                    size: Math.random() * 2 + 1
                });
            }
        }
        
        function animateParticles() {
            ctx.clearRect(0, 0, width, height);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.beginPath();
            
            particles.forEach((p, i) => {
                p.x += p.vx; p.y += p.vy;
                if (p.x < 0 || p.x > width) p.vx *= -1;
                if (p.y < 0 || p.y > height) p.vy *= -1;
                
                ctx.moveTo(p.x, p.y);
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                
                // Draw lines between close particles
                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                    if (dist < 100) {
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                    }
                }
            });
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
            ctx.stroke();
            ctx.fill();
            requestAnimationFrame(animateParticles);
        }
        
        initParticles();
        animateParticles();
        window.addEventListener('resize', initParticles);
"""
html = html.replace('// Landing Page Initialization', js_inject + '\n        // Landing Page Initialization')

# Update polling loop to update charts
chart_update_inject = """
                        // Update Charts
                        const sData = scoreChart.data.datasets[0].data;
                        sData.push(scoreValue);
                        sData.shift();
                        scoreChart.update();
                        
                        const bData = bpmChart.data.datasets[0].data;
                        bData.push(data.bpm);
                        bData.shift();
                        bpmChart.update();
"""
html = html.replace("const scoreValue = data.score;", "const scoreValue = data.score;" + chart_update_inject)

with open('templates/index.html', 'w') as f:
    f.write(html)
