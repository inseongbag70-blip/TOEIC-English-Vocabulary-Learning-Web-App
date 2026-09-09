from flask import Flask, jsonify, render_template_string
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
WORDS_FILE = os.path.join(BASE, "data", "words.json")

with open(WORDS_FILE, encoding="utf-8") as f:
    WORDS = json.load(f)

app = Flask(__name__)

HTML = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TOEIC 5단어</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f6f7fb;color:#172033;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif}.wrap{max-width:980px;margin:auto;padding:18px}.top{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:18px}.brand{font-weight:900;font-size:22px}.nav{display:flex;gap:7px;flex-wrap:wrap}.btn{border:1px solid #dfe3ea;background:#fff;border-radius:12px;padding:10px 14px;font-weight:800;cursor:pointer;text-decoration:none;color:#172033}.primary{background:#2563eb;color:#fff;border-color:#2563eb}.green{background:#059669;color:#fff;border-color:#059669}.red{background:#dc2626;color:#fff;border-color:#dc2626}.hero{background:#111827;color:#fff;border-radius:24px;padding:28px;margin-bottom:16px}.hero h1{margin:0 0 8px;font-size:32px}.hero p{color:#d1d5db;margin:7px 0}.bar{height:10px;background:#374151;border-radius:99px;overflow:hidden;margin:16px 0}.bar>div{height:100%;background:#60a5fa}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:13px}.card{background:#fff;border:1px solid #e5e7eb;border-radius:18px;padding:19px;box-shadow:0 3px 12px #00000009}.num{font-size:13px;color:#9aa2b1}.word{font-size:28px;font-weight:900;letter-spacing:-.5px}.meaning{margin-top:8px;color:#4b5563;line-height:1.7}.actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:16px}.hidden{display:none!important}.muted{color:#6b7280}.quizq{font-size:20px;font-weight:900;margin-bottom:10px}.option{display:block;border:1px solid #e5e7eb;border-radius:12px;padding:12px;margin:8px 0;cursor:pointer}.option:hover{background:#eff6ff;border-color:#93c5fd}.option input{margin-right:8px}.score{font-size:54px;font-weight:950}.notice{padding:12px 14px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:13px;color:#1e3a8a;margin:12px 0}.danger{background:#fef2f2;border-color:#fecaca;color:#991b1b}table{width:100%;border-collapse:collapse}th,td{padding:11px 8px;text-align:left;border-bottom:1px solid #eee}footer{padding:30px 0;color:#9aa2b1;font-size:13px}@media(max-width:600px){.wrap{padding:12px}.hero h1{font-size:27px}.word{font-size:24px}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <a class="brand" href="#" onclick="showHome();return false">🎯 TOEIC 5단어</a>
    <nav class="nav">
      <button class="btn" onclick="showHome()">홈</button>
      <button class="btn" onclick="showWrong()">오답노트 <span id="wrongBadge"></span></button>
    </nav>
  </header>
  <main id="app"></main>
  <footer>TOEIC PDF 단어 데이터 기반 · 학습 진도는 현재 브라우저에 저장됩니다.</footer>
