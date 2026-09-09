from flask import Flask, jsonify, render_template_string, request
import json
import os
import urllib.parse
import urllib.request
import re

BASE = os.path.dirname(os.path.abspath(__file__))
WORDS_FILE = os.path.join(BASE, "data", "words.json")

with open(WORDS_FILE, encoding="utf-8") as f:
    WORDS = json.load(f)

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "words": len(WORDS)})

@app.post("/translate")
def translate():
    """Translate Korean UI/meanings into Simplified Chinese.
    Uses Google Translate's public web endpoint server-side so browsers do not need CORS access.
    """
    data = request.get_json(silent=True) or {}
    texts = data.get("texts") or []
    if not isinstance(texts, list):
        return jsonify({"translations":[]}), 400
    out = []
    for text in texts[:100]:
        text = str(text)
        if not text.strip() or not re.search(r"[가-힣]", text):
            out.append(text)
            continue
        try:
            q = urllib.parse.quote(text)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ko&tl=zh-CN&dt=t&q={q}"
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            translated = "".join(x[0] for x in raw[0] if x and x[0])
            out.append(translated or text)
        except Exception:
            out.append(text)
    return jsonify({"translations": out})

HTML = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TOEIC 5단어</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f6f7fb;color:#172033;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif}.wrap{max-width:980px;margin:auto;padding:18px}.top{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:18px}.brand{font-weight:900;font-size:22px;color:#172033;text-decoration:none}.nav{display:flex;gap:7px;flex-wrap:wrap}.btn{border:1px solid #dfe3ea;background:#fff;border-radius:12px;padding:10px 14px;font-weight:800;cursor:pointer;text-decoration:none;color:#172033}.btn:disabled{opacity:.55;cursor:not-allowed}.primary{background:#2563eb;color:#fff;border-color:#2563eb}.green{background:#059669;color:#fff;border-color:#059669}.red{background:#dc2626;color:#fff;border-color:#dc2626}.dark{background:#111827;color:#fff;border-color:#111827}.hero{background:#111827;color:#fff;border-radius:24px;padding:28px;margin-bottom:16px}.hero h1{margin:0 0 8px;font-size:32px}.hero p{color:#d1d5db;margin:7px 0}.bar{height:10px;background:#374151;border-radius:99px;overflow:hidden;margin:16px 0}.bar>div{height:100%;background:#60a5fa}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:13px}.card{background:#fff;border:1px solid #e5e7eb;border-radius:18px;padding:19px;box-shadow:0 3px 12px #00000009}.num{font-size:13px;color:#9aa2b1}.word{font-size:28px;font-weight:900;letter-spacing:-.5px}.meaning{margin-top:8px;color:#4b5563;line-height:1.7}.actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:16px}.hidden{display:none!important}.muted{color:#6b7280}.quizq{font-size:20px;font-weight:900;margin-bottom:10px}.option{display:block;border:1px solid #e5e7eb;border-radius:12px;padding:12px;margin:8px 0;cursor:pointer}.option:hover{background:#eff6ff;border-color:#93c5fd}.option input{margin-right:8px}.score{font-size:54px;font-weight:950}.notice{padding:12px 14px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:13px;color:#1e3a8a;margin:12px 0}.danger{background:#fef2f2;border-color:#fecaca;color:#991b1b}table{width:100%;border-collapse:collapse}th,td{padding:11px 8px;text-align:left;border-bottom:1px solid #eee}.mode-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:15px 0}.mode{border:2px solid #e5e7eb;background:#fff;border-radius:18px;padding:18px;text-align:left;cursor:pointer}.mode.active{border-color:#2563eb;background:#eff6ff}.mode h3{margin:0 0 5px}.mode p{margin:0;color:#6b7280;line-height:1.5}.type-pill{display:inline-block;padding:5px 9px;border-radius:999px;background:#eef2ff;color:#3730a3;font-size:12px;font-weight:800;margin-bottom:10px}.input-answer{width:100%;font-size:20px;padding:14px;border:2px solid #dfe3ea;border-radius:13px;outline:none}.input-answer:focus{border-color:#2563eb}.small{font-size:13px}.speaker{margin-left:8px;padding:6px 9px;border-radius:10px;border:1px solid #dfe3ea;background:#fff;cursor:pointer}.review-list{display:flex;gap:8px;flex-wrap:wrap}.review-chip{padding:9px 12px;border:1px solid #dfe3ea;background:#fff;border-radius:12px;cursor:pointer;font-weight:700}footer{padding:30px 0;color:#9aa2b1;font-size:13px}@media(max-width:600px){.wrap{padding:12px}.hero h1{font-size:27px}.word{font-size:24px}.mode-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <a class="brand" href="#" onclick="showHome();return false">🎯 TOEIC 5단어</a>
    <nav class="nav">
      <button class="btn" onclick="showHome()">홈</button>
      <button class="btn" onclick="showWrong()">오답노트 <span id="wrongBadge"></span></button>
      <button class="btn" id="langBtn" onclick="toggleLanguage()">🇨🇳 中文</button>
    </nav>
  </header>
  <main id="app"></main>
  <footer>TOEIC PDF 단어 데이터 기반 · 학습 진도와 오답노트는 현재 브라우저에 저장됩니다.</footer>
