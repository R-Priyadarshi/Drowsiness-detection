with open("templates/index.html", "r") as f:
    content = f.read()

# Fix 1: The broken CSS and HEAD
# We have a duplicate </head> and weird text around line 570.
# Let's remove from the first </head> to the second </head>.
import re
# Find the end of the first </head> and the actual <body>
# The broken block is:
#     </style>
# </head>
#             color: #00ff88;
#             font-size: 2rem;
#             letter-spacing: 2px;
#             margin-bottom: 10px;
#             text-transform: uppercase;
#         }
#         
#         .calibration-subtext {
#             color: #ccc;
#             font-size: 1rem;
#         }
#     </style>
# </head>
# <body>

broken_block_regex = r"</head>\s+color: #00ff88;.*?</style>\s*</head>"
content = re.sub(broken_block_regex, "</head>", content, flags=re.DOTALL)

# Let's also make sure we didn't accidentally delete the calibration-text CSS, which was meant for the calibration overlay.
# I'll just re-add it into the main <style> block properly.
calibration_css = """
        .calibration-text {
            color: #00ff88;
            font-size: 2rem;
            letter-spacing: 2px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .calibration-subtext {
            color: #ccc;
            font-size: 1rem;
        }
"""
content = content.replace("/* Calibration Overlay */", calibration_css + "\n        /* Calibration Overlay */")

# Fix 2: Add the missing <canvas> tags and draggability to dashboard cards.
dashboard_regex = r'<!-- Score Card -->.*?<div class="card">.*?<div class="card-title">Drowsiness Score</div>.*?</div>\s*</div>'
new_score_card = """<!-- Score Card -->
            <div class="card" draggable="true">
                <div class="card-title">Drowsiness Score</div>
                <div class="score-value" id="score-val">0</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="score-bar"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.75rem; color: var(--text-muted);">
                    <span>0 (Awake)</span>
                    <span>30 (Alarm)</span>
                </div>
                <div class="chart-container"><canvas id="scoreChart"></canvas></div>
            </div>"""
content = re.sub(r'<!-- Score Card -->\s*<div class="card">\s*<div class="card-title">Drowsiness Score</div>.*?</div>\s*</div>', new_score_card, content, flags=re.DOTALL)

# Add chart to the Eye & Heart stats card specifically for Heart Rate.
# Wait, the heart rate card is inside a grid.
heart_rate_card = r'<div class="card eye-card">\s*<div class="eye-label">Heart Rate \(rPPG\)</div>\s*<div class="eye-val" id="bpm-val" style="color: #ff44aa;">-- BPM</div>\s*</div>'
new_heart_rate_card = """<div class="card eye-card" draggable="true" style="grid-column: span 3;">
                    <div class="eye-label">Heart Rate (rPPG)</div>
                    <div class="eye-val" id="bpm-val" style="color: #ef4444;">-- BPM</div>
                    <div class="chart-container"><canvas id="bpmChart"></canvas></div>
                </div>"""
# Let's just replace the whole eye-stats grid to include the charts correctly and make them draggable.
eye_stats_grid = r'<!-- Eye & Heart Stats -->\s*<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;">.*?</div>\s*</div>\s*</div>'
new_eye_stats = """<!-- Eye & Heart Stats -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div class="card eye-card" draggable="true">
                    <div class="eye-label">L-Eye Close Prob</div>
                    <div class="eye-val" id="left-eye-val">0.00</div>
                </div>
                <div class="card eye-card" draggable="true">
                    <div class="eye-label">R-Eye Close Prob</div>
                    <div class="eye-val" id="right-eye-val">0.00</div>
                </div>
            </div>
            
            <div class="card" draggable="true">
                <div class="card-title">Heart Rate (rPPG)</div>
                <div class="score-value" id="bpm-val" style="color: #ef4444; display: flex; align-items: center; gap: 10px;">
                    -- <span style="font-size: 1rem; color: #ffcccc;">BPM</span>
                </div>
                <div class="chart-container"><canvas id="bpmChart"></canvas></div>
            </div>"""
content = re.sub(r'<!-- Eye & Heart Stats -->\s*<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;">.*?</div>\s*</div>\s*</div>', new_eye_stats, content, flags=re.DOTALL)

# Also make the System State Card draggable
content = content.replace('<div class="card" style="margin-top: auto;">\n                <div class="card-title">Current State</div>', '<div class="card" draggable="true" style="margin-top: auto;">\n                <div class="card-title">Current State</div>')


# Fix 3: The Chart.js missing updating logic in the fetch status loop
# In the JS, we have `scoreVal.textContent = data.score;`
# We need to add the Chart updating logic there.
chart_update_logic = """
                    scoreVal.textContent = data.score;
                    // Update Charts
                    if (typeof scoreChart !== 'undefined') {
                        const sData = scoreChart.data.datasets[0].data;
                        sData.push(data.score);
                        sData.shift();
                        scoreChart.update();
                    }
                    if (typeof bpmChart !== 'undefined' && data.bpm > 0) {
                        const bData = bpmChart.data.datasets[0].data;
                        bData.push(data.bpm);
                        bData.shift();
                        bpmChart.update();
                    }
"""
content = content.replace("scoreVal.textContent = data.score;", chart_update_logic)

# Fix undefined scoreValue at line 751
content = content.replace("if (data.iot_triggered && scoreValue > 30) {", "if (data.iot_triggered && data.score > 30) {")

# Write it back
with open("templates/index.html", "w") as f:
    f.write(content)

