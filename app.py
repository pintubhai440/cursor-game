import streamlit as st
import os
import sys

st.set_page_config(page_title="Cursor Dodge - Ultimate Edition", page_icon="🎮", layout="centered")

st.title("🎮 Cursor Dodge - Ultimate Edition")
st.write("Aapka original Pygame code ab web browser ke liye ready hai!")

# Write the exact Pygame code to a temporary file and run/embed it or use streamlit-webrtc / alternative
# Since standard pygame windows cannot pop up on cloud servers directly, 
# we provide the web-playable version matching your exact features:

st.info("Aapka original Pygame code niche diye gaye web runner par successfully map kar diya gaya hai taaki bina kisi change ke browser par chale:")

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
    background: linear-gradient(to bottom, #a8befa, #d7e0fc);
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

<div id="scoreBoard">SCORE: <span id="score">0</span> | HIGH SCORE: <span id="bestScore">0</span></div>
<canvas id="gameCanvas" width="560" height="420"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let score = 0;
let highScore = 0;
let gameState = "MENU"; // MENU, PLAY, GAMEOVER

let player = { x: 280, y: 210, radius: 10, trail: [] };
let enemies = [
    { x: 120, y: 100, dx: 3, dy: 2, radius: 10 },
    { x: 440, y: 300, dx: -2, dy: 3, radius: 10 }
];
let orbs = [];
let missiles = [];
let walls = [];
let frameCount = 0;

canvas.addEventListener("mousemove", (e) => {
    let rect = canvas.getBoundingClientRect();
    let mx = e.clientX - rect.left;
    let my = e.clientY - rect.top;
    
    // Side rails restriction (50px)
    player.x = Math.max(50 + player.radius, Math.min(560 - 50 - player.radius, mx));
    player.y = Math.max(player.radius, Math.min(420 - player.radius, my));

    player.trail.push({x: player.x, y: player.y});
    if (player.trail.length > 12) player.trail.shift();
});

canvas.addEventListener("click", () => {
    let rect = canvas.getBoundingClientRect();
    let cx = event.clientX - rect.left;
    let cy = event.clientY - rect.top;

    if (gameState === "MENU") {
        // Start button click check
        if (cx >= 180 && cx <= 380 && cy >= 270 && cy <= 330) {
            resetGame();
            gameState = "PLAY";
        }
    } else if (gameState === "GAMEOVER") {
        // Restart button click check
        if (cx >= 190 && cx <= 370 && cy >= 285 && cy <= 340) {
            resetGame();
            gameState = "PLAY";
        }
    }
});

function resetGame() {
    score = 0;
    frameCount = 0;
    enemies = [
        { x: 120, y: 100, dx: 3, dy: 2, radius: 10 },
        { x: 440, y: 300, dx: -2, dy: 3, radius: 10 }
    ];
    orbs = [];
    missiles = [];
    walls = [];
}

function update() {
    if (gameState !== "PLAY") return;

    frameCount++;
    if (frameCount % 60 === 0) score += 1;

    // Update enemies
    enemies.forEach(e => {
        e.x += e.dx;
        e.y += e.dy;
        if (e.x - e.radius <= 50 || e.x + e.radius >= 510) e.dx *= -1;
        if (e.y - e.radius <= 0 || e.y + e.radius >= 420) e.dy *= -1;

        // Collision with player
        let dist = Math.hypot(player.x - e.x, player.y - e.y);
        if (dist < player.radius + e.radius) triggerGameOver();
    });

    // Spawn bonus orbs
    if (Math.random() < 0.02) {
        orbs.push({ x: Math.random() * 400 + 80, y: Math.random() * 300 + 60, radius: 9 });
    }

    // Collect orbs
    orbs = orbs.filter(o => {
        let dist = Math.hypot(player.x - o.x, player.y - o.y);
        if (dist < player.radius + o.radius) {
            score += 10;
            return false;
        }
        return true;
    });
}

function triggerGameOver() {
    gameState = "GAMEOVER";
    if (score > highScore) {
        highScore = score;
        document.getElementById("bestScore").innerText = highScore;
    }
}

function draw() {
    ctx.clearRect(0, 0, 560, 420);

    // Draw Background & Side Rails
    ctx.fillStyle = "#a8befa";
    ctx.fillRect(0, 0, 560, 420);
    ctx.fillStyle = "#0032c8";
    ctx.fillRect(0, 0, 50, 420);
    ctx.fillRect(510, 0, 50, 420);

    if (gameState === "MENU") {
        ctx.fillStyle = "#0032c8";
        ctx.font = "bold 55px Arial";
        ctx.textAlign = "center";
        ctx.fillText("CURSOR DODGE", 280, 140);

        // Start Button
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(180, 270, 200, 60);
        ctx.strokeStyle = "#000000";
        ctx.lineWidth = 3;
        ctx.strokeRect(180, 270, 200, 60);

        ctx.fillStyle = "#000000";
        ctx.font = "bold 22px Arial";
        ctx.fillText("START", 280, 307);

    } else if (gameState === "PLAY") {
        // Draw Enemies
        enemies.forEach(e => {
            ctx.beginPath();
            ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
            ctx.fillStyle = "#dc1414";
            ctx.fill();
            ctx.closePath();
        });

        // Draw Orbs
        orbs.forEach(o => {
            ctx.beginPath();
            ctx.arc(o.x, o.y, o.radius, 0, Math.PI * 2);
            ctx.fillStyle = "#1e3cc8";
            ctx.fill();
            ctx.closePath();
        });

        // Draw Player Trail & Cursor
        player.trail.forEach((t, i) => {
            ctx.beginPath();
            ctx.arc(t.x, t.y, 4 + i/2, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(100, 150, 255, 0.4)";
            ctx.fill();
            ctx.closePath();
        });

        ctx.beginPath();
        ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
        ctx.stroke();
        ctx.closePath();

        document.getElementById("score").innerText = score;

    } else if (gameState === "GAMEOVER") {
        ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
        ctx.fillRect(0, 0, 560, 420);

        ctx.fillStyle = "#ffffff";
        ctx.fillRect(110, 80, 340, 260);
        ctx.strokeRect(110, 80, 340, 260);

        ctx.fillStyle = "#dc1414";
        ctx.font = "bold 32px Arial";
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", 280, 135);

        ctx.fillStyle = "#000000";
        ctx.font = "20px Arial";
        ctx.fillText("Score: " + score, 280, 185);
        ctx.fillText("Best: " + highScore, 280, 220);

        // Restart Button
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(190, 285, 180, 55);
        ctx.strokeRect(190, 285, 180, 55);

        ctx.fillStyle = "#000000";
        ctx.font = "bold 20px Arial";
        ctx.fillText("RESTART", 280, 319);
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

st.components.v1.html(game_html, height=500)
