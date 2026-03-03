import pickle
import streamlit as st
import requests
import streamlit.components.v1 as components

st.markdown("""
    <style>
        @keyframes pulse {
            0%   { box-shadow: 0 0 0 0 rgba(247, 37, 133, 0.7); }
            50%  { box-shadow: 0 0 18px 8px rgba(247, 37, 133, 0.3); }
            100% { box-shadow: 0 0 0 0 rgba(247, 37, 133, 0.0); }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes glowTitle {
            0%   { text-shadow: 0 0 10px #fff, 0 0 20px #f72585; }
            50%  { text-shadow: 0 0 20px #fff, 0 0 40px #7209b7, 0 0 60px #f72585; }
            100% { text-shadow: 0 0 10px #fff, 0 0 20px #f72585; }
        }
        @keyframes shimmer {
            0%   { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        @keyframes float {
            0%   { transform: translateY(0px); }
            50%  { transform: translateY(-6px); }
            100% { transform: translateY(0px); }
        }
        @keyframes borderGlow {
            0%   { border-color: rgba(247,37,133,0.4); }
            50%  { border-color: rgba(114,9,183,0.9); }
            100% { border-color: rgba(247,37,133,0.4); }
        }
        @keyframes scanline {
            0%   { transform: translateY(-100%); }
            100% { transform: translateY(100vh); }
        }
        @keyframes bgZoom {
            0%   { transform: scale(1); }
            50%  { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .stApp {
            background: transparent !important;
        }

        /* ── Background image — brightness raised from 0.35 → 0.65 ── */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            background-image: url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1920');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            animation: bgZoom 20s ease-in-out infinite;
            filter: brightness(0.65) saturate(1.3);
            z-index: 0;
        }

        .stApp::after {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 60px;
            background: linear-gradient(transparent, rgba(247,37,133,0.03), transparent);
            animation: scanline 6s linear infinite;
            pointer-events: none;
            z-index: 1;
        }

        /* ── Glass card — opacity lowered from 0.70 → 0.45 so bg shows through ── */
        .block-container {
            background: rgba(10, 5, 30, 0.45) !important;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            animation: fadeInUp 0.8s ease forwards;
            position: relative;
            z-index: 2;
        }

        h1, h2, h3 {
            color: white !important;
            animation: glowTitle 3s ease-in-out infinite;
        }
        .stSelectbox > div > div {
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(224,170,255,0.4) !important;
            border-radius: 12px !important;
            color: white !important;
            animation: borderGlow 3s ease infinite;
        }
        .stButton > button {
            background: linear-gradient(90deg, #f72585, #7209b7, #f72585) !important;
            background-size: 200% auto !important;
            color: white !important;
            border-radius: 25px !important;
            font-weight: 700 !important;
            animation: pulse 1.8s infinite, shimmer 2s linear infinite;
            transition: transform 0.2s ease !important;
        }
        .stButton > button:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 0 30px rgba(247, 37, 133, 0.9) !important;
            animation: none !important;
        }
        img {
            border-radius: 14px !important;
            border: 2px solid rgba(224, 170, 255, 0.35) !important;
            box-shadow: 0 6px 24px rgba(114, 9, 183, 0.5) !important;
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
            animation: float 4s ease-in-out infinite;
        }
        img:hover {
            transform: scale(1.08) translateY(-5px) !important;
            box-shadow: 0 12px 40px rgba(247, 37, 133, 0.7) !important;
            animation: none !important;
        }
        .movie-title {
            color: white;
            font-weight: 600;
            font-size: 0.85rem;
            margin: 8px 0 4px 0;
            animation: fadeInUp 0.6s ease forwards;
        }
        .movie-rating {
            color: #f9c74f;
            font-size: 0.85rem;
            margin-bottom: 4px;
            animation: fadeInUp 0.8s ease forwards;
        }
        .movie-overview {
            color: #ccc;
            font-size: 0.75rem;
            line-height: 1.4;
            animation: fadeInUp 1s ease forwards;
        }
        .stExpander {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(224,170,255,0.2) !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
        }
        .stExpander:hover {
            border-color: rgba(247,37,133,0.5) !important;
            box-shadow: 0 4px 15px rgba(247,37,133,0.2) !important;
        }
        .stExpander p, .stExpander div {
            color: white !important;
        }
        .stSpinner > div {
            border-top-color: #f72585 !important;
        }
    </style>
""", unsafe_allow_html=True)

