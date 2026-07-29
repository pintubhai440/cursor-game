import streamlit as st

st.set_page_config(page_title="Cursor Dodge Game", page_icon="🎮", layout="centered")

st.title("🎮 Cursor Dodge - Ultimate Edition")
st.write("Aapka Pygame desktop app direct web browser par run nahi ho sakta, isliye yeh raha uska web version jo seedha yahan browser mein chalega!")

# HTML + JavaScript based interactive canvas game for browser
game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {
    background-color: #f0f2f6;
    text-align: center;
    font-family: Arial, sans-serif;
  }
  canvas {
    background: linear-gradient(to bottom, #a8befa, #d7e0fc;
    border: 4px solid #0032c8;
    border-radius: 8px;
    cursor: none;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
  }
  #scoreBoard {
    font-size: 24px;
    font-weight: bold;
    color: #0032c8;
    margin-bottom: 10px;
  }
</style>
</head>
<body>

<div id="scoreBoard">Score: <span id="score">0</span> | Best: <span id="bestScore">0</span></div>
<canvas id="gameCanvas" width="560" height="420"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let score = 0;
let bestScore = 0;
let isGameOver = false;

let player = { x: 280, y: 210, radius: 10 };
let enemies = [
    { x: 100, y: 100, dx: 3, dy: 2, radius: 10 },
    { x: 400, y: 300, dx: -2, dy: 3, radius: 10 }
];

canvas.addEventListener("mousemove", (e) => {
    let rect = canvas.getBoundingClientRect();
    player.x = e.clientX - rect.left;
    player.y = e.clientY - rect.top;
    
    // Keep player inside rails (50px side bars)
    if (player.x < 50 + player.radius) player.x = 50 + player.radius;
    if (player.x > 560 - 50 - player.radius) player.x = 560 - 50 - player.radius;
    if (player.y < player.radius) player.y = player.radius;
    if (player.y > 420 - player.radius) player.y = 420 - player.radius;
});

canvas.addEventListener("click", () => {
    if (isGameOver) {
        score = 0;
        enemies = [
            { x: 100, y: 100, dx: 3, dy: 2, radius: 10 },
            { x: 400, y: 300, dx: -2, dy: 3, radius: 10 }
        ];
        isGameOver = false;
    }
});

function update() {
    if (isGameOver) return;

    score += 1;
    document.getElementById("score").innerText = Math.floor(score / 10);

    // Update enemies
    enemies.forEach(e => {
        e.x += e.dx;
        e.y += e.dy;

        if (e.x - e.radius <= 50 || e.x + e.radius >= 510) e.dx *= -1;
        if (e.y - e.radius <= 0 || e.y + e.radius >= 420) e.dy *= -1;

        // Collision check
        let dist = Math.hypot(player.x - e.x, player.y - e.y);
        if (dist < player.radius + e.radius) {
            isGameOver = true;
            let currentScore = Math.floor(score / 10);
            if (currentScore > bestScore) {
                bestScore = currentScore;
                document.getElementById("bestScore").innerText = bestScore;
            }
        }
    });
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Side Rails
    ctx.fillStyle = "#0032c8";
    ctx.fillRect(0, 0, 50, canvas.height);
    ctx.fillRect(canvas.width - 50, 0, 50, canvas.height);

    // Draw Enemies
    enemies.forEach(e => {
        ctx.beginPath();
        ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
        ctx.fillStyle = "#dc1414";
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "#ffffff";
        ctx.stroke();
        ctx.closePath();
    });

    // Draw Player Cursor
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#000000";
    ctx.stroke();
    ctx.closePath();

    if (isGameOver) {
        ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 30px Arial";
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);
        
        ctx.font = "18px Arial";
        ctx.fillText("Click anywhere to Restart", canvas.width / 2, canvas.height / 2 + 20);
    }
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

loop();
</script>

</body>
</html>
"""

# Render the game component inside Streamlit
st.components.v1.html(game_html, height=500)
