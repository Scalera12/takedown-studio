/* Takedown Studio · comportements communs */
(function(){
  var d=document, qsa=function(s,r){return Array.prototype.slice.call((r||d).querySelectorAll(s))};

  /* intro officielle de l'accueil : « part vidéo de skate », avec les vrais dessins de Takedown.
     Tout avance image par image à 12 images/s (coupes sèches, caméra qui tremble), pas d'easing lisse.
     Une fois par visite (sessionStorage), ?intro pour la revoir, ?apercu pour la sauter.
     Un clic, une touche, la molette ou un toucher la passe. Rien si l'utilisateur demande moins d'animation. */
  var marque=d.querySelector('.hero .mark');
  var q=new URLSearchParams(location.search), stock=null;
  try{stock=sessionStorage}catch(e){}
  var deja=false; try{deja=stock&&stock.getItem('td-intro')==='vue'}catch(e){}
  var jouer=marque&&!q.has('apercu')&&(q.has('intro')||!deja)&&scrollY<10&&!matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(jouer){
    try{stock&&stock.setItem('td-intro','vue')}catch(e){}
    var racine=marque.currentSrc||marque.src, base=racine.slice(0,racine.indexOf('assets/img/'));
    var im=function(nom){return base+'assets/img/'+nom};
    var html=d.documentElement; html.classList.add('intro-on','intro-vue');
    var cible=marque.getBoundingClientRect();
    var hasard=function(a,b){return a+Math.random()*(b-a)};
    var ov=d.createElement('div'); ov.className='intro'; ov.setAttribute('aria-hidden','true');
    var portrait=innerHeight>innerWidth;
    /* les plans : [début, fin] en secondes, contenu, cadrage */
    var plans=[
      {de:.17,a:.6,  h:'<div class="b" data-j="3" style="left:'+(portrait?'-18':'4')+'%;top:12%;height:'+(portrait?'70':'98')+'vh;transform:rotate(5deg)"><img style="height:100%;width:auto" src="'+im('illustration-encre-blanc-800.webp')+'" alt=""></div>', zoom:.08},
      {de:.68,a:1.06,h:'<div class="b" data-j="4" style="right:'+(portrait?'-30':'-4')+'%;top:-14%;height:'+(portrait?'72':'104')+'vh;transform:rotate(-11deg)"><img style="height:100%;width:auto" src="'+im('illustration-pinceau-blanc-800.webp')+'" alt=""></div>', pan:16},
      {de:1.06,a:1.2,inv:1,h:'<div class="b" data-j="6" style="right:'+(portrait?'-26':'2')+'%;top:-8%;height:'+(portrait?'72':'104')+'vh;transform:rotate(-8deg)"><img style="height:100%;width:auto" src="'+im('illustration-pinceau-noir-800.webp')+'" alt=""></div>'},
      {de:1.2,a:1.82,h:'<div class="b" data-j="3" style="left:'+(portrait?'0':'3')+'vw;top:50%;width:'+(portrait?'190':'112')+'vw;transform:translateY(-50%) rotate(-7deg)"><img src="'+im('logo-texte-blanc-1000.webp')+'" alt=""><img class="fantome" src="'+im('logo-texte-blanc-1000.webp')+'" alt=""></div>', panDe:portrait?40:16, panA:portrait?-92:-4},
      {de:1.9,a:9,h:'<div class="b logo" data-j="2" style="left:'+cible.left+'px;top:'+cible.top+'px;width:'+cible.width+'px"><img src="'+racine+'" alt=""></div>', calme:2.45}
    ];
    var html2='';
    plans.forEach(function(p,n){html2+='<div class="plan'+(p.inv?' inv':'')+'" data-n="'+n+'">'+p.h+'</div>'});
    for(var r=0;r<3;r++) html2+='<span class="rayure"></span>';
    html2+='<div class="vignette"></div><div class="grain"></div>'+
      '<span class="hud rec"><i></i>Rec</span><span class="hud tc">00:00:00:00</span>'+
      '<span class="hud sp">SP · Takedown Studio · Bromont QC</span><button class="passer" type="button">Passer ›</button>';
    ov.innerHTML=html2;
    d.body.appendChild(ov);

    var elPlans=Array.prototype.slice.call(ov.querySelectorAll('.plan'));
    var rayures=Array.prototype.slice.call(ov.querySelectorAll('.rayure'));
    var grain=ov.querySelector('.grain'), tc=ov.querySelector('.tc'), rec=ov.querySelector('.rec i');
    var bandeDepart=Math.floor(hasard(11,47))*1800+Math.floor(hasard(0,1800));   // compteur de cassette pris au milieu d'une bande
    var pad=function(x){return (x<10?'0':'')+x};
    var gel=q.has('gel')?parseFloat(q.get('gel')):null;
    var t0=performance.now(), fini=false, image=0, evts=['click','keydown','wheel','touchstart'];
    var tic=function(){
      var t=gel!==null?gel:(performance.now()-t0)/1000; image++;   // ?gel=1.3 fige l'intro à 1,3 s (réglages)
      /* plan actif : coupe sèche, aucun fondu */
      plans.forEach(function(p,n){
        var on=t>=p.de&&t<p.a; elPlans[n].classList.toggle('on',on);
        if(!on) return;
        var b=elPlans[n].querySelector('.b'), j=+b.dataset.j, prog=(t-p.de)/(Math.min(p.a,3)-p.de);
        if(p.calme&&t>p.calme) j=0;   // le logo finit immobile, à sa place dans le hero
        var bouge='translate('+(j?hasard(-j,j):0).toFixed(1)+'px,'+(j?hasard(-j,j):0).toFixed(1)+'px)';
        if(p.zoom) bouge+=' scale('+(1+p.zoom*Math.floor(prog*5)/5).toFixed(3)+')';
        if(p.pan) bouge+=' translateX('+(p.pan*(1-Math.floor(prog*4)/4)).toFixed(1)+'vw)';
        if(p.panDe!==undefined) bouge+=' translateX('+(p.panDe+(p.panA-p.panDe)*Math.floor(prog*7)/7).toFixed(1)+'vw)';   // panoramique saccadé
        b.querySelectorAll('img').forEach(function(i){i.style.transform=bouge});
      });
      /* grain qui saute, rayures de pellicule, compteur, REC qui clignote */
      grain.style.transform='translate('+hasard(-20,20).toFixed(0)+'%,'+hasard(-20,20).toFixed(0)+'%)';
      rayures.forEach(function(s){var v=Math.random()<.35;s.style.display=v?'block':'none';if(v)s.style.left=hasard(3,97).toFixed(1)+'%'});
      var f=bandeDepart+Math.floor(t*30);
      tc.textContent=pad(Math.floor(f/108000))+':'+pad(Math.floor(f/1800)%60)+':'+pad(Math.floor(f/30)%60)+':'+pad(f%30);
      rec.style.opacity=(Math.floor(t*2)%2)?'0':'1';
      if(t>=3.05&&gel===null) fin();
    };
    var horloge=setInterval(tic,1000/12); tic();
    var fin=function(){
      if(fini)return; fini=true; clearInterval(horloge);
      evts.forEach(function(ev){removeEventListener(ev,fin)});
      elPlans.forEach(function(p,n){p.classList.toggle('on',n===elPlans.length-1)});
      var l=elPlans[elPlans.length-1].querySelector('img'); l.style.transform='none';
      ov.classList.add('sort'); html.classList.remove('intro-on');
      setTimeout(function(){ov.remove()},650);
    };
    if(gel===null) evts.forEach(function(ev){addEventListener(ev,fin,{passive:true})});
  }

  /* apparition au défilement */
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.12,rootMargin:'0px 0px -40px 0px'});
    qsa('.rv').forEach(function(el,i){el.style.transitionDelay=(i%4)*80+'ms';io.observe(el)});
  } else qsa('.rv').forEach(function(el){el.classList.add('in')});

  /* quotes qui s'allument */
  var lignes=qsa('.words .line');
  if(lignes.length){
    var allume=function(){var mid=innerHeight*.62;lignes.forEach(function(l){l.classList.toggle('on',l.getBoundingClientRect().top<mid)})};
    addEventListener('scroll',allume,{passive:true});allume();
  }

  /* menu cellulaire */
  var nav=d.querySelector('.nav'), burger=d.querySelector('.burger');
  if(burger){
    burger.addEventListener('click',function(){
      var ouvert=nav.classList.toggle('open');
      burger.setAttribute('aria-expanded',ouvert);
      d.body.style.overflow=ouvert?'hidden':'';
    });
    qsa('.menu-m a').forEach(function(a){a.addEventListener('click',function(){nav.classList.remove('open');d.body.style.overflow=''})});
  }

  /* carrousel */
  qsa('[data-rail]').forEach(function(zone){
    var rail=zone.querySelector('.rail');
    qsa('.railnav button',zone).forEach(function(b){
      b.addEventListener('click',function(){var it=rail.querySelector('.item');rail.scrollBy({left:(+b.dataset.d)*it.offsetWidth*1.05})});
    });
  });

  var params=new URLSearchParams(location.search);

  /* filtres des réalisations */
  var chips=qsa('.chip[data-f]');
  if(chips.length){
    var filtrer=function(f){
      chips.forEach(function(c){c.setAttribute('aria-pressed',c.dataset.f===f)});
      qsa('.real').forEach(function(r){r.hidden=!(f==='tous'||r.dataset.c.split(' ').indexOf(f)>-1)});
    };
    chips.forEach(function(c){c.addEventListener('click',function(){
      filtrer(c.dataset.f);
      var u=new URL(location.href); if(c.dataset.f==='tous')u.searchParams.delete('f'); else u.searchParams.set('f',c.dataset.f);
      history.replaceState(null,'',u);
    })});
    var f=params.get('f'); if(f&&chips.some(function(c){return c.dataset.f===f}))filtrer(f);
  }

  /* formulaire de soumission */
  var form=d.getElementById('soumission');
  if(!form) return;
  var sel=form.querySelector('#service'), sais=form.querySelector('#sais-pas');
  var svc=params.get('service');
  if(svc&&sel.querySelector('option[value="'+svc+'"]')) sel.value=svc;
  var majSais=function(){
    if(sais.checked){sel.dataset.avant=sel.value;sel.value='je-sais-pas'}
    else if(sel.value==='je-sais-pas'&&sel.dataset.avant) sel.value=sel.dataset.avant;
  };
  sais.addEventListener('change',majSais);
  sel.addEventListener('change',function(){sais.checked=sel.value==='je-sais-pas'});
  if(sel.value==='je-sais-pas') sais.checked=true;

  /* fichiers */
  var depot=form.querySelector('.depot'), inp=form.querySelector('#fichiers'), liste=form.querySelector('.fichiers');
  var choisis=[];
  var taille=function(n){return n>1048576?(n/1048576).toFixed(1)+' Mo':Math.max(1,Math.round(n/1024))+' Ko'};
  var dessine=function(){
    liste.innerHTML='';
    choisis.forEach(function(f,i){
      var li=d.createElement('li');
      li.innerHTML='<b></b><span></span><button type="button">Retirer</button>';
      li.querySelector('b').textContent=f.name; li.querySelector('span').textContent=taille(f.size);
      li.querySelector('button').addEventListener('click',function(){choisis.splice(i,1);dessine()});
      liste.appendChild(li);
    });
  };
  var ajoute=function(fl){Array.prototype.forEach.call(fl,function(f){if(!choisis.some(function(c){return c.name===f.name&&c.size===f.size}))choisis.push(f)});dessine()};
  inp.addEventListener('change',function(){ajoute(inp.files);inp.value=''});
  ['dragenter','dragover'].forEach(function(t){depot.addEventListener(t,function(e){e.preventDefault();depot.classList.add('sur')})});
  ['dragleave','drop'].forEach(function(t){depot.addEventListener(t,function(e){e.preventDefault();depot.classList.remove('sur')})});
  depot.addEventListener('drop',function(e){ajoute(e.dataTransfer.files)});
  depot.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();inp.click()}});

  /* validation */
  var valide=function(){
    var premier=null;
    qsa('[required]',form).forEach(function(ch){
      var ok=ch.value.trim()!=='' && (ch.type!=='email'||/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(ch.value.trim()));
      ch.closest('.champ').classList.toggle('err',!ok);
      if(!ok&&!premier) premier=ch;
    });
    if(premier) premier.focus();
    return !premier;
  };
  qsa('[required]',form).forEach(function(ch){ch.addEventListener('input',function(){ch.closest('.champ').classList.remove('err')})});

  var etat=d.getElementById('etat'), bouton=form.querySelector('button[type=submit]');
  form.addEventListener('submit',function(e){
    e.preventDefault();
    etat.className='etat'; etat.textContent='';
    if(!valide()){etat.className='etat ko';etat.textContent='Il manque des informations. Regarde les champs en rouge.';return}
    var fd=new FormData(form);
    fd.delete('fichiers');
    choisis.forEach(function(f){fd.append('fichiers',f,f.name)});
    fd.append('page',d.referrer||'');
    bouton.disabled=true; bouton.textContent='Envoi en cours…';
    fetch(form.action,{method:'POST',body:fd}).then(function(r){
      if(!r.ok) throw new Error(r.status);
      form.hidden=true;
      etat.className='etat ok';
      etat.textContent='Merci pour ta demande. Nous allons regarder les informations reçues et te contacter pour discuter de ton projet.';
      etat.scrollIntoView({behavior:'smooth',block:'center'});
    }).catch(function(){
      etat.className='etat ko';
      etat.innerHTML='L’envoi n’a pas fonctionné. Réessaie dans un instant ou écris-nous à <a href="mailto:info@takedownstudio.com" style="text-decoration:underline">info@takedownstudio.com</a>.';
    }).then(function(){bouton.disabled=false;bouton.textContent='Envoyer ma demande'});
  });
})();