</div>
<script>
const WORDS = __WORDS__;
const KEY='toeic5_progress_v3';
const LANG_KEY='toeic5_language_v1';
let language=localStorage.getItem(LANG_KEY)||'ko';
let translationCache=JSON.parse(localStorage.getItem('toeic5_zh_cache_v1')||'{}');
const emptyState=()=>({completed:[],wrong:{},quizzes:0,correct:0,answered:0,level:1});
let state=load();
function load(){try{return {...emptyState(),...JSON.parse(localStorage.getItem(KEY)||'{}')}}catch(e){return emptyState()}}
function save(){localStorage.setItem(KEY,JSON.stringify(state));updateBadge()}
function updateBadge(){const el=document.getElementById('wrongBadge');if(el)el.textContent=Object.keys(state.wrong||{}).length?`(${Object.keys(state.wrong).length})`:''}
function groups(){let a=[];for(let i=0;i<WORDS.length;i+=5)a.push(WORDS.slice(i,i+5));return a}
const GS=groups();
function currentGroup(){for(let i=0;i<GS.length;i++)if(!state.completed.includes(i))return i;return Math.max(0,GS.length-1)}
function esc(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
function layout(html){document.getElementById('app').innerHTML=html;updateBadge();updateLangButton();window.scrollTo({top:0,behavior:'smooth'});if(language==='zh')translateVisibleToChinese()}
function updateLangButton(){const b=document.getElementById('langBtn');if(b)b.textContent=language==='ko'?'🇨🇳 中文':'🇰🇷 한국어'}
function toggleLanguage(){language=language==='ko'?'zh':'ko';localStorage.setItem(LANG_KEY,language);updateLangButton();showHome()}
function hasKorean(s){return /[가-힣]/.test(s)}
async function translateVisibleToChinese(){
  const nodes=[]; const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  while(walker.nextNode()){const n=walker.currentNode;const el=n.parentElement;if(el&&(el.tagName==='SCRIPT'||el.tagName==='STYLE'))continue;if(hasKorean(n.nodeValue)&&n.nodeValue.trim())nodes.push(n)}
  const unique=[...new Set(nodes.map(n=>n.nodeValue.trim()))];
  const missing=unique.filter(x=>!translationCache[x]);
  if(missing.length){
    try{const r=await fetch('/translate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({texts:missing})});const d=await r.json();(d.translations||[]).forEach((v,i)=>{if(v)translationCache[missing[i]]=v});localStorage.setItem('toeic5_zh_cache_v1',JSON.stringify(translationCache))}catch(e){}
  }
  nodes.forEach(n=>{const raw=n.nodeValue;const key=raw.trim();if(translationCache[key])n.nodeValue=raw.replace(key,translationCache[key])});
  updateLangButton();
}
function setLevel(n){state.level=n;save();showHome()}
function home(){
  const g=currentGroup(),done=state.completed.length,pct=Math.round(done/GS.length*100),ws=GS[g];
  const review=state.completed.slice().sort((a,b)=>a-b);
  layout(`<section class="hero"><h1>하루 5단어, 게임처럼 외우기</h1><p>5개 학습 → 테스트 → 오답 복습. 이미 끝낸 세트도 언제든 다시 공부할 수 있습니다.</p><div class="bar"><div style="width:${pct}%"></div></div><p>${done} / ${GS.length} 세트 완료 · 전체 ${WORDS.length}단어 · 오답 ${Object.keys(state.wrong).length}개</p></section>
  <section class="card"><h2>테스트 레벨 선택</h2><div class="mode-grid">
    <button class="mode ${state.level===1?'active':''}" onclick="setLevel(1)"><h3>LEVEL 1 · 객관식</h3><p>영어 단어를 보고 한국어 뜻 4개 중 하나를 선택합니다.</p></button>
    <button class="mode ${state.level===2?'active':''}" onclick="setLevel(2)"><h3>LEVEL 2 · 랜덤 입력</h3><p>한국어 뜻 → 영어 타자 또는 영어 → 한국어 뜻을 랜덤으로 출제합니다.</p></button>
  </div></section>
  <section class="card"><h2>다음 학습: ${g+1}세트</h2><p class="muted">단어 ${ws[0].number}~${ws[ws.length-1].number} · 현재 LEVEL ${state.level}</p><div class="grid">${ws.map(w=>`<div class="card"><div class="num">${w.number}</div><div class="word">${esc(w.word)} <button class="speaker" onclick="speak('${esc(w.word).replace(/'/g,"\\'")}');event.stopPropagation()" title="발음 듣기">🔊</button></div><div class="meaning">${esc(w.meaning)}</div></div>`).join('')}</div><div class="actions"><button class="btn primary" onclick="showLearn(${g})">5단어 학습 시작 →</button><button class="btn" onclick="startQuiz(${g},false)">바로 테스트</button></div></section>
  ${review.length?`<section class="card" style="margin-top:13px"><h2>복습</h2><p class="muted">완료한 단어를 5개씩 나누지 않고 한곳에서 확인하고 다시 학습할 수 있습니다.</p><div class="actions"><button class="btn green" onclick="showReview()">전체 복습 보기 →</button><button class="btn" onclick="startReviewQuiz()">완료 단어 랜덤 테스트</button></div></section>`:''}
  <section class="card danger" style="margin-top:13px"><h2>학습 데이터</h2><p class="muted">이 브라우저에 저장된 완료 진도, 오답노트, 테스트 기록을 모두 삭제합니다.</p><button class="btn red" onclick="resetProgress()">학습 데이터 초기화</button></section>
  <div class="grid" style="margin-top:13px"><div class="card"><div class="num">누적 테스트</div><div class="word">${state.quizzes}회</div></div><div class="card"><div class="num">정답률</div><div class="word">${state.answered?Math.round(state.correct/state.answered*100):0}%</div></div><div class="card"><div class="num">오답 단어</div><div class="word">${Object.keys(state.wrong).length}개</div></div></div>`)
}
function showHome(){home()}
function showLearn(g){const ws=GS[g]||GS[0];layout(`<section class="hero"><h1>${g+1}번째 5단어</h1><p>영어 단어를 먼저 보고 뜻을 떠올린 뒤 확인하세요. 🔊 버튼으로 발음도 듣고, <b>예문 보기</b>에서 TOEIC 실전형 문장과 전체 한국어 해석을 확인하세요.</p></section><div class="grid">${ws.map(w=>`<div class="card"><div class="num">${w.number}</div><div class="word">${esc(w.word)} <button class="speaker" onclick="speak('${esc(w.word).replace(/'/g,"\'")}')" title="발음 듣기">🔊 듣기</button></div><details><summary>뜻 보기</summary><div class="meaning">${esc(w.meaning)}</div></details><details style="margin-top:10px"><summary>💬 예문 보기</summary><div class="meaning"><b>${esc(exampleFor(w))}</b><div style="margin-top:6px;color:#374151">🇰🇷 ${esc(exampleTranslation(w))}</div><div class="small muted" style="margin-top:6px">TOEIC 실전형 예문 · 전체 문장 해석</div></div></details></div>`).join('')}</div><div class="actions"><button class="btn" onclick="showHome()">← 홈</button><button class="btn primary" onclick="startQuiz(${g},false)">LEVEL ${state.level} 테스트 시작 →</button></div>`)}
function getPOS(w){const m=String(w.meaning||''); const x=m.match(/\(([^)]*)\)/); return x?x[1].toLowerCase():''}
function cleanMeaning(w){return String(w.meaning||'').replace(/\([^)]*\)/g,'').split(/[,/;·]|\s+또는\s+|\s+및\s+/)[0].trim()}
function exampleFor(w){
  const word=String(w.word); const m=cleanMeaning(w); const pos=getPOS(w);
  const meaning=m.replace(/\s+/g,' ').trim();
  // TOEIC/비즈니스 상황에서 자연스럽게 쓰이는, 너무 쉽지 않은 짧은 예문
  const cues=[
    [/예약|예매|reserve/i,`Please reserve a conference room for tomorrow morning.`],
    [/수신|인정|감사|acknowledge/i,`Please acknowledge receipt of the email by Friday.`],
    [/재고|inventory/i,`We need to check our inventory before placing the order.`],
    [/경영진|임원|executive/i,`The executive will attend the meeting this afternoon.`],
    [/특징|특색|특집|feature/i,`The new model features a more efficient design.`],
    [/상품권|바우처|voucher/i,`Customers can use the voucher at participating stores.`],
    [/견적|평가|추산|estimate/i,`The contractor provided an estimate for the repairs.`],
    [/재개|resume/i,`The meeting will resume after a short break.`],
    [/문제|이슈|발행|issue/i,`The company plans to issue a revised report.`],
    [/자격|적격|eligible/i,`Only eligible employees can apply for the program.`],
    [/주도권|계획|initiative/i,`The company launched a new training initiative.`],
    [/요리|음식|culinary/i,`The hotel is known for its excellent culinary program.`],
    [/광범위|대규모|extensive/i,`The project requires extensive research and planning.`],
    [/예치금|보증금|deposit/i,`A deposit is required to confirm the reservation.`],
    [/소매|retail/i,`The company expanded its retail operations last year.`],
    [/가격|알맞|affordable/i,`The hotel offers comfortable rooms at affordable rates.`],
    [/승인|수여|grant/i,`The committee granted funding for the project.`],
    [/상당히|현저|중요한 정도|significantly/i,`Sales increased significantly during the holiday season.`]
  ];
  for(const [re,sentence] of cues) if(re.test(meaning)||re.test(word)) return sentence;
  if(/동사|verb/.test(pos)) return `The manager asked us to ${word} the request promptly.`;
  if(/형용사|adjective/.test(pos)) return `The company chose a ${word} solution for the project.`;
  if(/부사|adverb/.test(pos)) return `The results have improved ${word} over the past year.`;
  if(/전치사|preposition/.test(pos)) return `The office is ${word} the main entrance.`;
  if(/명사|noun/.test(pos)) return `The manager discussed the ${word} during the meeting.`;
  return `The company introduced a new ${word} policy this year.`;
}
function exampleTranslation(w){
  const word=String(w.word); const m=cleanMeaning(w); const pos=getPOS(w);
  const cues=[
    [/예약|예매|reserve/i,'내일 아침 회의실을 예약해 주세요.'],
    [/수신|인정|감사|acknowledge/i,'금요일까지 이메일을 받았다는 사실을 확인해 주세요.'],
    [/재고|inventory/i,'주문하기 전에 재고를 확인해야 합니다.'],
    [/경영진|임원|executive/i,'그 임원은 오늘 오후 회의에 참석할 예정입니다.'],
    [/특징|특색|특집|feature/i,'새 모델은 더욱 효율적인 디자인을 갖추고 있습니다.'],
    [/상품권|바우처|voucher/i,'고객은 참여 매장에서 이 바우처를 사용할 수 있습니다.'],
    [/견적|평가|추산|estimate/i,'계약업체는 수리 비용에 대한 견적을 제공했습니다.'],
    [/재개|resume/i,'회의는 잠시 휴식 후 다시 시작될 예정입니다.'],
    [/문제|이슈|발행|issue/i,'회사는 수정된 보고서를 발행할 계획입니다.'],
    [/자격|적격|eligible/i,'자격이 있는 직원만 이 프로그램에 신청할 수 있습니다.'],
    [/주도권|계획|initiative/i,'회사는 새로운 교육 계획을 시작했습니다.'],
    [/요리|음식|culinary/i,'그 호텔은 훌륭한 요리 프로그램으로 유명합니다.'],
    [/광범위|대규모|extensive/i,'그 프로젝트에는 광범위한 조사와 계획이 필요합니다.'],
    [/예치금|보증금|deposit/i,'예약을 확정하려면 보증금이 필요합니다.'],
    [/소매|retail/i,'그 회사는 지난해 소매 사업을 확장했습니다.'],
    [/가격|알맞|affordable/i,'그 호텔은 합리적인 가격에 편안한 객실을 제공합니다.'],
    [/승인|수여|grant/i,'위원회는 그 프로젝트에 자금을 지원하기로 승인했습니다.'],
    [/상당히|현저|중요한 정도|significantly/i,'연휴 기간 동안 매출이 크게 증가했습니다.']
  ];
  for(const [re,t] of cues) if(re.test(m)||re.test(word)) return t;
  if(/동사|verb/.test(pos)) return `관리자는 우리에게 그 요청을 신속하게 처리하도록 요청했습니다. (${m})`;
  if(/형용사|adjective/.test(pos)) return `회사는 그 프로젝트를 위해 적절한 해결책을 선택했습니다. (${m})`;
  if(/부사|adverb/.test(pos)) return `지난 1년 동안 결과가 크게 개선되었습니다. (${m})`;
  if(/전치사|preposition/.test(pos)) return `사무실은 정문 근처에 있습니다. (${m})`;
  if(/명사|noun/.test(pos)) return `관리자는 회의에서 ${m}에 대해 논의했습니다.`;
  return `회사는 올해 새로운 정책을 도입했습니다. (${m})`;
}
function speak(word){if('speechSynthesis' in window){window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(word);u.lang='en-US';u.rate=.82;window.speechSynthesis.speak(u)}else alert('이 브라우저에서는 음성 재생을 지원하지 않습니다.')}
function makeOptions(correct){const others=WORDS.filter(x=>x.number!==correct.number);return [correct,...shuffle(others).slice(0,3)].sort(()=>Math.random()-.5)}
function shuffle(a){return [...a].sort(()=>Math.random()-.5)}
function startQuiz(g,review){const ws=review?shuffle(GS.flat()).slice(0,5):(GS[g]||GS[0]); if(state.level===2)showLevel2Quiz(ws,g,review);else showLevel1Quiz(ws,g,review)}
function showQuiz(g){startQuiz(g,false)}
function showLevel1Quiz(ws,g,review){const questions=ws.map(w=>({w,opts:makeOptions(w)}));window.currentQuiz={type:'level1',g,review,questions};layout(`<section class="hero"><h1>LEVEL 1 · ${review?'복습 ':''}테스트</h1><p>영어 단어에 맞는 한국어 뜻을 선택하세요.</p></section><form onsubmit="submitLevel1(event)">${questions.map((q,i)=>`<div class="card" style="margin-bottom:13px"><div class="quizq">${i+1}. ${esc(q.w.word)} <button type="button" class="speaker" onclick="speak('${esc(q.w.word).replace(/'/g,"\\'")}')">🔊</button></div>${q.opts.map(o=>`<label class="option"><input required type="radio" name="q${i}" value="${o.number}">${esc(o.meaning)}</label>`).join('')}</div>`).join('')}<button class="btn primary" type="submit">채점하기</button></form>`)}
function normalizeEnglish(s){return String(s).toLowerCase().trim().replace(/[\s\-_'’]/g,'').replace(/[^a-z]/g,'')}
function meaningParts(s){return String(s).replace(/\([^)]*\)/g,'').split(/[,/;·]|\s+또는\s+|\s+및\s+/).map(x=>x.trim()).filter(Boolean)}
function normalizeKorean(s){return String(s).toLowerCase().trim().replace(/[\s\-_'’.,!?~]/g,'').replace(/[^가-힣a-z0-9]/g,'')}
function lev(a,b){const m=a.length,n=b.length;if(!m)return n;if(!n)return m;let prev=Array.from({length:n+1},(_,i)=>i);for(let i=1;i<=m;i++){let cur=[i];for(let j=1;j<=n;j++)cur[j]=Math.min(cur[j-1]+1,prev[j]+1,prev[j-1]+(a[i-1]===b[j-1]?0:1));prev=cur}return prev[n]}
function koreanMeaningCorrect(input,meaning){const a=normalizeKorean(input);if(!a)return false;return meaningParts(meaning).some(p=>{const b=normalizeKorean(p);if(!b)return false;if(a===b||a.includes(b)||b.includes(a))return true;const d=lev(a,b);return d<=Math.max(1,Math.floor(Math.min(a.length,b.length)*.22))})}
function showLevel2Quiz(ws,g,review){const questions=shuffle(ws).map(w=>({w,kind:Math.random()<.5?'en':'ko'}));window.currentQuiz={type:'level2',g,review,questions};layout(`<section class="hero"><h1>LEVEL 2 · ${review?'복습 ':''}랜덤 테스트</h1><p>문제 유형이 랜덤으로 섞입니다. 한국어 뜻은 띄어쓰기나 약간의 표현 차이는 허용합니다.</p></section><form onsubmit="submitLevel2(event)">${questions.map((q,i)=>q.kind==='ko'?`<div class="card" style="margin-bottom:13px"><div class="type-pill">한국어 → 영어</div><div class="quizq">${i+1}. ${esc(q.w.meaning.replace(/\([^)]*\)/g,''))}</div><input class="input-answer" autocomplete="off" autocapitalize="none" spellcheck="false" name="q${i}" placeholder="영어 단어를 입력하세요" required></div>`:`<div class="card" style="margin-bottom:13px"><div class="type-pill">영어 → 한국어</div><div class="quizq">${i+1}. ${esc(q.w.word)} <button type="button" class="speaker" onclick="speak('${esc(q.w.word).replace(/'/g,"\\'")}')">🔊</button></div><input class="input-answer" name="q${i}" placeholder="한국어 뜻을 입력하세요" required></div>`).join('')}<button class="btn primary" type="submit">채점하기</button></form>`)}
function submitLevel1(e){e.preventDefault();const qs=window.currentQuiz.questions;let score=0,wrong=[];const fd=new FormData(e.target);qs.forEach((q,i)=>{const ans=Number(fd.get('q'+i));if(ans===q.w.number)score++;else wrong.push(q.w)});recordResult(score,qs.length,wrong);showResult(score,qs.length,wrong)}
function submitLevel2(e){e.preventDefault();const qs=window.currentQuiz.questions;let score=0,wrong=[];const fd=new FormData(e.target);qs.forEach((q,i)=>{const ans=String(fd.get('q'+i)||'');const ok=q.kind==='ko'?normalizeEnglish(ans)===normalizeEnglish(q.w.word):koreanMeaningCorrect(ans,q.w.meaning);if(ok)score++;else wrong.push(q.w)});recordResult(score,qs.length,wrong);showResult(score,qs.length,wrong)}
function recordResult(score,total,wrong){state.quizzes++;state.correct+=score;state.answered+=total;wrong.forEach(w=>{const k=String(w.number);if(!state.wrong[k])state.wrong[k]={...w,wrong_count:0};state.wrong[k].wrong_count++});const q=window.currentQuiz;if(q&&!q.review&&q.g!==undefined&&!state.completed.includes(q.g)){state.completed.push(q.g);state.completed.sort((a,b)=>a-b)}save()}
function showResult(score,total,wrong){layout(`<section class="hero"><div class="num">테스트 결과</div><div class="score">${score} / ${total}</div><p>${score===total?'완벽합니다! 🎉':`${wrong.length}개가 오답노트에 추가되었습니다.`}</p></section>${wrong.length?`<section class="card"><h2>이번 테스트 오답</h2><table><tr><th>No.</th><th>단어</th><th>뜻</th></tr>${wrong.map(w=>`<tr><td>${w.number}</td><td><b>${esc(w.word)}</b></td><td>${esc(w.meaning)}</td></tr>`).join('')}</table></section>`:''}<div class="actions"><button class="btn" onclick="showHome()">홈으로</button><button class="btn red" onclick="showWrong()">오답노트</button><button class="btn primary" onclick="showLearn(${currentGroup()})">다음 학습 →</button></div>`)}
function startReviewQuiz(){const ws=shuffle(GS.flat().filter((_,i)=>state.completed.includes(Math.floor(i/5)))).slice(0,5);if(!ws.length)return alert('먼저 완료한 세트가 필요합니다.');if(state.level===2)showLevel2Quiz(ws,true);else showLevel1Quiz(ws,currentGroup(),true)}
function showReview(){const vals=[];state.completed.slice().sort((a,b)=>a-b).forEach(i=>{(GS[i]||[]).forEach(w=>vals.push(w))});if(!vals.length){layout(`<section class="hero"><h1>복습</h1><p>아직 완료한 단어가 없습니다.</p></section><button class="btn primary" onclick="showHome()">학습하러 가기</button>`);return}layout(`<section class="hero"><h1>전체 복습</h1><p>완료한 ${vals.length}개 단어를 한곳에서 복습합니다. 🔊 버튼으로 발음도 들을 수 있습니다.</p></section><section class="card"><div class="grid">${vals.map(w=>`<div class="card"><div class="num">${w.number}</div><div class="word">${esc(w.word)} <button class="speaker" onclick="speak('${esc(w.word).replace(/'/g,"\\'")}')" title="발음 듣기">🔊</button></div><div class="meaning">${esc(w.meaning)}</div></div>`).join('')}</div><div class="actions"><button class="btn" onclick="showHome()">← 홈</button><button class="btn green" onclick="startReviewQuiz()">완료 단어 랜덤 테스트</button></div></section>`)}

function showWrong(){const vals=Object.values(state.wrong).sort((a,b)=>a.number-b.number);if(!vals.length){layout(`<section class="hero"><h1>오답노트</h1><p>아직 틀린 단어가 없습니다.</p></section><button class="btn primary" onclick="showHome()">학습하러 가기</button>`);return}layout(`<section class="hero"><h1>오답노트</h1><p>총 ${vals.length}개 단어</p></section><section class="card"><table><tr><th>No.</th><th>단어</th><th>뜻</th><th>오답</th></tr>${vals.map(x=>`<tr><td>${x.number}</td><td><b>${esc(x.word)}</b> <button class="speaker" onclick="speak('${esc(x.word).replace(/'/g,"\\'")}')">🔊</button></td><td>${esc(x.meaning)}</td><td>${x.wrong_count}회</td></tr>`).join('')}</table><div class="actions"><button class="btn primary" onclick="showWrongQuiz()">오답만 다시 테스트</button><button class="btn red" onclick="clearWrong()">오답노트 비우기</button></div></section>`)}
function showWrongQuiz(){const vals=Object.values(state.wrong);if(!vals.length)return showWrong();const ws=shuffle(vals).slice(0,5);if(state.level===2)showLevel2Quiz(ws,true);else{const questions=ws.map(w=>({w,opts:makeOptions(w)}));window.currentQuiz={type:'wrong',questions,review:true};layout(`<section class="hero"><h1>오답 복습 테스트</h1><p>현재 LEVEL ${state.level} 방식으로 출제합니다.</p></section><form onsubmit="submitWrong(event)">${questions.map((q,i)=>`<div class="card" style="margin-bottom:13px"><div class="quizq">${i+1}. ${esc(q.w.word)}</div>${q.opts.map(o=>`<label class="option"><input required type="radio" name="q${i}" value="${o.number}">${esc(o.meaning)}</label>`).join('')}</div>`).join('')}<button class="btn primary">채점하기</button></form>`)}}
function submitWrong(e){e.preventDefault();const qs=window.currentQuiz.questions;const fd=new FormData(e.target);let score=0,wrong=[];qs.forEach((q,i)=>{const ans=Number(fd.get('q'+i));if(ans===q.w.number)score++;else {wrong.push(q.w);if(state.wrong[String(q.w.number)])state.wrong[String(q.w.number)].wrong_count++}});recordResult(score,qs.length,wrong);showResult(score,qs.length,wrong)}
function clearWrong(){if(confirm('오답노트를 모두 삭제할까요?')){state.wrong={};save();showWrong()}}
function resetProgress(){if(confirm('학습 진도, 오답노트, 테스트 기록을 모두 초기화할까요? 이 작업은 되돌릴 수 없습니다.')){state=emptyState();save();alert('학습 데이터가 초기화되었습니다.');showHome()}}
showHome();
</script>
</body></html>'''

@app.get("/")
def index():
    return render_template_string(HTML.replace("__WORDS__", json.dumps(WORDS, ensure_ascii=False)))

@app.post("/translate")
def translate():
    data=request.get_json(silent=True) or {}
    texts=data.get("texts") or []
    texts=[str(x)[:500] for x in texts[:40]]
    out=[]
    for text in texts:
        try:
            q=urllib.parse.quote(text)
            url=f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=ko&tl=zh-CN&dt=t&q={q}"
            with urllib.request.urlopen(url, timeout=5) as resp:
                raw=json.loads(resp.read().decode("utf-8"))
            out.append("".join(part[0] for part in raw[0] if part and part[0]))
        except Exception:
            out.append(text)
    return jsonify(translations=out)

@app.get("/health")
def health():
    return jsonify(status="ok", words=len(WORDS))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
