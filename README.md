# 🍎 Project Newton: The Hybrid Math Engine
https://graph-tool-1b0a.onrender.com

> "Why do I have to tell the calculator what mode to be in? It should just know."

### 💡 The "Why"
I built Newton because I was frustrated with standard tools. If I open a graphing app and type `2 + 2`, it gives me an error because there is no `x`. If I open a calculator and type `y = x^2`, it gives me a syntax error.

I wanted to build a **Context-Aware Engine**. I wanted a tool that adapts to the user's thought process instantly. If I type algebra, it visualizes. If I type arithmetic, it solves.

### 🛠️ The Logic (The "X-Trigger")
The core innovation is the **Intelligent Parser**.
Instead of forcing the user to click a "Mode" button, the engine analyzes the input string in real-time (every keystroke).
*   **The Rule:** `if (input contains 'x') -> Switch to Graph Mode`
*   **The Result:** The UI transforms instantly. The input border turns **Blue** (Graph) or **Green** (Calc), giving immediate visual feedback.

### ⚡ Key Features
1.  **The "Lazy" Input Sanitizer:**
    *   Problem: Users type `2x` or `(x+1)(x-2)`. Computers hate this; they want `2*x`.
    *   Solution: I wrote a Regex algorithm that auto-injects multiplication signs where humans forget them.
2.  **Asymptote Guard:**
    *   Problem: Plotting `tan(x)` usually creates ugly vertical lines connecting the waves.
    *   Solution: The engine detects "Infinite Jumps" (when Y changes faster than the screen height) and lifts the digital pen, keeping the graph mathematically pure.
3.  **Variable Reactor:**
    *   If you type `m*x + c`, the engine detects `m` and `c` are unknown and automatically generates sliders for them.

### 🚀 How to Run
1.  Clone the repo.
2.  `pip install -r requirements.txt`
3.  `python app.py`

---
*Engineered by [Your Name]*
