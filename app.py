from flask import Flask, render_template_string

app = Flask(__name__)

# --- PROJECT NEWTON: THE GRAPHING ENGINE ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newton | Mathematical Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <!-- MATH.JS: The Calculation Brain -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.8.0/math.js"></script>
    <style>
        :root { --bg: #0d1117; --panel: #161b22; --accent: #2f81f7; --text: #c9d1d9; --grid: #30363d; }
        body { margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; overflow: hidden; display: flex; height: 100vh; }
        
        /* LAYOUT */
        .sidebar { width: 320px; background: var(--panel); border-right: 1px solid var(--grid); display: flex; flex-direction: column; padding: 15px; box-sizing: border-box; z-index: 10; }
        .viewport { flex: 1; position: relative; overflow: hidden; cursor: crosshair; }
        
        /* INPUT AREA */
        .input-group { margin-bottom: 15px; }
        .label { font-size: 12px; font-weight: 600; color: #8b949e; margin-bottom: 5px; display: block; }
        input[type="text"] {
            width: 100%; background: #0d1117; border: 1px solid var(--grid); color: #fff;
            padding: 12px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 16px;
            box-sizing: border-box; outline: none; transition: 0.2s;
        }
        input[type="text"]:focus { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(47, 129, 247, 0.3); }
        
        /* KEYPAD */
        .keypad { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 20px; }
        .key {
            background: #21262d; border: 1px solid rgba(240,246,252,0.1); color: #fff;
            padding: 10px 0; border-radius: 6px; cursor: pointer; font-family: 'JetBrains Mono'; font-size: 13px;
            transition: 0.1s; user-select: none;
        }
        .key:hover { background: #30363d; }
        .key:active { background: var(--accent); border-color: var(--accent); }
        .key.fn { color: var(--accent); font-weight: bold; }

        /* VARIABLE REACTOR */
        #variables { flex: 1; overflow-y: auto; border-top: 1px solid var(--grid); padding-top: 10px; }
        .var-row { display: flex; align-items: center; margin-bottom: 10px; font-size: 14px; }
        .var-name { width: 30px; font-family: 'JetBrains Mono'; font-weight: bold; color: #79c0ff; }
        input[type="range"] { flex: 1; margin: 0 10px; accent-color: var(--accent); cursor: pointer; }
        .var-val { width: 40px; text-align: right; font-size: 12px; }

        /* CANVAS */
        canvas { display: block; width: 100%; height: 100%; }
        
        /* OVERLAYS */
        .zoom-controls { position: absolute; bottom: 20px; right: 20px; display: flex; gap: 10px; }
        .fab { width: 40px; height: 40px; border-radius: 50%; background: var(--panel); border: 1px solid var(--grid); color: white; font-size: 20px; cursor: pointer; display: grid; place-items: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        .fab:hover { background: var(--accent); }

        .coords { position: absolute; top: 10px; right: 20px; background: rgba(0,0,0,0.7); padding: 5px 10px; border-radius: 4px; font-family: 'JetBrains Mono'; font-size: 12px; pointer-events: none; }
    </style>
</head>
<body>

<!-- SIDEBAR: INPUT & CONTROLS -->
<div class="sidebar">
    <div class="input-group">
        <span class="label">FUNCTION f(x) =</span>
        <input type="text" id="eq-input" value="sin(x) * x" placeholder="Type eq... e.g. x^2">
    </div>

    <div class="keypad">
        <button class="key fn" onclick="insert('sin(')">sin</button>
        <button class="key fn" onclick="insert('cos(')">cos</button>
        <button class="key fn" onclick="insert('tan(')">tan</button>
        <button class="key" onclick="insert('^')">^</button>
        
        <button class="key fn" onclick="insert('log(')">log</button>
        <button class="key fn" onclick="insert('sqrt(')">√</button>
        <button class="key fn" onclick="insert('floor(')">[ ]</button>
        <button class="key" onclick="insert('pi')">π</button>
        
        <button class="key" onclick="insert('(')">(</button>
        <button class="key" onclick="insert(')')">)</button>
        <button class="key" onclick="insert('x')">x</button>
        <button class="key" onclick="backspace()">⌫</button>
    </div>

    <span class="label">VARIABLE REACTOR</span>
    <div id="variables">
        <!-- Sliders appear here -->
        <div style="color: #555; font-size: 12px; text-align: center; margin-top: 20px;">No variables detected</div>
    </div>
</div>

<!-- MAIN VIEWPORT -->
<div class="viewport">
    <div class="coords" id="coord-box">x: 0.00, y: 0.00</div>
    <canvas id="graph"></canvas>
    
    <div class="zoom-controls">
        <button class="fab" onclick="resetView()">⟲</button>
        <button class="fab" onclick="zoom(1.2)">+</button>
        <button class="fab" onclick="zoom(0.8)">−</button>
    </div>
</div>

<script>
    const canvas = document.getElementById('graph');
    const ctx = canvas.getContext('2d');
    const input = document.getElementById('eq-input');
    const varBox = document.getElementById('variables');

    // --- ENGINE STATE ---
    let state = {
        scale: 40, // Pixels per unit
        offsetX: 0, 
        offsetY: 0,
        variables: {}, // Stores values for m, c, a, etc.
        isDragging: false,
        lastMouse: {x: 0, y: 0}
    };

    // --- INITIALIZATION ---
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
        state.offsetX = canvas.width / 2;
        state.offsetY = canvas.height / 2;
        draw();
    }
    window.addEventListener('resize', resize);

    // --- INPUT HANDLING ---
    function insert(txt) {
        let curPos = input.selectionStart;
        let val = input.value;
        input.value = val.slice(0, curPos) + txt + val.slice(input.selectionEnd);
        input.focus();
        input.setSelectionRange(curPos + txt.length, curPos + txt.length);
        parseAndDraw();
    }

    function backspace() {
        let curPos = input.selectionStart;
        if (curPos === 0) return;
        let val = input.value;
        input.value = val.slice(0, curPos - 1) + val.slice(curPos);
        input.focus();
        input.setSelectionRange(curPos - 1, curPos - 1);
        parseAndDraw();
    }

    input.addEventListener('input', parseAndDraw);

    // --- THE VARIABLE REACTOR ---
    function updateVariables(node) {
        // 1. Extract symbols from the MathJS node tree
        let symbols = new Set();
        node.traverse(function (node, path, parent) {
            if (node.type === 'SymbolNode' && node.name !== 'x' && node.name !== 'e' && node.name !== 'pi') {
                if (!math[node.name]) { // Ignore built-ins like sin/cos if parsed as symbol
                    symbols.add(node.name);
                }
            }
        });

        // 2. Sync State
        let currentVars = Object.keys(state.variables);
        let newVars = Array.from(symbols);
        let needsUpdate = false;

        // Check for changes
        if (currentVars.length !== newVars.length) needsUpdate = true;
        else {
            for(let v of newVars) if(!state.variables.hasOwnProperty(v)) needsUpdate = true;
        }

        if (needsUpdate) {
            varBox.innerHTML = '';
            if (newVars.length === 0) {
                varBox.innerHTML = '<div style="color: #555; font-size: 12px; text-align: center; margin-top: 20px;">No variables detected</div>';
            }
            
            newVars.sort().forEach(v => {
                if (!state.variables[v]) state.variables[v] = 1; // Default value
                
                let row = document.createElement('div');
                row.className = 'var-row';
                row.innerHTML = `
                    <span class="var-name">${v}</span>
                    <input type="range" min="-10" max="10" step="0.1" value="${state.variables[v]}" oninput="setVar('${v}', this.value)">
                    <span class="var-val" id="val-${v}">${state.variables[v]}</span>
                `;
                varBox.appendChild(row);
            });
        }
    }

    window.setVar = (name, val) => {
        state.variables[name] = parseFloat(val);
        document.getElementById(`val-${name}`).innerText = val;
        draw(); // Re-draw instantly
    };

    // --- CORE GRAPHING ENGINE ---
    function parseAndDraw() {
        try {
            const expr = input.value;
            if (!expr) return;
            const node = math.parse(expr);
            const code = node.compile();
            
            // Update UI for variables
            updateVariables(node);

            draw(code);
        } catch (e) {
            // console.log("Incomplete Expression");
        }
    }

    function draw(compiledFunc) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // 1. Draw Grid
        drawGrid();

        // 2. Draw Function
        if (!compiledFunc && input.value) {
             try { compiledFunc = math.compile(input.value); } catch(e) { return; }
        }
        if (!compiledFunc) return;

        ctx.beginPath();
        ctx.strokeStyle = '#2f81f7';
        ctx.lineWidth = 2;

        // Scope includes x and all dynamic variables
        let scope = { ...state.variables }; 

        let started = false;
        // Iterate pixels across the screen
        for (let px = 0; px < canvas.width; px += 2) { // Step 2px for speed
            // Screen X -> World X
            let x = (px - state.offsetX) / state.scale;
            scope.x = x;

            try {
                let y = compiledFunc.evaluate(scope);
                
                // World Y -> Screen Y
                // Note: Canvas Y is inverted (0 is top)
                let py = state.offsetY - (y * state.scale);

                // DISCONTINUITY CHECK (The "Great Integer" Fix)
                // If the jump is too big (vertical line), lift the pen
                if (started) {
                    // Get previous point
                    // (We could cache it, but let's check boundary)
                    if (Math.abs(py - ctx.currentY) > canvas.height) { 
                        // Massive jump (likely asymptotic or tan(x)), don't draw line
                        ctx.moveTo(px, py);
                    } else {
                        ctx.lineTo(px, py);
                    }
                } else {
                    ctx.moveTo(px, py);
                    started = true;
                }
                
                // Hack to track previous Y for Discontinuity Check
                ctx.currentY = py;

            } catch (e) {
                started = false; // Gap in domain (e.g. sqrt(-1))
            }
        }
        ctx.stroke();
    }

    function drawGrid() {
        ctx.strokeStyle = '#30363d';
        ctx.lineWidth = 1;
        ctx.font = "10px Inter";
        ctx.fillStyle = "#8b949e";

        let startX = -state.offsetX / state.scale;
        let endX = (canvas.width - state.offsetX) / state.scale;
        let startY = -(canvas.height - state.offsetY) / state.scale; // Bottom (since Y inverted)
        let endY = state.offsetY / state.scale; // Top

        // Vertical Lines (X-Axis)
        // Determine step size based on zoom
        let step = 1;
        if (state.scale > 100) step = 0.5;
        if (state.scale < 20) step = 5;

        // X Grid
        for (let x = Math.floor(startX/step)*step; x < endX; x += step) {
            let px = state.offsetX + (x * state.scale);
            ctx.beginPath();
            ctx.moveTo(px, 0); ctx.lineTo(px, canvas.height);
            ctx.stroke();
            // Labels
            if (Math.abs(x) > 0.001) ctx.fillText(x.toFixed(1).replace('.0',''), px + 4, state.offsetY + 12);
        }

        // Y Grid
        for (let y = Math.floor(-endY/step)*step; y < -startY; y += step) {
            let py = state.offsetY - (y * state.scale);
            ctx.beginPath();
            ctx.moveTo(0, py); ctx.lineTo(canvas.width, py);
            ctx.stroke();
            // Labels
            if (Math.abs(y) > 0.001) ctx.fillText(y.toFixed(1).replace('.0',''), state.offsetX + 4, py - 4);
        }

        // Axes
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, state.offsetY); ctx.lineTo(canvas.width, state.offsetY); // X Axis
        ctx.moveTo(state.offsetX, 0); ctx.lineTo(state.offsetX, canvas.height); // Y Axis
        ctx.stroke();
    }

    // --- INTERACTION (PAN & ZOOM) ---
    canvas.addEventListener('mousedown', e => {
        state.isDragging = true;
        state.lastMouse = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mouseup', () => state.isDragging = false);

    canvas.addEventListener('mousemove', e => {
        // 1. Pan
        if (state.isDragging) {
            let dx = e.clientX - state.lastMouse.x;
            let dy = e.clientY - state.lastMouse.y;
            state.offsetX += dx;
            state.offsetY += dy;
            state.lastMouse = { x: e.clientX, y: e.clientY };
            draw();
        }

        // 2. Coordinate Tracker
        let rect = canvas.getBoundingClientRect();
        let mx = e.clientX - rect.left;
        let my = e.clientY - rect.top;
        let wx = (mx - state.offsetX) / state.scale;
        let wy = (state.offsetY - my) / state.scale;
        document.getElementById('coord-box').innerText = `x: ${wx.toFixed(2)}, y: ${wy.toFixed(2)}`;
    });

    // Zoom
    function zoom(factor) {
        state.scale *= factor;
        draw();
    }
    
    function resetView() {
        state.scale = 40;
        state.offsetX = canvas.width / 2;
        state.offsetY = canvas.height / 2;
        draw();
    }

    canvas.addEventListener('wheel', e => {
        e.preventDefault();
        zoom(e.deltaY < 0 ? 1.1 : 0.9);
    });

    // Init
    resize();
    parseAndDraw();

</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
