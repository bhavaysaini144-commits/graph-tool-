from flask import Flask, render_template_string

app = Flask(__name__)

# --- NEWTON v7: THE UNBREAKABLE ENGINE ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newton v7 | Final Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/11.8.0/math.js"></script>
    <style>
        :root { --bg: #ffffff; --panel: #f8f9fa; --accent: #2563eb; --calc: #16a34a; --text: #1f2937; --border: #e5e7eb; }
        body { margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; display: flex; height: 100vh; overflow: hidden; }
        
        /* SIDEBAR LAYOUT */
        .sidebar { width: 360px; background: var(--panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 15px; z-index: 20; box-shadow: 5px 0 15px rgba(0,0,0,0.05); }
        
        /* DYNAMIC INPUT HEADER */
        .header-card {
            background: white; border: 2px solid var(--border); border-radius: 8px; padding: 15px;
            margin-bottom: 15px; transition: 0.3s; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .header-card.graph-mode { border-color: var(--accent); }
        .header-card.calc-mode { border-color: var(--calc); }
        
        .mode-label { font-size: 10px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; display: block; }
        
        .input-row { display: flex; align-items: center; }
        .fn-label { font-family: 'JetBrains Mono'; font-weight: bold; color: #9ca3af; margin-right: 8px; font-size: 16px; }
        input[type="text"] {
            width: 100%; border: none; outline: none; font-family: 'JetBrains Mono'; font-size: 20px; background: transparent; color: #111;
        }
        
        /* CALCULATOR RESULT OVERLAY */
        .result-row { 
            text-align: right; font-family: 'JetBrains Mono'; font-size: 28px; font-weight: bold; 
            color: var(--calc); margin-top: 10px; border-top: 1px solid #eee; padding-top: 5px;
            display: none; /* Hidden by default */
        }
        .header-card.calc-mode .result-row { display: block; }

        /* KEYPAD */
        .keypad { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin-bottom: 10px; }
        .btn {
            background: white; border: 1px solid #d1d5db; border-radius: 6px; padding: 12px 0;
            font-family: 'Inter'; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer;
            transition: 0.1s; user-select: none; display: grid; place-items: center;
        }
        .btn:active { transform: translateY(2px); }
        .btn.blue { color: var(--accent); border-color: var(--accent); background: #eff6ff; }
        .btn.dark { background: #f3f4f6; color: #111; }
        .btn.x-btn { background: var(--accent); color: white; font-weight: 800; font-size: 16px; grid-column: span 2; }

        /* VARIABLES */
        #var-list { flex: 1; overflow-y: auto; border-top: 1px solid var(--border); padding-top: 10px; }
        .var-row { display: flex; align-items: center; margin-bottom: 10px; font-size: 12px; font-family: 'JetBrains Mono'; }
        .var-name { width: 20px; color: var(--accent); font-weight: bold; }
        input[type="range"] { flex: 1; margin: 0 10px; accent-color: var(--accent); cursor: pointer; }

        /* CANVAS */
        .viewport { flex: 1; position: relative; cursor: crosshair; background: #fff; }
        canvas { display: block; width: 100%; height: 100%; }
        
        /* HUD */
        .hud { position: absolute; bottom: 15px; left: 15px; background: rgba(255,255,255,0.95); padding: 5px 10px; border-radius: 5px; border: 1px solid #ccc; font-family: 'JetBrains Mono'; font-size: 11px; pointer-events: none; }
        .reset { position: absolute; top: 15px; right: 15px; padding: 8px 12px; background: white; border: 1px solid #ccc; border-radius: 5px; cursor: pointer; font-weight: 600; font-size: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }

    </style>
</head>
<body>

<div class="sidebar">
    <!-- HEADER CARD -->
    <div class="header-card graph-mode" id="card">
        <span class="mode-label" id="mode-text" style="color: var(--accent);">GRAPHING MODE</span>
        <div class="input-row">
            <span class="fn-label">y =</span>
            <input type="text" id="input" value="x^2 - 2" spellcheck="false" autocomplete="off">
        </div>
        <div class="result-row" id="calc-res">= 0</div>
    </div>

    <!-- KEYPAD -->
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
        <button class="btn x-btn" onclick="ins('x')">VARIABLE X</button>
        
        <button class="btn" onclick="ins('0')">0</button>
        <button class="btn" onclick="ins('.')">.</button>
        <button class="btn" onclick="ins(',')">,</button>
    </div>

    <div id="var-list"></div>
</div>

<div class="viewport">
    <canvas id="canvas"></canvas>
    <div class="hud" id="coords">x: 0.00, y: 0.00</div>
    <button class="reset" onclick="resetView()">⌖ Recenter</button>
</div>

<script>
    // --- CORE ENGINE ---
    const cvs = document.getElementById('canvas');
    const ctx = cvs.getContext('2d');
    const inp = document.getElementById('input');
    const card = document.getElementById('card');
    const modeTxt = document.getElementById('mode-text');
    const resTxt = document.getElementById('calc-res');
    
    let state = { scale: 40, cx: 0, cy: 0, offX: 0, offY: 0, vars: {}, drag: false, lx:0, ly:0 };

    // --- 1. THE UNBREAKABLE PARSER ---
    function process() {
        let raw = inp.value;
        if(!raw) return;

        // Clean Input
        let clean = raw.replace('π', 'pi').replace(' ', '');
        // Fix implicit mult: 2x -> 2*x, x( -> x*(
        clean = clean.replace(/(\d|\)|x)(?=[a-z]|\(|x)/gi, '$1*');
        
        // --- THE SWITCH ---
        // If input has 'x', it is a GRAPH. No exceptions.
        const isGraph = /x/i.test(clean);

        if (isGraph) {
            setMode('graph');
            try {
                const node = math.parse(clean);
                const code = node.compile();
                updateSliders(node);
                drawGraph(code);
            } catch(e) {
                modeTxt.innerText = "SYNTAX ERROR";
                modeTxt.style.color = "#dc2626";
            }
        } else {
            setMode('calc');
            try {
                // Calc Mode
                ctx.clearRect(0,0,cvs.width,cvs.height);
                drawGrid(true); // Faint grid
                
                const val = math.evaluate(clean);
                
                // Format
                let out = parseFloat(val.toFixed(8));
                if (!isFinite(val)) out = "Undefined"; // Catch tan(pi/2)
                resTxt.innerText = "= " + out;
                
            } catch(e) {
                resTxt.innerText = "Error";
            }
        }
    }

    function setMode(mode) {
        if (mode === 'graph') {
            card.className = "header-card graph-mode";
            modeTxt.innerText = "GRAPHING MODE";
            modeTxt.style.color = "#2563eb";
            document.getElementById('var-list').style.display = 'block';
        } else {
            card.className = "header-card calc-mode";
            modeTxt.innerText = "CALCULATOR MODE";
            modeTxt.style.color = "#16a34a";
            document.getElementById('var-list').style.display = 'none';
        }
    }

    // --- 2. GRAPH RENDERER ---
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

                if(started && Math.abs(py - prevY) > h) {
                    ctx.moveTo(px, py); // Asymptote Cut
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

        ctx.beginPath();
        for(let x=sx; x<=ex; x++) {
            if(Math.abs(x % step) > 0.01) continue;
            let px = state.cx + state.offX + x*state.scale;
            ctx.strokeStyle = (x===0) ? "#000" : (faint?"#f0f0f0":"#e5e7eb");
            ctx.moveTo(px,0); ctx.lineTo(px,h);
            if(!faint && x!==0) ctx.fillText(parseFloat(x.toFixed(1)), px+2, state.cy+state.offY+12);
        }
        // Y Axis and Horizontals would go here similarly...
        let sy = Math.floor((state.cy + state.offY - h)/state.scale);
        let ey = Math.ceil((state.cy + state.offY)/state.scale);
        for(let y=sy; y<=ey; y++) {
            if(Math.abs(y % step) > 0.01) continue;
            let py = state.cy + state.offY - y*state.scale;
            ctx.strokeStyle = (y===0) ? "#000" : (faint?"#f0f0f0":"#e5e7eb");
            ctx.moveTo(0,py); ctx.lineTo(w,py);
            if(!faint && y!==0) ctx.fillText(parseFloat(y.toFixed(1)), state.cx+state.offX+4, py-2);
        }
        ctx.stroke();
    }

    // --- 3. UI HELPERS ---
    function updateSliders(node) {
        let found = new Set();
        node.traverse(n => {
            if (n.isSymbolNode && !['x','pi','e'].includes(n.name) && !math[n.name]) found.add(n.name);
        });
        
        const list = document.getElementById('var-list');
        let needsUpdate = false;
        let arr = Array.from(found).sort();
        
        // Simple sync check
        if (arr.length !== list.childElementCount) needsUpdate = true;
        
        if (needsUpdate) {
            list.innerHTML = '';
            arr.forEach(v => {
                if(!state.vars[v]) state.vars[v]=1;
                let div = document.createElement('div');
                div.className = 'var-row';
                div.innerHTML = `
                    <span class="var-name">${v}</span>
                    <input type="range" min="-5" max="5" step="0.1" value="${state.vars[v]}" oninput="state.vars['${v}']=parseFloat(this.value); process()">
                `;
                list.appendChild(div);
            });
        }
    }

    // Input Tools
    window.ins = (t) => { 
        let p = inp.selectionStart; 
        inp.value = inp.value.slice(0,p)+t+inp.value.slice(inp.selectionEnd); 
        inp.focus(); inp.setSelectionRange(p+t.length, p+t.length);
        process(); 
    };
    window.bs = () => { 
        let p = inp.selectionStart;
        if(p>0) { inp.value = inp.value.slice(0,p-1)+inp.value.slice(p); inp.focus(); inp.setSelectionRange(p-1, p-1); process(); }
    };

    // Init
    function resize() { cvs.width=cvs.parentElement.clientWidth; cvs.height=cvs.parentElement.clientHeight; state.cx=cvs.width/2; state.cy=cvs.height/2; process(); }
    window.onload = resize; window.onresize = resize;
    inp.addEventListener('input', process);
    
    // Nav
    cvs.addEventListener('mousedown', e=>{state.drag=true; state.lx=e.clientX; state.ly=e.clientY;});
    window.addEventListener('mouseup', ()=>state.drag=false);
    window.addEventListener('mousemove', e=>{
        if(state.drag) { state.offX += e.clientX-state.lx; state.offY += e.clientY-state.ly; state.lx=e.clientX; state.ly=e.clientY; process(); }
        let mx = (e.clientX - cvs.getBoundingClientRect().left - state.cx - state.offX)/state.scale;
        let my = (state.cy + state.offY - (e.clientY - cvs.getBoundingClientRect().top))/state.scale;
        document.getElementById('coords').innerText = `x:${mx.toFixed(2)}, y:${my.toFixed(2)}`;
    });
    cvs.addEventListener('wheel', e=>{ e.preventDefault(); state.scale *= e.deltaY<0?1.1:0.9; process(); }, {passive:false});
    window.resetView = () => { state.scale=40; state.offX=0; state.offY=0; process(); };

</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(debug=True, port=8080)