components.html("""
<canvas id="movie-bg-canvas"></canvas>
<script>
const canvas = document.getElementById('movie-bg-canvas');
const ctx    = canvas.getContext('2d');
function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
resize();
window.addEventListener('resize', resize);
const rand = (a, b) => Math.random() * (b - a) + a;
const EMOJIS = ['🎬','🎥','🍿','⭐','🎞️','🏆','🎭','📽️','💫','✨'];
const particles = Array.from({length: 28}, () => ({
    x: rand(0, window.innerWidth), y: rand(0, window.innerHeight),
    emoji: EMOJIS[Math.floor(rand(0, EMOJIS.length))],
    size: rand(18, 36), speedX: rand(-0.35, 0.35), speedY: rand(-0.5, -0.15),
    opacity: rand(0.15, 0.45), wobble: rand(0, Math.PI * 2), wobbleSpeed: rand(0.01, 0.025)
}));
const stars = Array.from({length: 80}, () => ({
    x: rand(0, window.innerWidth), y: rand(0, window.innerHeight),
    r: rand(0.5, 1.8), twinkle: rand(0, Math.PI * 2), speed: rand(0.02, 0.06)
}));
let filmOffset = 0;
function drawFilmStrip(x) {
    const holeW = 18, holeH = 28, gap = 14, stripW = 36;
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(x, 0, stripW, canvas.height);
    ctx.fillStyle = 'rgba(255,255,255,0.1)';
    let offset = filmOffset % (holeH + gap);
    for (let y = -holeH + offset; y < canvas.height + holeH; y += holeH + gap) {
        ctx.beginPath(); ctx.roundRect(x + (stripW - holeW)/2, y, holeW, holeH, 4); ctx.fill();
    }
}
const shoots = Array.from({length: 4}, () => resetShoot({}));
function resetShoot(s) {
    s.x = rand(0, canvas.width); s.y = rand(0, canvas.height * 0.4);
    s.len = rand(80, 160); s.speed = rand(8, 16);
    s.angle = rand(20, 45) * Math.PI / 180; s.alpha = 1;
    s.active = Math.random() > 0.6; return s;
}
function draw() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    stars.forEach(s => {
        s.twinkle += s.speed;
        const alpha = 0.3 + 0.5 * Math.abs(Math.sin(s.twinkle));
        ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${alpha})`; ctx.fill();
    });
    shoots.forEach(s => {
        if (!s.active) { if (Math.random() < 0.003) s.active = true; return; }
        ctx.save(); ctx.globalAlpha = s.alpha;
        ctx.strokeStyle = `rgba(255,220,255,${s.alpha})`; ctx.lineWidth = 2;
        ctx.shadowBlur = 8; ctx.shadowColor = '#f72585';
        ctx.beginPath(); ctx.moveTo(s.x, s.y);
        ctx.lineTo(s.x + Math.cos(s.angle)*s.len, s.y + Math.sin(s.angle)*s.len);
        ctx.stroke(); ctx.restore();
        s.x += s.speed*Math.cos(s.angle); s.y += s.speed*Math.sin(s.angle);
        s.alpha -= 0.018;
        if (s.alpha <= 0 || s.x > W || s.y > H) resetShoot(s);
    });
    filmOffset += 0.6;
    drawFilmStrip(0); drawFilmStrip(W - 36);
    particles.forEach(p => {
        p.wobble += p.wobbleSpeed;
        p.x += p.speedX + Math.sin(p.wobble) * 0.4; p.y += p.speedY;
        if (p.y < -60) p.y = H + 40;
        if (p.x < -60) p.x = W + 40;
        if (p.x > W+60) p.x = -40;
        ctx.save(); ctx.globalAlpha = p.opacity;
        ctx.font = `${p.size}px serif`; ctx.fillText(p.emoji, p.x, p.y);
        ctx.restore();
    });
    requestAnimationFrame(draw);
}
draw();
</script>
<style>
    #movie-bg-canvas {
        position: fixed; top: 0; left: 0;
        width: 100vw; height: 100vh;
        z-index: 0; pointer-events: none;
    }
</style>
""", height=0)

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

@st.cache_data(show_spinner=False)
def fetch_details(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url).json()
    rating = round(data.get('vote_average', 0), 1)
    overview = data.get('overview', 'No overview available.')
    release = data.get('release_date', 'N/A')[:4]
    genres = ", ".join([g['name'] for g in data.get('genres', [])[:2]])
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return rating, overview, release, genres, full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names,recommended_movie_posters

st.header('Movie Recommender System')
movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)
if st.button('Show Recommendation'):
    with st.spinner('🎬 Finding best matches...'):
        recommended_movie_names,recommended_movie_posters = recommend(selected_movie)
        movie_ids = [movies[movies['title'] == recommended_movie_names[i]].movie_id.values[0] for i in range(5)]
        all_details = [fetch_details(mid) for mid in movie_ids]

    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    for i, col in enumerate(cols):
        with col:
            rating, overview, release, genres, _ = all_details[i]
            st.image(recommended_movie_posters[i])
            st.markdown(f"<div class='movie-title'>🎬 {recommended_movie_names[i]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='movie-rating'>⭐ {rating}/10 &nbsp;|&nbsp; 📅 {release}</div>", unsafe_allow_html=True)
            if genres:
                st.markdown(f"<div class='movie-overview'>🎭 {genres}</div>", unsafe_allow_html=True)
            with st.expander("📖 Overview"):
                st.write(overview)
