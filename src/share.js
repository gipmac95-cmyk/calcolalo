(function(){
  const hEl=document.querySelector('.tool-head h1');const h1=hEl?[...hEl.childNodes].filter(n=>!(n.classList&&n.classList.contains('ic'))).map(n=>n.textContent).join(''):document.title;
  const box=document.createElement('div');box.className='share';
  const EN=(document.documentElement.lang||'').startsWith('en');
  box.innerHTML='<span>'+(EN?'Share the result':'Condividi il risultato')+'</span><a class="btn wa" href="#" target="_blank" rel="noopener"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3a.4.4 0 0 0 0-.4l-.8-1.9c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.4.8 3.2.7a2.8 2.8 0 0 0 1.8-1.3 2.3 2.3 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z"/></svg> WhatsApp</a><button type="button" class="btn cp">'+(EN?'Copy link':'Copia link')+'</button>';
  const target=document.querySelector('.result')||document.querySelector('.panel');
  if(!target)return;target.appendChild(box);
  const url=()=>location.origin+location.pathname+location.search;
  box.querySelector('.wa').addEventListener('click',function(){
    const lbl=(document.querySelector('.result .lbl')||{}).textContent,big=(document.querySelector('.result .big')||{}).textContent;
    const t=big&&big.trim()!=='–'&&lbl?(EN?`${h1.trim()} – ${lbl.trim()}: ${big.trim()}. Work out yours for free 👉 ${url()}`:`${h1.trim()} – ${lbl.trim()}: ${big.trim()}. Calcola il tuo gratis qui 👉 ${url()}`):(EN?`Check out this free calculator: ${h1.trim()} 👉 ${url()}`:`Guarda questo calcolatore gratuito: ${h1.trim()} 👉 ${url()}`);
    this.href='https://wa.me/?text='+encodeURIComponent(t);
    try{if(window.gtag)gtag('event','share',{method:'whatsapp',content_type:'calcolatore',item_id:location.pathname})}catch(e){}
  });
  box.querySelector('.cp').addEventListener('click',function(){
    const b=this;const done=()=>{b.textContent=EN?'Link copied!':'Link copiato!';setTimeout(()=>b.textContent=EN?'Copy link':'Copia link',2000)};
    try{navigator.clipboard.writeText(url()).then(done,done)}catch(e){done()}
    try{if(window.gtag)gtag('event','share',{method:'copy_link',item_id:location.pathname})}catch(e){}
  });
})();