</div>
<script>
const WORDS = __WORDS__;
const KEY='toeic5_progress_v2';
const emptyState=()=>({completed:[],wrong:{},quizzes:0,correct:0,answered:0});
let state=load();
function load(){try{return {...emptyState(),...JSON.parse(localStorage.getItem(KEY)||'{}')}}catch(e){return emptyState()}}
function save(){localStorage.setItem(KEY,JSON.stringify(state));updateBadge()}
function updateBadge(){const el=document.getElementById('wrongBadge');if(el)el.textContent=Object.keys(state.wrong||{}).length?`(${Object.keys(state.wrong).length})`:''}
function groups(){let a=[];for(let i=0;i<WORDS.length;i+=5)a.push(WORDS.slice(i,i+5));return a}
const GS=groups();
function currentGroup(){for(let i=0;i<GS.length;i++)if(!state.completed.includes(i))return i;return Math.max(0,GS.length-1)}
function esc(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
function layout(html){document.getElementById('app').innerHTML=html;updateBadge();window.scrollTo({top:0,behavior:'smooth'})}
function home(){const g=currentGroup(),done=state.completed.length,pct=Math.round(done/GS.length*100),ws=GS[g];layout(`<section class="hero"><h1>하루 5단어, 게임처럼 외우기</h1><p>5개 학습 → 5문제 테스트 → 틀린 단어는 자동 오답노트</p><div class="bar"><div style="width:${pct}%"></div></div><p>${done} / ${GS.length} 세트 완료 · 전체 ${WORDS.length}단어 · 오답 ${Object.keys(state.wrong).length}개</p></section><section class="card"><h2>다음 학습: ${g+1}세트</h2><p class="muted">단어 ${ws[0].number}~${ws[ws.length-1].number}</p><div class="grid">${ws.map(w=>`<div class="card"><div class="num">${w.number}</div><div class="word">${esc(w.word)}</div><div class="meaning">${esc(w.meaning)}</div></div>`).join('')}</div><div class="actions"><button class="btn primary" onclick="showLearn(${g})">5단어 학습 시작 →</button><button class="btn" onclick="showQuiz(${g})">바로 테스트</button></div></section><div class="grid" style="margin-top:13px"><div class="card"><div class="num">누적 테스트</div><div class="word">${state.quizzes}회</div></div><div class="card"><div class="num">정답률</div><div class="word">${state.answered?Math.round(state.correct/state.answered*100):0}%</div></div><div class="card"><div class="num">오답 단어</div><div class="word">${Object.keys(state.wrong).length}개</div></div></div>`)}
function showHome(){home()}
function showLearn(g){const ws=GS[g]||GS[0];layout(`<section class="hero"><h1>${g+1}번째 5단어</h1><p>영어 단어를 먼저 보고 뜻을 떠올린 뒤 뜻을 확인하세요.</p></section><div class="grid">${ws.map(w=>`<div class="card"><div class="num">${w.number}</div><div class="word">${esc(w.word)}</div><details><summary>뜻 보기</summary><div class="meaning">${esc(w.meaning)}</div></details></div>`).join('')}</div><div class="actions"><button class="btn" onclick="showHome()">← 홈</button><button class="btn primary" onclick="showQuiz(${g})">테스트 시작 →</button></div>`)}
function makeOptions(correct){const others=WORDS.filter(x=>x.number!==correct.number);return [correct,...shuffle(others).slice(0,3)].sort(()=>Math.random()-.5)}
function shuffle(a){return [...a].sort(()=>Math.random()-.5)}
function showQuiz(g){const ws=GS[g]||GS[0];const questions=ws.map(w=>({w,opts:makeOptions(w)}));window.currentQuiz={type:'group',g,questions};layout(`<section class="hero"><h1>${g+1}번째 테스트</h1><p>5문제입니다. 각 단어에 맞는 뜻을 고르세요.</p></section><form onsubmit="submitQuiz(event)">${questions.map((q,i)=>`<div class="card" style="margin-bottom:13px"><div class="quizq">${i+1}. ${esc(q.w.word)}</div>${q.opts.map(o=>`<label class="option"><input required type="radio" name="q${i}" value="${o.number}">${esc(o.meaning)}</label>`).join('')}</div>`).join('')}<button class="btn primary" type="submit">채점하기</button></form>`)}
function submitQuiz(e){e.preventDefault();const qs=window.currentQuiz.questions;let score=0,wrong=[];qs.forEach((q,i)=>{const ans=Number(new FormData(e.target).get('q'+i));if(ans===q.w.number)score++;else wrong.push(q.w)});state.quizzes++;state.correct+=score;state.answered+=qs.length;wrong.forEach(w=>{const k=String(w.number);if(!state.wrong[k])state.wrong[k]={...w,wrong_count:0};state.wrong[k].wrong_count++});if(score===5&&!state.completed.includes(window.currentQuiz.g))state.completed.push(window.currentQuiz.g);save();showResult(score,qs.length,wrong)}
function showResult(score,total,wrong){layout(`<section class="hero"><div class="num">테스트 결과</div><div class="score">${score} / ${total}</div><p>${score===total?'완벽합니다! 다음 세트로 넘어가세요 🎉':`${wrong.length}개가 오답노트에 추가되었습니다.`}</p></section>${wrong.length?`<section class="card"><h2>이번 테스트 오답</h2><table><tr><th>No.</th><th>단어</th><th>뜻</th></tr>${wrong.map(w=>`<tr><td>${w.number}</td><td><b>${esc(w.word)}</b></td><td>${esc(w.meaning)}</td></tr>`).join('')}</table></section>`:''}<div class="actions"><button class="btn" onclick="showHome()">홈으로</button><button class="btn red" onclick="showWrong()">오답노트</button><button class="btn primary" onclick="showLearn(${currentGroup()})">다음 학습 →</button></div>`)}
function showWrong(){const vals=Object.values(state.wrong).sort((a,b)=>a.number-b.number);if(!vals.length){layout(`<section class="hero"><h1>오답노트</h1><p>아직 틀린 단어가 없습니다.</p></section><button class="btn primary" onclick="showHome()">학습하러 가기</button>`);return}layout(`<section class="hero"><h1>오답노트</h1><p>총 ${vals.length}개 단어</p></section><section class="card"><table><tr><th>No.</th><th>단어</th><th>뜻</th><th>오답</th></tr>${vals.map(x=>`<tr><td>${x.number}</td><td><b>${esc(x.word)}</b></td><td>${esc(x.meaning)}</td><td>${x.wrong_count}회</td></tr>`).join('')}</table><div class="actions"><button class="btn primary" onclick="showWrongQuiz()">오답만 다시 테스트</button><button class="btn red" onclick="clearWrong()">오답노트 비우기</button></div></section>`)}
function showWrongQuiz(){const vals=Object.values(state.wrong);if(!vals.length)return showWrong();const ws=shuffle(vals).slice(0,5);const questions=ws.map(w=>({w,opts:makeOptions(w)}));window.currentQuiz={type:'wrong',questions};layout(`<section class="hero"><h1>오답 복습 테스트</h1><p>오답노트에서 최대 5개를 출제합니다.</p></section><form onsubmit="submitWrong(event)">${questions.map((q,i)=>`<div class="card" style="margin-bottom:13px"><div class="quizq">${i+1}. ${esc(q.w.word)}</div>${q.opts.map(o=>`<label class="option"><input required type="radio" name="q${i}" value="${o.number}">${esc(o.meaning)}</label>`).join('')}</div>`).join('')}<button class="btn primary">채점하기</button></form>`)}
function submitWrong(e){e.preventDefault();const qs=window.currentQuiz.questions;const fd=new FormData(e.target);let score=0;qs.forEach((q,i)=>{const ans=Number(fd.get('q'+i));if(ans===q.w.number)score++;else if(state.wrong[String(q.w.number)])state.wrong[String(q.w.number)].wrong_count++});state.quizzes++;state.correct+=score;state.answered+=qs.length;save();layout(`<section class="hero"><div class="score">${score} / ${qs.length}</div><p>오답 복습 테스트가 끝났습니다.</p></section><div class="actions"><button class="btn red" onclick="showWrong()">오답노트</button><button class="btn primary" onclick="showWrongQuiz()">다시 테스트</button><button class="btn" onclick="showHome()">홈</button></div>`)}
function clearWrong(){if(confirm('오답노트를 모두 삭제할까요?')){state.wrong={};save();showWrong()}}
showHome();
</script>
</body></html>'''

@app.get("/")
def index():
    return render_template_string(HTML.replace("__WORDS__", json.dumps(WORDS, ensure_ascii=False)))

@app.get("/health")
def health():
    return jsonify(status="ok", words=len(WORDS))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
