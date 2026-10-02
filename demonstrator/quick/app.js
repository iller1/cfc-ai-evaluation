'use strict';
const $ = id => document.getElementById(id);
const copy = {
  en: {
    eyebrow:'ONE CLAIM · ONE CHANGED INPUT', title:'Two sources agree. Is that enough?', lead:'A definite conclusion needs more than matching answers.',
    evidence:'01 / EVIDENCE STATE', sourceA:'Source A supports the claim', sourceB:'Source B supports the claim', current:'Current · within scope',
    rule:'This case requires two independent supports. Different source labels do not establish independence.', candidateLabel:'FIXED CANDIDATE CONCLUSION', candidate:'“DemoSubject is safe.”', fiction:'Fictional structured example; no live model response.',
    check:'02 / FROZEN CFC CHECK', claimState:'Claim state', closure:'Control closure', authority:'Explicit independence attestation',
    recorded:'Recorded execution · CFC Anchor 0.2.90rc1. The button switches between two actual saved runs; it does not execute Python in your browser.',
    boundary:'The attestation is synthetic demo input. ALLOW means this structured case meets the controller’s closure conditions; it does not establish real-world safety or general AI reliability.',
    details:'Inspect the evidence and raw results', delta:'Only changed input: independence_authority = NONE → VERIFIED. Conclusion, evidence, provenance shape, scope and required support count are identical.',
    download:'Download both inputs and raw outputs (JSON)', full:'Full executable demo & source ↗', wrapper:'Operator Wrapper v1.23 remains separate and unchanged.',
    stopReason:'Two positive supports. Independence has not been established.', allowReason:'The explicit independence attestation permits closure in this case.',
    before:'A / BEFORE', after:'B / AFTER', change:'Only the independence-authority state changes.', add:'Add the demo attestation →', reset:'Remove the attestation ↺',
    stopTake:'Agreement alone does not justify closure here. Add the missing attestation to see the second recorded result.',
    allowTake:'Same evidence, different authority state. The recorded controller result changes from STOP to ALLOW.',
    loading:'Loading recorded execution…', error:'The saved results could not be loaded or checked. No decision is displayed.', unavailable:'RESULT UNAVAILABLE', retry:'Retry loading', timestamp:'Recorded at (UTC): ', commit:'Source revision: '
  },
  pl: {
    eyebrow:'JEDNO TWIERDZENIE · JEDNA ZMIANA', title:'Dwa źródła są zgodne. Czy to wystarczy?', lead:'Stanowczy wniosek wymaga więcej niż zgodnych odpowiedzi.',
    evidence:'01 / STAN DOWODÓW', sourceA:'Źródło A potwierdza twierdzenie', sourceB:'Źródło B potwierdza twierdzenie', current:'Aktualne · we właściwym zakresie',
    rule:'Ten przypadek wymaga dwóch niezależnych źródeł wsparcia. Różne nazwy źródeł nie potwierdzają niezależności.', candidateLabel:'STAŁY WNIOSEK DO SPRAWDZENIA', candidate:'„DemoSubject jest bezpieczny”.', fiction:'Fikcyjny, ustrukturyzowany przykład; bez odpowiedzi modelu na żywo.',
    check:'02 / KONTROLA ZAMROŻONYM CFC', claimState:'Stan twierdzenia', closure:'Domknięcie kontroli', authority:'Jawne poświadczenie niezależności',
    recorded:'Zapis wykonania · CFC Anchor 0.2.90rc1. Przycisk przełącza dwa rzeczywiste, zapisane wyniki; nie uruchamia Pythona w przeglądarce.',
    boundary:'Poświadczenie jest syntetycznym wejściem demonstracyjnym. ALLOW oznacza spełnienie warunków domknięcia tego przypadku; nie dowodzi rzeczywistego bezpieczeństwa ani ogólnej niezawodności AI.',
    details:'Zobacz dowody i surowe wyniki', delta:'Jedyna zmiana wejścia: independence_authority = NONE → VERIFIED. Wniosek, dowody, struktura pochodzenia, zakres i wymagana liczba źródeł pozostają identyczne.',
    download:'Pobierz oba wejścia i surowe wyniki (JSON)', full:'Pełny demonstrator do uruchomienia i kod ↗', wrapper:'Operator Wrapper v1.23 pozostaje osobny i niezmieniony.',
    stopReason:'Dwa źródła potwierdzają twierdzenie. Nie ustalono ich niezależności.', allowReason:'Jawne poświadczenie niezależności pozwala domknąć ten przypadek.',
    before:'A / PRZED', after:'B / PO', change:'Zmienia się tylko stan poświadczenia niezależności.', add:'Dodaj poświadczenie demonstracyjne →', reset:'Usuń poświadczenie ↺',
    stopTake:'Sama zgodność nie uzasadnia tu domknięcia. Dodaj brakujące poświadczenie, by zobaczyć drugi zapisany wynik.',
    allowTake:'Te same dowody, inny stan poświadczenia. Zapisany wynik kontrolera zmienia się ze STOP na ALLOW.',
    loading:'Wczytuję zapis wykonania…', error:'Nie udało się wczytać lub sprawdzić zapisanych wyników. Decyzja nie jest wyświetlana.', unavailable:'WYNIK NIEDOSTĘPNY', retry:'Wczytaj ponownie', timestamp:'Wykonano (UTC): ', commit:'Wersja źródłowa: '
  }
};
let lang = new URLSearchParams(location.search).get('lang') === 'pl' ? 'pl' : 'en';
let record = null, selected = 'a', failed = false;
const stable = x => Array.isArray(x) ? '['+x.map(stable).join(',')+']' : x && typeof x === 'object' ? '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+stable(x[k])).join(',')+'}' : JSON.stringify(x);
function validate(data) {
  if (data.mode !== 'recorded_frozen_engine_execution') throw Error('Invalid mode');
  const a=data.experiment.a.input, b=data.experiment.b.input;
  const delta=[...new Set([...Object.keys(a),...Object.keys(b)])].filter(k=>stable(a[k])!==stable(b[k]));
  if (stable(delta)!==stable(['independence_authority']) || a.independence_authority!=='NONE' || b.independence_authority!=='VERIFIED') throw Error('Invalid A/B inputs');
  for (const key of ['a','b']) {
    const run=data.runs[key], expected=key==='b';
    if(run.result.engine_sha256!==data.engine_sha256 || run.result.control_closure!==expected || run.presentation.decision!==(expected?'ALLOW':'STOP') || run.presentation.claim_state!==(expected?'VERIFIED':'SUPPORTED') || run.result.claim_states[0].status!==run.presentation.claim_state) throw Error('Inconsistent recorded results');
  }
}
function render() {
  const t=copy[lang]; document.documentElement.lang=lang;
  document.querySelectorAll('[data-t]').forEach(el=>el.textContent=t[el.dataset.t]);
  for(const l of ['en','pl']) $(l).setAttribute('aria-pressed',String(l===lang));
  $('stepLabel').textContent=t[selected==='a'?'before':'after']; $('actionDescription').textContent=t.change;
  if(!record){$('decision').textContent=failed?'—':'…'; $('output').dataset.state='loading'; $('reason').textContent=t[failed?'error':'loading']; $('toggle').textContent=t[failed?'retry':'loading']; $('toggle').disabled=!failed; $('takeaway').textContent=''; return;}
  const run=record.runs[selected], allow=run.result.control_closure;
  $('output').dataset.state=allow?'allow':'stop'; $('decision').textContent=run.presentation.decision;
  $('reason').textContent=t[allow?'allowReason':'stopReason']; $('claimState').textContent=run.presentation.claim_state;
  $('closure').textContent=String(run.result.control_closure); $('authorityState').textContent=record.experiment[selected].input.independence_authority;
  $('toggle').disabled=false; $('toggle').textContent=t[allow?'reset':'add']; $('takeaway').textContent=t[allow?'allowTake':'stopTake'];
  $('stamp').textContent=t.timestamp+record.generated_at_utc+' · '+t.commit+record.source_commit;
  $('engine').textContent=record.engine_sha256;
  for(const k of ['a','b']) $('raw'+k.toUpperCase()).textContent=JSON.stringify({input:record.experiment[k].input,output:record.runs[k].result},null,2);
}
async function load(){ failed=false; render(); try {const response=await fetch('recorded-ab.json'); if(!response.ok)throw Error('Load failed'); const data=await response.json(); validate(data); record=data;} catch(e){failed=true; record=null;} render(); }
$('toggle').onclick=()=>{if(failed){load();return;} selected=selected==='a'?'b':'a';render();};
for(const l of ['en','pl']) $(l).onclick=()=>{lang=l;render();};
load();
