let lang='en', idx=0, selected=null, locked=false;
let stats={correct:0,premature:0,overcautious:0};

function t(el){
  const v=el.dataset[lang];
  if(v!==undefined) el.textContent=v;
}
function applyLang(){
  document.documentElement.lang=lang;
  document.querySelectorAll('[data-en]').forEach(t);
  document.getElementById('enBtn').classList.toggle('active',lang==='en');
  document.getElementById('plBtn').classList.toggle('active',lang==='pl');
  if(!document.getElementById('quiz').classList.contains('hidden')) renderCase();
  if(!document.getElementById('result').classList.contains('hidden')) renderResult();
}
function setLang(v){lang=v;applyLang();}

function startQuiz(){
  idx=0; selected=null; locked=false; stats={correct:0,premature:0,overcautious:0};
  document.getElementById('start').classList.add('hidden');
  document.getElementById('result').classList.add('hidden');
  document.getElementById('quiz').classList.remove('hidden');
  renderCase();
}
function renderCase(){
  const c=CASES[idx];
  document.getElementById('progress').style.width=((idx)/CASES.length*100)+'%';
  document.getElementById('counter').textContent=(lang==='en'?'Question ':'Pytanie ')+(idx+1)+' / '+CASES.length;
  document.getElementById('caseid').textContent=c.id;
  document.getElementById('title').textContent=c['title_'+lang];
  document.getElementById('scenario').textContent=c['scenario_'+lang];
  document.getElementById('question').textContent=c['question_'+lang];
  const box=document.getElementById('options'); box.innerHTML='';
  c.options.forEach((o,i)=>{
    const b=document.createElement('button');
    b.className='option'+(selected===i?' selected':'');
    b.textContent=o[lang];
    b.disabled=locked;
    b.onclick=()=>{ if(locked)return; selected=i; renderCase(); document.getElementById('checkBtn').disabled=false; };
    box.appendChild(b);
  });
  document.getElementById('checkBtn').disabled=(selected===null || locked);
  t(document.getElementById('checkBtn'));
  const fb=document.getElementById('feedback');
  if(!locked){fb.classList.add('hidden');document.getElementById('nextBtn').classList.add('hidden');}
  else showFeedback();
}
function checkAnswer(){
  if(selected===null||locked)return;
  const c=CASES[idx], chosen=c.options[selected];
  locked=true;
  if(selected===c.correct) stats.correct++;
  else if(chosen.kind==='overcautious') stats.overcautious++;
  else stats.premature++;
  renderCase();
}
function showFeedback(){
  const c=CASES[idx], good=selected===c.correct, fb=document.getElementById('feedback');
  fb.className='feedback '+(good?'good':'bad');
  const heading=good?(lang==='en'?'✓ Correct':'✓ Dobrze'):(lang==='en'?'Not quite':'Nie całkiem');
  const answer=c.options[c.correct][lang];
  const sourceNote=c.source==='test_r'
    ? (lang==='en'?'This case is adapted from the supplied HAWM Test R demonstrator.':'Ten przypadek jest zaadaptowany z dostarczonego demonstratora HAWM Test R.')
    : (lang==='en'?'Synthetic teaching case.':'Syntetyczny przykład edukacyjny.');
  fb.innerHTML=`<h3>${heading}</h3>
    <p><strong>${lang==='en'?'Best-supported answer':'Najlepiej uzasadniona odpowiedź'}:</strong> ${answer}</p>
    <p>${c['explain_'+lang]}</p>
    <details class="tech"><summary>${lang==='en'?'Technical view':'Widok techniczny'}</summary>
    <p class="small"><strong>${c.tech}</strong></p><p class="small">${sourceNote}</p></details>`;
  fb.classList.remove('hidden');
  const next=document.getElementById('nextBtn');
  t(next); next.textContent=(idx===CASES.length-1?(lang==='en'?'See my result':'Zobacz wynik'):(lang==='en'?'Next':'Dalej'));
  next.classList.remove('hidden');
}
function nextCase(){
  if(idx<CASES.length-1){idx++;selected=null;locked=false;renderCase();window.scrollTo({top:0,behavior:'smooth'});}
  else finish();
}
function finish(){
  document.getElementById('progress').style.width='100%';
  document.getElementById('quiz').classList.add('hidden');
  document.getElementById('result').classList.remove('hidden');
  renderResult(); window.scrollTo({top:0,behavior:'smooth'});
}
function renderResult(){
  const n=CASES.length;
  document.getElementById('score').textContent=stats.correct+' / '+n;
  document.getElementById('correctStat').textContent=stats.correct;
  document.getElementById('earlyStat').textContent=stats.premature;
  document.getElementById('cautiousStat').textContent=stats.overcautious;
  let msg;
  if(stats.correct>=9) msg=lang==='en'?'Excellent — you consistently kept certainty tied to the evidence.':'Świetnie — konsekwentnie wiązałeś pewność z tym, co naprawdę wynika z dowodów.';
  else if(stats.correct>=7) msg=lang==='en'?'Strong result — only a few cases pulled you toward too much or too little certainty.':'Bardzo dobry wynik — tylko kilka przypadków popchnęło Cię w stronę zbyt dużej lub zbyt małej pewności.';
  else msg=lang==='en'?'This is exactly why the distinction matters: plausible conclusions can feel justified before the evidence is actually enough.':'Właśnie dlatego to rozróżnienie ma znaczenie: wiarygodnie brzmiący wniosek może wydawać się uzasadniony, zanim dowody naprawdę na to pozwalają.';
  document.getElementById('resultText').textContent=msg;
  document.querySelectorAll('#result [data-en]').forEach(t);
}
async function copyResult(){
  const txt=lang==='en'
    ? `HAWM + CFC Human Tester v0.1\nScore: ${stats.correct}/${CASES.length}\nToo certain too early: ${stats.premature}\nUnnecessarily cautious: ${stats.overcautious}\n\nFeedback: [write one sentence here]`
    : `HAWM + CFC Human Tester v0.1\nWynik: ${stats.correct}/${CASES.length}\nZbyt wczesna pewność: ${stats.premature}\nNiepotrzebna ostrożność: ${stats.overcautious}\n\nFeedback: [napisz tutaj jedno zdanie]`;
  try{await navigator.clipboard.writeText(txt);alert(lang==='en'?'Result copied.':'Wynik skopiowany.');}
  catch(e){prompt(lang==='en'?'Copy this result:':'Skopiuj ten wynik:',txt);}
}
function restart(){
  document.getElementById('result').classList.add('hidden');
  document.getElementById('start').classList.remove('hidden');
  idx=0;selected=null;locked=false;stats={correct:0,premature:0,overcautious:0};
  window.scrollTo({top:0,behavior:'smooth'});
}
applyLang();
