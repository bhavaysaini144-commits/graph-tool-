from flask import Flask, render_template_string

app = Flask(__name__)

# --- NEWTON v4: PRECISION ENGINE ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newton v4 | Precision Graph</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.8.0/math.js"></script>
    <style>
        /* CLEAN, MINIMALIST UI */
        :root { --bg: #ffffff; --sidebar: #f4f4f5; --accent: #2563eb; --text: #18181b; --grid: #e4e4e7; --border: #d4d4d8; }
        body { margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; display: flex; height: 100vh; overflow: hidden; }
        
        /* SIDEBAR */
        .sidebar { width: 320px; background: var(--sidebar); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 20px; z-index: 10; box-shadow: 2px 0 10px rgba(0,0,0,0.05); }
        
        .title { font-weight: 800; font-size: 14px; letter-spacing: 1px; margin-bottom: 20px; color: #52525b; text-transform: uppercase; }
        
        /* INPUT BOX */
        .input-container { position: relative; margin-bottom: 10px; }
        .input-label { position: absolute; left: 12px; top: 11px; color: var(--accent); font-weight: 700; font-family: 'JetBrains Mono'; font-size: 14px; pointer-events: none; }
        input[type="text"] {
            width: 100%; padding: 10px 10px 10px 50px; border: 1px solid var(--border); border-radius: 6px;
            font-family: 'JetBrains Mono', monospace; font-size: 16px; outline: none; box-sizing: border-box;
            background: white; color: #000; transition: 0.2s;
        }
        input[type="text"]:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
        
        /* STATUS & HELP */
        #status { font-size: 11px; margin-top: 5px; font-weight: 600; min-height: 15px; }
        .ok { color: #16a34a; }
        .err { color: #dc2626; }
        
        .tips { font-size: 11px; color: #71717a; margin-top: 5px; line-height: 1.4; }

        /* VARIABLES */
        #var-list { flex: 1; overflow-y: auto; margin-top: 20px; border-top: 1px solid var(--border); padding-top: 10px; }
        .var-item { display: flex; align-items: center; margin-bottom: 12px; font-family: 'JetBrains Mono'; font-size: 12px; }
        .var-label { width: 20px; font-weight: bold; color: var(--accent); }
        input[type="range"] { flex: 1; margin: 0 10px; accent-color: var(--accent); cursor: pointer; }
        .var-val { width: 40px; text-align: right; color: #555; }

        /* CANVAS */
        .main { flex: 1; position: relative; cursor: crosshair; }
        canvas { display: block; width: 100%; height: 100%; }
        
        /* HUD */
        .coords { position: absolute; bottom: 15px; left: 15px; background: rgba(255,255,255,0.9); padding: 6px 10px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 12px; border: 1px solid var(--border); pointer-events: none; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        
        .reset-btn { position: absolute; top: 15px; right: 15px; background: white; border: 1px solid var(--border); padding: 8px 12px; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: 0.2s; }
        .reset-btn:hover { background: #f4f4f5; }

    </style>
</head>
<body>

<div class="sidebar">
    <div class="title">Precision Grapher</div>
    
    <div class="input-container">
        <span class="input-label">y =</span>
        <input type="text" id="input" value="x^2 - 4" placeholder="Type Math..." spellcheck="false">
    </div>
    <div id="status" class="ok">Ready</div>
    <div class="tips">
        Try: <span style="font-family:'JetBrains Mono'">sin(x)</span>, <span style="font-family:'JetBrains Mono'">2x + 1</span>, <span style="font-family:'JetBrains Mono'">log(x)</span><br>
        * Auto-multiplication enabled (2x → 2*x)
    </div>

    <div id="var-list"></div>
</div>

<div class="main">
    <canvas id="canvas"></canvas>
    <div class="coords" id="coords">x: 0.0, y: 0.0</div>
    <button class="reset-btn" onclick="resetView()">Recenter View</button>
</div>

<script>
    const cvs = document.getElementById('canvas');
    const ctx = cvs.getContext('2d');
    const inp = document.getElementById('input');
    const stat = document.getElementById('status');
    
    // ENGINE STATE
    let state = {
        scale: 40, // Pixels per unit
        cx: 0, cy: 0, // Center in Pixels (calculated on resize)
        xOffset: 0, yOffset: 0, // Pan offset in Pixels
        vars: {},
        dragging: false,
        lx: 0, ly: 0
    };

    // --- 1. ROBUST INPUT SANITIZATION ---
    function cleanInput(expr) {
        if (!expr) return "";
        // Remove 'y=' or 'f(x)='
        if (expr.includes('=')) expr = expr.split('=')[1];
        
        // Auto-Multiply: 2x -> 2*x, x sin(x) -> x*sin(x), (x+1)(x-1) -> (x+1)*(x-1)
        // Regex looks for: Number/Paren followed immediately by Letter/Paren
        expr = expr.replace(/(\d|\))(?=[a-z]|\()/gi, '$1*');
        
        return expr;
    }

    // --- 2. PARSER & VARIABLE DETECTOR ---
    function updateVars(node) {
        let found = new Set();
        node.traverse(n => {
            // Find symbols that are NOT built-in math functions
            if (n.isSymbolNode && !['x', 'e', 'pi'].includes(n.name) && typeof math[n.name] !== 'function') {
                found.add(n.name);
            }
        });
        
        // Sync UI
        const list = document.getElementById('var-list');
        const current = Object.keys(state.vars);
        const next = Array.from(found).sort();

        if (JSON.stringify(current) !== JSON.stringify(next)) {
            list.innerHTML = '';
            if (next.length === 0) list.innerHTML = '<div style="text-align:center; color:#999; font-size:11px; margin-top:10px;">No dynamic variables</div>';
            
            next.forEach(v => {
                if (state.vars[v] === undefined) state.vars[v] = 1.0;
                let div = document.createElement('div');
                div.className = 'var-item';
                div.innerHTML = `
                    <span class="var-label">${v}</span>
                    <input type="range" min="-5" max="5" step="0.1" value="${state.vars[v]}" oninput="setVar('${v}', this.value)">
                    <span class="var-val">${state.vars[v]}</span>
                `;
                list.appendChild(div);
            });
            // Cleanup old keys
            for (let k in state.vars) if (!found.has(k)) delete state.vars[k];
        }
    }
    window.setVar = (k, v) => { state.vars[k] = parseFloat(v); render(); };

    // --- 3. RENDERING CORE ---
    function render() {
        // Clear
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, cvs.width, cvs.height);
        
        drawGrid();
        
        let raw = inp.value.trim();
        if (!raw) return;

        try {
            let clean = cleanInput(raw);
            const node = math.parse(clean);
            const code = node.compile();
            updateVars(node);
            
            stat.innerText = "Graphing: " + clean;
            stat.className = "ok";
            
            drawCurve(code);
        } catch (e) {
            stat.innerText = "Error: " + e.message.split('(')[0]; // Short error
            stat.className = "err";
        }
    }

    function drawCurve(func) {
        ctx.beginPath();
        ctx.strokeStyle = "#2563eb"; // Blue
        ctx.lineWidth = 2;
        ctx.lineJoin = "round";

        let w = cvs.width;
        let h = cvs.height;
        let scope = { ...state.vars };
        
        let started = false;
        let prevY = NaN;

        // Step Size: 1px is standard, 0.5px is high precision
        // We stick to 1px for speed, but handle jumps carefully
        for (let px = 0; px <= w; px++) {
            // Screen X -> Math X
            // formula: (px - center_x - offset_x) / scale
            let x = (px - state.cx - state.xOffset) / state.scale;
            scope.x = x;

            try {
                let y = func.evaluate(scope);
                
                // Math Y -> Screen Y
                // formula: center_y + offset_y - (y * scale)  [Minus because Screen Y is inverted]
                let py = state.cy + state.yOffset - (y * state.scale);

                // Check for validity
                if (isNaN(py) || !isFinite(py) || Math.abs(y) > 1e6) {
                    started = false;
                    prevY = NaN;
                    continue;
                }

                // ASYMPTOTE DETECTION
                // If the jump from prevY to currentY is massive (greater than screen height),
                // it's likely a vertical asymptote (like tan(x) or 1/x). Don't connect.
                if (started && Math.abs(py - prevY) > h) {
                    ctx.moveTo(px, py);
                } else if (!started) {
                    ctx.moveTo(px, py);
                    started = true;
                } else {
                    ctx.lineTo(px, py);
                }
                prevY = py;

            } catch (e) {
                started = false;
                prevY = NaN;
            }
        }
        ctx.stroke();
    }

    function drawGrid() {
        ctx.lineWidth = 1;
        ctx.font = "10px JetBrains Mono";
        ctx.fillStyle = "#666";
        
        let w = cvs.width;
        let h = cvs.height;
        
        // Dynamic Grid Sizing
        let step = 1; // Math Units
        if (state.scale > 80) step = 0.5;
        if (state.scale < 30) step = 2;
        if (state.scale < 15) step = 5;
        if (state.scale < 5) step = 10;

        // Visible Range
        let startX = Math.floor((-state.cx - state.xOffset) / state.scale);
        let endX = Math.ceil((w - state.cx - state.xOffset) / state.scale);
        
        let startY = Math.floor((state.cy + state.yOffset - h) / state.scale);
        let endY = Math.ceil((state.cy + state.yOffset) / state.scale);

        ctx.beginPath();
        
        // Vertical Lines (X)
        for (let x = startX; x <= endX; x++) {
            if (x % step !== 0) continue;
            let px = state.cx + state.xOffset + (x * state.scale);
            
            // Axis vs Grid
            if (x === 0) ctx.strokeStyle = "#000"; // Y-Axis
            else ctx.strokeStyle = "#e4e4e7";
            
            ctx.moveTo(px, 0); ctx.lineTo(px, h);
            
            // Label
            if (x !== 0) ctx.fillText(x, px + 2, state.cy + state.yOffset + 12);
        }

        // Horizontal Lines (Y)
        for (let y = startY; y <= endY; y++) {
            if (y % step !== 0) continue;
            let py = state.cy + state.yOffset - (y * state.scale);
            
            if (y === 0) ctx.strokeStyle = "#000"; // X-Axis
            else ctx.strokeStyle = "#e4e4e7";

            ctx.moveTo(0, py); ctx.lineTo(w, py);
            
            // Label
            if (y !== 0) ctx.fillText(y, state.cx + state.xOffset + 4, py - 2);
        }
        ctx.stroke();
    }

    // --- 4. NAVIGATION ---
    function resize() {
        cvs.width = cvs.parentElement.clientWidth;
        cvs.height = cvs.parentElement.clientHeight;
        state.cx = cvs.width / 2;
        state.cy = cvs.height / 2;
        render();
    }
    window.addEventListener('resize', resize);
    window.onload = resize;

    // Mouse Interaction
    cvs.addEventListener('mousedown', e => {
        state.dragging = true;
        state.lx = e.clientX; state.ly = e.clientY;
    });
    window.addEventListener('mouseup', () => state.dragging = false);
    
    window.addEventListener('mousemove', e => {
        // Pan
        if (state.dragging) {
            state.xOffset += e.clientX - state.lx;
            state.yOffset += e.clientY - state.ly;
            state.lx = e.clientX; state.ly = e.clientY;
            render();
        }
        
        // Coordinates
        let rect = cvs.getBoundingClientRect();
        let mx = e.clientX - rect.left;
        let my = e.clientY - rect.top;
        let mathX = (mx - state.cx - state.xOffset) / state.scale;
        let mathY = (state.cy + state.yOffset - my) / state.scale;
        document.getElementById('coords').innerText = `x: ${mathX.toFixed(2)}, y: ${mathY.toFixed(2)}`;
    });

    // Zoom
    cvs.addEventListener('wheel', e => {
        e.preventDefault();
        let zoom = e.deltaY < 0 ? 1.1 : 0.9;
        state.scale *= zoom;
        // Cap zoom to prevent crashes
        if (state.scale < 2) state.scale = 2;
        if (state.scale > 500) state.scale = 500;
        render();
    }, {passive: false});

    function resetView() {
        state.scale = 40;
        state.xOffset = 0; state.yOffset = 0;
        render();
    }

    // Live Update
    inp.addEventListener('input', render);

</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(debug=True, port=8080)

