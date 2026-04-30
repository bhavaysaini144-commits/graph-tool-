from flask import Flask, render_template_string

app = Flask(__name__)

# --- NEWTON v3: SCIENTIFIC STANDARD ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Newton v3 | Scientific Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;600&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <!-- MATH ENGINE -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.8.0/math.js"></script>
    <style>
        :root { 
            --bg: #1e1e1e; --panel: #252526; --accent: #007acc; --text: #d4d4d4; 
            --grid-mj: #444; --grid-mn: #333; --key-bg: #333333; --key-act: #3e3e42;
        }
        body { margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; overflow: hidden; display: flex; height: 100vh; touch-action: none; }
        
        /* SIDEBAR LAYOUT */
        .sidebar { 
            width: 360px; background: var(--panel); border-right: 1px solid #000; 
            display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; z-index: 20; 
            box-shadow: 5px 0 15px rgba(0,0,0,0.3);
        }

        /* HEADER & INPUT */
        .header { font-size: 12px; font-weight: 800; color: #666; letter-spacing: 2px; margin-bottom: 10px; display: flex; justify-content: space-between; }
        .status { font-size: 10px; color: #4fc1ff; }
        .status.err { color: #f48771; }

        .input-wrapper { position: relative; margin-bottom: 15px; }
        .fn-label { position: absolute; left: 10px; top: 12px; font-family: 'Roboto Mono'; color: #007acc; font-weight: bold; pointer-events: none; }
        input[type="text"] {
            width: 100%; background: #1e1e1e; border: 1px solid #3c3c3c; color: #fff;
            padding: 12px 10px 12px 50px; border-radius: 4px; font-family: 'Roboto Mono', monospace; font-size: 16px;
            box-sizing: border-box; outline: none; transition: 0.2s;
        }
        input[type="text"]:focus { border-color: var(--accent); background: #2d2d2d; }

        /* SCIENTIFIC KEYPAD */
        .keypad { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; margin-bottom: 15px; }
        .key {
            background: var(--key-bg); border: none; color: #fff;
            padding: 10px 0; border-radius: 2px; cursor: pointer; font-family: 'Inter'; font-size: 11px; font-weight: 600;
            transition: 0.1s; user-select: none; display: grid; place-items: center;
        }
        .key:active { background: var(--accent); transform: translateY(1px); }
        .key.num { background: #2d2d2d; font-size: 13px; font-family: 'Roboto Mono'; }
        .key.op { background: #252526; border: 1px solid #3c3c3c; color: var(--accent); }
        .key.var { color: #9cdcfe; }
        .key.del { background: #5a2d2d; color: #ffcccc; }
        .key.go { background: var(--accent); grid-column: span 2; }

        /* VARIABLE SLIDERS */
        .var-zone { flex: 1; overflow-y: auto; border-top: 1px solid #3c3c3c; padding-top: 10px; }
        .var-row { display: flex; align-items: center; margin-bottom: 8px; font-family: 'Roboto Mono'; font-size: 12px; background: #2d2d2d; padding: 5px; border-radius: 4px; }
        .var-label { color: #9cdcfe; width: 30px; font-weight: bold; }
        input[type="range"] { flex: 1; margin: 0 10px; height: 2px; accent-color: var(--accent); }
        
        /* CANVAS AREA */
        .viewport { flex: 1; position: relative; cursor: crosshair; background: #121212; }
        canvas { display: block; width: 100%; height: 100%; }
        
        /* HUD ELEMENTS */
        .hud-coords { 
            position: absolute; bottom: 10px; left: 10px; 
            background: rgba(0,0,0,0.8); color: #fff; 
            padding: 5px 10px; border-radius: 4px; font-family: 'Roboto Mono'; font-size: 11px; 
            border: 1px solid #444; pointer-events: none; 
        }
        .controls { position: absolute; bottom: 10px; right: 10px; display: flex; gap: 5px; }
        .btn-icon { width: 32px; height: 32px; background: #252526; color: white; border: 1px solid #444; border-radius: 4px; cursor: pointer; display: grid; place-items: center; font-size: 16px; }
        .btn-icon:hover { background: var(--accent); border-color: var(--accent); }

    </style>
</head>
<body>

<div class="sidebar">
    <div class="header">
        <span>SCIENTIFIC ENGINE</span>
        <span id="status" class="status">READY</span>
    </div>
    
    <div class="input-wrapper">
        <span class="fn-label">f(x)=</span>
        <input type="text" id="input" value="log(x)" spellcheck="false">
    </div>

    <!-- PRO KEYPAD -->
    <div class="keypad">
        <!-- Row 1 -->
        <button class="key" onclick="ins('sin(')">sin</button>
        <button class="key" onclick="ins('cos(')">cos</button>
        <button class="key" onclick="ins('tan(')">tan</button>
        <button class="key var" onclick="ins('pi')">π</button>
        <button class="key var" onclick="ins('e')">e</button>
        
        <!-- Row 2 -->
        <button class="key" onclick="ins('asin(')">sin⁻¹</button>
        <button class="key" onclick="ins('acos(')">cos⁻¹</button>
        <button class="key" onclick="ins('atan(')">tan⁻¹</button>
        <button class="key" onclick="ins('^')">xʸ</button>
        <button class="key" onclick="ins('sqrt(')">√</button>

        <!-- Row 3 -->
        <button class="key num" onclick="ins('7')">7</button>
        <button class="key num" onclick="ins('8')">8</button>
        <button class="key num" onclick="ins('9')">9</button>
        <button class="key op" onclick="ins('/')">÷</button>
        <button class="key" onclick="ins('ln(')">ln</button>

        <!-- Row 4 -->
        <button class="key num" onclick="ins('4')">4</button>
        <button class="key num" onclick="ins('5')">5</button>
        <button class="key num" onclick="ins('6')">6</button>
        <button class="key op" onclick="ins('*')">×</button>
        <button class="key" onclick="ins('log10(')">log</button>

        <!-- Row 5 -->
        <button class="key num" onclick="ins('1')">1</button>
        <button class="key num" onclick="ins('2')">2</button>
        <button class="key num" onclick="ins('3')">3</button>
        <button class="key op" onclick="ins('-')">−</button>
        <button class="key" onclick="ins('abs(')">|x|</button>

        <!-- Row 6 -->
        <button class="key num" onclick="ins('0')">0</button>
        <button class="key num" onclick="ins('.')">.</button>
        <button class="key var" onclick="ins('x')">x</button>
        <button class="key op" onclick="ins('+')">+</button>
        <button class="key op" onclick="ins('(')">(</button>

        <!-- Row 7 -->
        <button class="key del" onclick="del()">DEL</button>
        <button class="key op" onclick="ins(')')">)</button>
        <button class="key go" onclick="render()">GRAPH ↵</button>
    </div>

    <div class="header" style="margin-top: 10px; border-top: 1px solid #333; padding-top: 10px;">
        <span>PARAMETERS</span>
    </div>
    <div id="var-zone" class="var-zone"></div>
</div>

<div class="viewport" id="vp">
    <canvas id="canvas"></canvas>
    <div class="hud-coords" id="coords">x: 0, y: 0</div>
    <div class="controls">
        <button class="btn-icon" onclick="resetView()">⌖</button>
        <button class="btn-icon" onclick="zoom(1.2)">+</button>
        <button class="btn-icon" onclick="zoom(0.8)">−</button>
    </div>
</div>

<script>
    // --- CORE CONFIG ---
    const cvs = document.getElementById('canvas');
    const ctx = cvs.getContext('2d');
    const inp = document.getElementById('input');
    const stat = document.getElementById('status');
    
    let view = { x: 0, y: 0, scale: 50 }; // View center (world coords), scale (px per unit)
    let vars = {}; // Variable store
    let drag = { active: false, lx: 0, ly: 0 };

    // --- RESIZE ---
    function resize() {
        cvs.width = cvs.parentElement.clientWidth;
        cvs.height = cvs.parentElement.clientHeight;
        render();
    }
    window.addEventListener('resize', resize);

    // --- MATH PARSING ---
    function updateVars(node) {
        let found = new Set();
        node.traverse(n => {
            if (n.isSymbolNode && !['x','e','pi'].includes(n.name) && !math[n.name]) {
                found.add(n.name);
            }
        });
        
        let zone = document.getElementById('var-zone');
        let needsUpdate = false;
        
        // Check consistency
        let current = Object.keys(vars);
        let next = Array.from(found).sort();
        if (JSON.stringify(current) !== JSON.stringify(next)) needsUpdate = true;

        if (needsUpdate) {
            zone.innerHTML = '';
            if (next.length === 0) zone.innerHTML = '<div style="color:#444;font-size:11px;text-align:center;padding:10px;">No variables detected</div>';
            
            next.forEach(v => {
                if (vars[v] === undefined) vars[v] = 1;
                let row = document.createElement('div');
                row.className = 'var-row';
                row.innerHTML = `
                    <span class="var-label">${v}</span>
                    <input type="range" min="-5" max="5" step="0.01" value="${vars[v]}" oninput="setVar('${v}', this.value)">
                    <span style="width:35px;text-align:right">${vars[v]}</span>
                `;
                zone.appendChild(row);
            });
            // Clean old
            for(let k in vars) if(!found.has(k)) delete vars[k];
        }
    }
    window.setVar = (k,v) => { vars[k] = parseFloat(v); render(); };

    function render() {
        // 1. Clear
        ctx.fillStyle = "#121212";
        ctx.fillRect(0, 0, cvs.width, cvs.height);
        
        // 2. Grid
        drawGrid();

        // 3. Parse & Draw
        let expr = inp.value.trim();
        if(!expr) return;
        if(expr.includes('=')) expr = expr.split('=')[1]; // Handle y=...

        try {
            const node = math.parse(expr);
            const code = node.compile();
            updateVars(node);
            
            stat.innerText = "RENDERING"; stat.className = "status";
            drawGraph(code);
            
        } catch(e) {
            stat.innerText = "SYNTAX ERROR"; stat.className = "status err";
        }
    }

    function drawGraph(func) {
        ctx.beginPath();
        ctx.strokeStyle = "#007acc";
        ctx.lineWidth = 2;
        
        let scope = { ...vars };
        let w = cvs.width, h = cvs.height;
        let cx = w/2, cy = h/2;
        
        // DRAW LOOP
        let prevY = null;
        
        for (let px = 0; px <= w; px += 1) { // High Res
            // Screen -> World
            let worldX = (px - cx) / view.scale + view.x;
            scope.x = worldX;
            
            try {
                let worldY = func.evaluate(scope);
                
                // Handle Math Errors (like sqrt(-1) or log(-1))
                if (isNaN(worldY) || !isFinite(worldY)) {
                    // Check if we need to draw asymptote line
                    // For log(x), as x->0, y->-Infinity. 
                    // We clamp it for visual continuity.
                    if (prevY !== null) {
                        // If prev point was valid, draw off-screen
                        let clampY = (prevY < cy) ? -h*2 : h*2;
                        // ctx.lineTo(px, clampY); // Optional: Draw vertical asymptote
                    }
                    prevY = null;
                    continue;
                }

                // World -> Screen
                let py = cy - (worldY - view.y) * view.scale;

                // CLAMPING (The "Pure Length" Fix)
                // If y is way off screen, clamp it so lineTo draws to the edge
                let clampedY = py;
                if (py < -h) clampedY = -h;
                if (py > h*2) clampedY = h*2;

                if (prevY === null) {
                    ctx.moveTo(px, clampedY);
                } else {
                    // Discontinuity Check (e.g. tan(x))
                    if (Math.abs(py - prevY) > h) {
                        ctx.moveTo(px, py); // Lift pen
                    } else {
                        ctx.lineTo(px, py);
                    }
                }
                prevY = py;

            } catch(e) { prevY = null; }
        }
        ctx.stroke();
    }

    function drawGrid() {
        let cx = cvs.width/2;
        let cy = cvs.height/2;
        
        // Calc Grid Spacing
        let step = 1;
        if (view.scale > 80) step = 0.5;
        if (view.scale < 30) step = 2;
        if (view.scale < 10) step = 10;

        let startX = Math.floor(((0 - cx)/view.scale + view.x)/step)*step;
        let endX   = Math.ceil(((cvs.width - cx)/view.scale + view.x)/step)*step;
        let startY = Math.floor(((cy - cvs.height)/view.scale + view.y)/step)*step;
        let endY   = Math.ceil(((cy - 0)/view.scale + view.y)/step)*step;

        ctx.lineWidth = 1;
        ctx.font = "10px Roboto Mono";
        ctx.textAlign = "center";
        
        // Draw
        for (let x = startX; x <= endX; x+=step) {
            let px = cx + (x - view.x) * view.scale;
            ctx.beginPath();
            ctx.strokeStyle = (Math.abs(x) < 1e-10) ? "#fff" : (Math.abs(x)%5===0 ? "#555" : "#333");
            ctx.moveTo(px, 0); ctx.lineTo(px, cvs.height);
            ctx.stroke();
            if(Math.abs(x) > 1e-10) {
                ctx.fillStyle = "#888"; ctx.fillText(parseFloat(x.toFixed(2)), px, cy + 15);
            }
        }
        for (let y = startY; y <= endY; y+=step) {
            let py = cy - (y - view.y) * view.scale;
            ctx.beginPath();
            ctx.strokeStyle = (Math.abs(y) < 1e-10) ? "#fff" : (Math.abs(y)%5===0 ? "#555" : "#333");
            ctx.moveTo(0, py); ctx.lineTo(cvs.width, py);
            ctx.stroke();
            if(Math.abs(y) > 1e-10) {
                ctx.fillStyle = "#888"; ctx.fillText(parseFloat(y.toFixed(2)), cx - 15, py + 3);
            }
        }
    }

    // --- CONTROLS ---
    function ins(txt) {
        let start = inp.selectionStart;
        inp.value = inp.value.slice(0, start) + txt + inp.value.slice(inp.selectionEnd);
        inp.focus();
        inp.setSelectionRange(start + txt.length, start + txt.length);
        render();
    }
    function del() {
        let start = inp.selectionStart;
        if(start>0) {
            inp.value = inp.value.slice(0, start-1) + inp.value.slice(start);
            inp.focus();
            inp.setSelectionRange(start-1, start-1);
            render();
        }
    }

    // --- NAV ---
    cvs.addEventListener('mousedown', e => {
        drag.active = true;
        drag.lx = e.clientX; drag.ly = e.clientY;
    });
    window.addEventListener('mouseup', () => drag.active = false);
    window.addEventListener('mousemove', e => {
        // Pan
        if(drag.active) {
            let dx = (e.clientX - drag.lx) / view.scale;
            let dy = (e.clientY - drag.ly) / view.scale;
            view.x -= dx; view.y += dy;
            drag.lx = e.clientX; drag.ly = e.clientY;
            render();
        }
        // Coords
        let cx = cvs.width/2, cy = cvs.height/2;
        let wx = (e.clientX - cvs.getBoundingClientRect().left - cx) / view.scale + view.x;
        let wy = (cy - (e.clientY - cvs.getBoundingClientRect().top)) / view.scale + view.y;
        document.getElementById('coords').innerText = `x: ${wx.toFixed(2)}, y: ${wy.toFixed(2)}`;
    });
    
    // Zoom
    function zoom(f) { view.scale *= f; render(); }
    function resetView() { view.x=0; view.y=0; view.scale=50; render(); }
    cvs.addEventListener('wheel', e => {
        e.preventDefault();
        zoom(e.deltaY < 0 ? 1.1 : 0.9);
    }, {passive:false});

    // --- INIT ---
    inp.addEventListener('input', render);
    window.onload = resize;

</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
