from flask import Flask, render_template_string

app = Flask(__name__)

# --- NEWTON v6: HYBRID CALCULATOR & GRAPHER ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newton v6 | Hybrid Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.8.0/math.js"></script>
    <style>
        :root { --bg: #ffffff; --panel: #f3f4f6; --accent: #2563eb; --text: #1f2937; --border: #e5e7eb; }
        body { margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; display: flex; height: 100vh; overflow: hidden; }
        
        /* SIDEBAR */
        .sidebar { width: 360px; background: var(--panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 15px; z-index: 10; box-shadow: 4px 0 15px rgba(0,0,0,0.05); }
        
        /* RESULT DISPLAY (New Feature) */
        .display-box {
            background: white; border: 1px solid var(--border); border-radius: 8px; padding: 15px;
            margin-bottom: 15px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
        }
        .input-row { display: flex; align-items: center; margin-bottom: 5px; }
        .fn-label { font-family: 'JetBrains Mono'; font-weight: bold; color: #9ca3af; margin-right: 10px; font-size: 14px; }
        input[type="text"] {
            width: 100%; border: none; outline: none; font-family: 'JetBrains Mono'; font-size: 18px; background: transparent; color: #333;
        }
        .result-row { text-align: right; font-family: 'JetBrains Mono'; font-size: 24px; font-weight: bold; color: var(--accent); height: 30px; overflow: hidden; }
        .mode-badge { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #6b7280; font-weight: 600; }

        /* KEYPAD GRID */
        .keypad { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin-bottom: 15px; }
        .btn {
            background: white; border: 1px solid #d1d5db; border-radius: 6px; padding: 12px 0;
            font-family: 'Inter'; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer;
            transition: 0.1s; user-select: none;
        }
        .btn:active { background: var(--accent); color: white; border-color: var(--accent); transform: translateY(1px); }
        .btn.dark { background: #e5e7eb; }
        .btn.blue { color: var(--accent); font-weight: 800; }
        .btn.wide { grid-column: span 2; background: var(--accent); color: white; border-color: var(--accent); }

        /* VARIABLES */
        #var-list { flex: 1; overflow-y: auto; border-top: 1px solid var(--border); padding-top: 10px; }
        .var-row { display: flex; align-items: center; margin-bottom: 10px; font-size: 13px; font-family: 'JetBrains Mono'; }
        .var-name { width: 25px; color: var(--accent); font-weight: bold; }
        input[type="range"] { flex: 1; margin: 0 10px; accent-color: var(--accent); cursor: pointer; }
        
        /* MAIN CANVAS */
        .viewport { flex: 1; position: relative; cursor: crosshair; background: #fff; }
        canvas { display: block; width: 100%; height: 100%; }
        .hud { position: absolute; bottom: 20px; left: 20px; background: rgba(255,255,255,0.9); padding: 6px 10px; border-radius: 6px; border: 1px solid #ccc; font-family: 'JetBrains Mono'; font-size: 11px; pointer-events: none; }
        .reset-btn { position: absolute; top: 20px; right: 20px; padding: 8px 12px; background: white; border: 1px solid #ccc; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; }
    </style>
</head>
<body>

<div class="sidebar">
    <!-- CALCULATOR SCREEN -->
    <div class="display-box">
        <div class="input-row">
            <span class="fn-label">f =</span>
            <input type="text" id="input" value="tan(pi/3)" spellcheck="false" autocomplete="off">
        </div>
        <div class="result-row" id="result">1.732...</div>
        <div class="mode-badge" id="mode">CALCULATOR MODE</div>
    </div>

    <!-- SCIENTIFIC KEYPAD -->
    <div class="keypad">
        <button class="btn blue" onclick="ins('sin(')">sin</button>
        <button class="btn blue" onclick="ins('cos(')">cos</button>
        <button class="btn blue" onclick="ins('tan(')">tan</button>
        <button class="btn" onclick="ins('pi')">π</button>
        <button class="btn" onclick="ins('e')">e</button>

        <button class="btn" onclick="ins('^')">^</button>
        <button class="btn" onclick="ins('sqrt(')">√</button>
        <button class="btn" onclick="ins('(')">(</button>
        <button class="btn" onclick="ins(')')">)</button>
        <button class="btn dark" onclick="bs()">⌫</button>

        <button class="btn" onclick="ins('7')">7</button>
        <button class="btn" onclick="ins('8')">8</button>
        <button class="btn" onclick="ins('9')">9</button>
        <button class="btn dark" onclick="ins('/')">÷</button>
        <button class="btn dark" onclick="ins('*')">×</button>

        <button class="btn" onclick="ins('4')">4</button>
        <button class="btn" onclick="ins('5')">5</button>
        <button class="btn" onclick="ins('6')">6</button>
        <button class="btn dark" onclick="ins('-')">−</button>
        <button class="btn dark" onclick="ins('+')">+</button>

        <button class="btn" onclick="ins('1')">1</button>
        <button class="btn" onclick="ins('2')">2</button>
        <button class="btn" onclick="ins('3')">3</button>
        <button class="btn wide" onclick="render()">ENTER</button>

        <button class="btn" onclick="ins('0')">0</button>
        <button class="btn" onclick="ins('.')">.</button>
        <button class="btn blue" onclick="ins('x')">x</button>
    </div>

    <div id="var-list"></div>
</div>

<div class="viewport">
    <canvas id="canvas"></canvas>
    <div class="hud" id="coords">x: 0.00, y: 0.00</div>
    <button class="reset-btn" onclick="resetView()">⌖ Center Graph</button>
</div>

<script>
    const cvs = document.getElementById('canvas');
    const ctx = cvs.getContext('2d');
    const inp = document.getElementById('input');
    const resDisplay = document.getElementById('result');
    const modeDisplay = document.getElementById('mode');
    const varList = document.getElementById('var-list');

    let state = {
        scale: 40,
        cx: 0, cy: 0, // Center in pixels
        offX: 0, offY: 0, // Pan offset
        vars: { m:1, c:0 },
        drag: false, lx:0, ly:0
    };

    // --- 1. HYBRID LOGIC (Graph vs Calc) ---
    function render() {
        let raw = inp.value.trim();
        if(!raw) return;

        // Sanitize
        let clean = raw.replace('π', 'pi'); // Allow symbol pasting
        clean = clean.replace(/(\d|\))(?=[a-z]|\()/gi, '$1*'); // 2x -> 2*x
        clean = clean.replace(/\b([a-z])x\b/gi, '$1*x'); // mx -> m*x

        try {
            const node = math.parse(clean);
            const code = node.compile();
            
            // DETECT MODE: Does it have 'x' or unknown variables?
            // We treat 'x' specifically as the graphing variable.
            let symbols = new Set();
            node.traverse(n => {
                if (n.isSymbolNode && !math[n.name]) symbols.add(n.name);
            });

            // Update Sliders
            updateSliders(symbols);

            if (symbols.has('x')) {
                // GRAPH MODE
                modeDisplay.innerText = "GRAPHING MODE";
                modeDisplay.style.color = "#2563eb";
                resDisplay.innerText = "f(x)";
                drawGraph(code);
            } else {
                // CALCULATOR MODE
                modeDisplay.innerText = "CALCULATOR MODE";
                modeDisplay.style.color = "#16a34a";
                
                // Evaluate logic
                let scope = { ...state.vars };
                // pi and e are handled by mathjs automatically
                let val = code.evaluate(scope);
                
                // Format Output
                let out = parseFloat(val.toFixed(8)); // Precision
                if (Math.abs(val) > 1e10) out = "Infinity";
                resDisplay.innerText = "= " + out;
                
                // Clear Canvas for Calc Mode
                ctx.fillStyle = "#fff";
                ctx.fillRect(0,0,cvs.width,cvs.height);
                drawGrid(true); // Draw faint grid
            }

        } catch (e) {
            resDisplay.innerText = "Error";
            modeDisplay.innerText = "SYNTAX ERROR";
            modeDisplay.style.color = "#dc2626";
        }
    }

    // --- 2. GRAPHING ENGINE ---
    function drawGraph(func) {
        ctx.fillStyle = "#fff";
        ctx.fillRect(0,0,cvs.width,cvs.height);
        drawGrid(false);

        ctx.beginPath();
        ctx.strokeStyle = "#2563eb";
        ctx.lineWidth = 2.5;
        
        let w = cvs.width, h = cvs.height;
        let scope = { ...state.vars };
        let prevY = NaN;
        let started = false;

        for(let px=0; px<=w; px++) {
            let x = (px - state.cx - state.offX) / state.scale;
            scope.x = x;
            try {
                let y = func.evaluate(scope);
                let py = state.cy + state.offY - (y * state.scale);

                if(!isFinite(py)) { started=false; prevY=NaN; continue; }

                // Asymptote Check
                if(started && Math.abs(py - prevY) > h) {
                    ctx.moveTo(px, py);
                } else if(!started) {
                    ctx.moveTo(px, py);
                    started=true;
                } else {
                    ctx.lineTo(px, py);
                }
                prevY = py;
            } catch(e) { started=false; prevY=NaN; }
        }
        ctx.stroke();
    }

    function drawGrid(faint) {
        ctx.lineWidth = 1;
        ctx.font = "10px JetBrains Mono";
        ctx.fillStyle = "#999";
        let w=cvs.width, h=cvs.height;
        let step = state.scale > 80 ? 0.5 : (state.scale < 30 ? 5 : 1);

        let sx = Math.floor((-state.cx - state.offX)/state.scale);
        let ex = Math.ceil((w - state.cx - state.offX)/state.scale);
        let sy = Math.floor((state.cy + state.offY - h)/state.scale);
        let ey = Math.ceil((state.cy + state.offY)/state.scale);

        ctx.beginPath();
        for(let x=sx; x<=ex; x++) {
            if(x%step!==0) continue;
            let px = state.cx + state.offX + x*state.scale;
            ctx.strokeStyle = (x===0) ? "#000" : (faint ? "#f3f4f6" : "#e5e7eb");
            ctx.moveTo(px,0); ctx.lineTo(px,h);
            if(!faint && x!==0) ctx.fillText(x, px+2, state.cy+state.offY+12);
        }
        for(let y=sy; y<=ey; y++) {
            if(y%step!==0) continue;
            let py = state.cy + state.offY - y*state.scale;
            ctx.strokeStyle = (y===0) ? "#000" : (faint ? "#f3f4f6" : "#e5e7eb");
            ctx.moveTo(0,py); ctx.lineTo(w,py);
            if(!faint && y!==0) ctx.fillText(y, state.cx+state.offX+4, py-2);
        }
        ctx.stroke();
    }

    // --- 3. UI HELPERS ---
    function updateSliders(symbols) {
        let active = Array.from(symbols).filter(s => s !== 'x' && s !== 'pi' && s !== 'e').sort();
        let current = Object.keys(state.vars);
        
        if(JSON.stringify(active) !== JSON.stringify(current.filter(k => active.includes(k)).sort())) {
            varList.innerHTML = '';
            active.forEach(v => {
                if(state.vars[v]===undefined) state.vars[v]=1;
                let div = document.createElement('div');
                div.className = 'var-row';
                div.innerHTML = `
                    <span class="var-name">${v}</span>
                    <input type="range" min="-10" max="10" step="0.1" value="${state.vars[v]}" oninput="setVar('${v}', this.value)">
                    <span>${state.vars[v]}</span>
                `;
                varList.appendChild(div);
            });
        }
    }
    window.setVar = (k,v) => { state.vars[k]=parseFloat(v); render(); };

    // Keypad Logic
    window.ins = (txt) => {
        let p = inp.selectionStart;
        inp.value = inp.value.slice(0,p) + txt + inp.value.slice(inp.selectionEnd);
        inp.focus();
        inp.setSelectionRange(p+txt.length, p+txt.length);
        render();
    };
    window.bs = () => {
        let p = inp.selectionStart;
        if(p>0) {
            inp.value = inp.value.slice(0,p-1) + inp.value.slice(p);
            inp.focus();
            inp.setSelectionRange(p-1, p-1);
            render();
        }
    };

    // --- 4. EVENTS ---
    function resize() {
        cvs.width = cvs.parentElement.clientWidth;
        cvs.height = cvs.parentElement.clientHeight;
        state.cx = cvs.width/2; state.cy = cvs.height/2;
        render();
    }
    window.onload = resize;
    window.onresize = resize;
    inp.addEventListener('input', render);

    cvs.addEventListener('mousedown', e=>{state.drag=true; state.lx=e.clientX; state.ly=e.clientY;});
    window.addEventListener('mouseup', ()=>state.drag=false);
    window.addEventListener('mousemove', e=>{
        if(state.drag) {
            state.offX += e.clientX-state.lx; state.offY += e.clientY-state.ly;
            state.lx=e.clientX; state.ly=e.clientY;
            render();
        }
        let mx = (e.clientX - cvs.getBoundingClientRect().left - state.cx - state.offX)/state.scale;
        let my = (state.cy + state.offY - (e.clientY - cvs.getBoundingClientRect().top))/state.scale;
        document.getElementById('coords').innerText = `x:${mx.toFixed(2)}, y:${my.toFixed(2)}`;
    });
    cvs.addEventListener('wheel', e=>{
        e.preventDefault();
        state.scale *= e.deltaY<0 ? 1.1 : 0.9;
        render();
    }, {passive:false});
    window.resetView = () => { state.scale=40; state.offX=0; state.offY=0; render(); };

</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
