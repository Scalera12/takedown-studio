/* Takedown Studio · comportements communs */
(function(){
  var d=document, qsa=function(s,r){return Array.prototype.slice.call((r||d).querySelectorAll(s))};

  var calme=matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* logo qui flotte : une fois dessiné, il dérive et tourne lentement, comme s'il flottait.
     Somme de sinus à fréquences différentes = mouvement organique qui ne se répète pas. */
  var flotter=function(el,attente){
    if(!el||calme) return;
    var visible=true, depart=null, A=innerWidth<600?.6:1, actif=true;
    new IntersectionObserver(function(es){visible=es[0].isIntersecting}).observe(el);
    var bouge=function(now){
      if(!actif) return;
      if(depart===null) depart=now;
      var t0=(now-depart)/1000, t=t0*1.5, monte=Math.min(1,t0/1.6), k=A*monte*monte*(3-2*monte);
      if(visible){
        var x=k*(22*Math.sin(t*.42)+11*Math.sin(t*1.07+1.3)),
            y=k*(16*Math.sin(t*.33+2)+8*Math.sin(t*.91+.4)),
            r=k*(7*Math.sin(t*.27+.6)+3.5*Math.sin(t*.79+2.1)),
            s=1+k*.025*Math.sin(t*.53+1);
        el.style.transform='translate3d('+x.toFixed(1)+'px,'+y.toFixed(1)+'px,0) rotate('+r.toFixed(2)+'deg) scale('+s.toFixed(4)+')';
      }
      requestAnimationFrame(bouge);
    };
    setTimeout(function(){requestAnimationFrame(bouge)},attente||1900);
    return function(){actif=false};
  };
  flotter(d.querySelector('.hero.bientot .flotte'));
  flotter(d.querySelector('.hero .script-flotte'),2100);

  /* page d'entrée : les dessins du client flottent autour des lutteurs (demande de Takedown).
     Même flottement à sommes de sinus que le logo, plus une lente dérive et une légère rotation,
     chacun avec ses propres fréquences. Une seule boucle pour tous, transform seulement.
     Positions en % de l'écran, choisies pour laisser le logo et le bouton libres. */
  var NUEE_LARGE=[
    ['broderie-aiguille',   7, 10, 15, -8],
    ['presse-chaleur',     79,  8, 14,  6],
    ['serigraphie-racloir', 4, 56, 10,  9],
    ['patch-aiguille',     85, 50, 11, -6],
    ['chandail-tache',     13, 80, 15,  4],
    ['deux-tuques',        72, 78, 16, -3]
  ];
  var NUEE_CELL=[
    ['broderie-aiguille',   2,  8, 30, -8],
    ['presse-chaleur',     66,  7, 30,  6],
    ['chandail-tache',      3, 77, 32,  4],
    ['deux-tuques',        63, 78, 33, -3]
  ];
  var nuee=function(sp,base){
    var cell=innerWidth<700, liste=cell?NUEE_CELL:NUEE_LARGE;
    var boite=d.createElement('div'); boite.className='nuee'; boite.setAttribute('aria-hidden','true');
    var els=liste.map(function(n,i){
      var im=new Image(); im.alt=''; im.decoding='async';
      im.src=base+n[0]+'-blanc-360.webp';
      im.style.left=n[1]+'%'; im.style.top=n[2]+'%';
      im.style.setProperty('--w',(cell?n[3]+'vw':'min('+n[3]+'vw,'+Math.round(n[3]*13)+'px)'));
      im.style.setProperty('--o',cell?.6:.72);
      im.style.transform='rotate('+n[4]+'deg)';
      boite.appendChild(im);
      setTimeout(function(){im.classList.add('on')},(calme?0:1500)+i*180);
      // fréquences propres à chaque dessin, pour qu'ils ne bougent jamais ensemble
      return {el:im, r0:n[4], p:i*1.7+.4, f:.8+((i*37)%10)/25, a:cell?.55:1};
    });
    sp.insertBefore(boite,sp.firstChild);
    if(calme) return null;
    var actif=true, depart=null;
    var bouge=function(now){
      if(!actif) return;
      if(depart===null) depart=now;
      var t=(now-depart)/1000*1.5;
      for(var i=0;i<els.length;i++){
        var o=els[i], f=o.f, p=o.p, a=o.a;
        var x=a*(18*Math.sin(t*.31*f+p)+9*Math.sin(t*.83*f+p*2.1)+26*Math.sin(t*.07+p)),
            y=a*(14*Math.sin(t*.27*f+p+2)+7*Math.sin(t*.71*f+p*.6)+18*Math.sin(t*.05+p*1.3)),
            r=o.r0+6*Math.sin(t*.22*f+p)+2.5*Math.sin(t*.61*f+p*1.7);
        o.el.style.transform='translate3d('+x.toFixed(1)+'px,'+y.toFixed(1)+'px,0) rotate('+r.toFixed(2)+'deg)';
      }
      requestAnimationFrame(bouge);
    };
    requestAnimationFrame(bouge);
    return function(){actif=false};
  };

  /* page d'entrée de l'accueil : logo qui flotte + « Entrer ». Une fois par visite (sessionStorage),
     ?intro pour la revoir, ?apercu pour la sauter. Le contenu de l'accueil est déjà dans la page. */
  var marque=d.querySelector('.hero:not(.bientot) .mark, .hero[data-intro]');
  var q=new URLSearchParams(location.search), stock=null;
  try{stock=sessionStorage}catch(e){}
  var deja=false; try{deja=stock&&stock.getItem('td-entree')==='vue'}catch(e){}
  if(marque&&!q.has('apercu')&&(q.has('intro')||!deja)&&scrollY<10){
    var html=d.documentElement; html.classList.add('splash-on','splash-vu');
    var sp=d.createElement('div'); sp.className='splash'; sp.setAttribute('role','dialog'); sp.setAttribute('aria-label','Bienvenue chez Takedown Studio');
    sp.innerHTML='<div class="haut mono"><span>Takedown Studio</span><span>Bromont, QC</span></div>'+
      '<div class="flotte"><img src="'+(marque.getAttribute('data-intro')||marque.currentSrc||marque.src)+'" alt="Takedown Studio"></div>'+
      '<button class="entrer" type="button">Entrer <span aria-hidden="true">→</span></button>'+
      '<div class="bas mono"><span>Agence de branding</span><span>Vêtements et produits personnalisés</span></div>';
    d.body.appendChild(sp);
    var stop=flotter(sp.querySelector('.flotte'),1700);
    var stopNuee=nuee(sp,(marque.getAttribute('data-intro')||'').replace(/logo-complet[^\/]*$/,'')+'dessins/');
    var bouton=sp.querySelector('.entrer'), parti=false;
    try{bouton.focus({preventScroll:true})}catch(e){}
    var entrer=function(){
      if(parti) return; parti=true;
      try{stock&&stock.setItem('td-entree','vue')}catch(e){}
      removeEventListener('keydown',touche); removeEventListener('wheel',roule);
      sp.classList.add('sort'); html.classList.remove('splash-on');
      setTimeout(function(){stop&&stop();stopNuee&&stopNuee();sp.remove()},1100);
    };
    var touche=function(e){if(e.key==='Enter'||e.key==='Escape'||e.key===' '||e.key==='ArrowDown'){e.preventDefault();entrer()}};
    var roule=function(e){if(e.deltaY>8) entrer()};
    var y0=null;
    sp.addEventListener('touchstart',function(e){y0=e.touches[0].clientY},{passive:true});
    sp.addEventListener('touchmove',function(e){if(y0!==null&&y0-e.touches[0].clientY>50) entrer()},{passive:true});
    bouton.addEventListener('click',entrer);
    addEventListener('keydown',touche); addEventListener('wheel',roule,{passive:true});
  }

  /* l'entête : le script « Takedown Studio » et le monstre se dessinent; le script fait un premier tour
     sur lui-même, puis chacun refait un tour au survol ou au toucher (comme le logo de store.lqqkstudio.com).
     Minuteries plutôt qu'animationend : plus fiable. */
  Array.prototype.forEach.call(d.querySelectorAll('.hero .mark.bonhomme, .hero .mark.script'),function(el){
    if(calme) return;
    var script=el.classList.contains('script'), duree=script?1150:1000, fin=script?2150:2550;   // fin du dessin
    var tourner=function(){
      if(el.classList.contains('tourne')) return;
      el.classList.add('fini','tourne');
      setTimeout(function(){el.classList.remove('tourne')},duree);
    };
    el.addEventListener('mouseenter',tourner);
    el.addEventListener('click',tourner);
    if(d.documentElement.classList.contains('splash-vu')) el.classList.add('fini');
    else setTimeout(function(){el.classList.add('fini');if(script) tourner()},fin);
  });

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

  /* guide casquettes : carrousels qui défilent aux 3 s (pause quand on touche, quand c'est hors écran ou si le système réduit les animations) */
  qsa('.rail-g').forEach(function(rail){
    var slides=Array.prototype.slice.call(rail.children), chips=qsa('button',rail.parentNode.querySelector('.chips-g')||rail), i=0, pauseJusque=0, visible=false;
    var reduit=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
    var marque=function(n){i=n;chips.forEach(function(c,k){c.setAttribute('aria-pressed',k===n)})};
    var aller=function(n,doux){marque(n);rail.scrollTo({left:n*rail.clientWidth,behavior:doux===false?'auto':'smooth'})};
    var pause=function(){pauseJusque=Date.now()+8000};
    chips.forEach(function(c,k){c.addEventListener('click',function(){pause();aller(k)})});
    ['pointerdown','touchstart','wheel','focusin'].forEach(function(ev){rail.addEventListener(ev,pause,{passive:true})});
    var t=null;
    rail.addEventListener('scroll',function(){
      clearTimeout(t);t=setTimeout(function(){var n=Math.round(rail.scrollLeft/rail.clientWidth);if(n!==i&&n>=0&&n<slides.length)marque(n)},80);
    },{passive:true});
    if('IntersectionObserver' in window) new IntersectionObserver(function(es){visible=es[0].isIntersecting},{threshold:.35}).observe(rail); else visible=true;
    if(!reduit) setInterval(function(){
      if(!visible||document.hidden||Date.now()<pauseJusque) return;
      aller((i+1)%slides.length);
    },+rail.dataset.auto||3000);
  });

  /* filtres des réalisations */
  var chips=qsa('.chip[data-f]');
  if(chips.length){
    var filtrer=function(f){
      chips.forEach(function(c){c.setAttribute('aria-pressed',c.dataset.f===f)});
      qsa('.real').forEach(function(r){r.hidden=!(f==='tous'||r.classList.contains('insta')||r.dataset.c.split(' ').indexOf(f)>-1)});
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
  /* mêmes limites que le Worker : 8 fichiers, 10 Mo chacun, 25 Mo au total */
  var MAX_N=8, MAX_UN=10485760, MAX_TOT=26214400, refus=[];
  var ajoute=function(fl){
    refus=[];
    Array.prototype.forEach.call(fl,function(f){
      if(choisis.some(function(c){return c.name===f.name&&c.size===f.size}))return;
      var tot=choisis.reduce(function(a,c){return a+c.size},0);
      if(f.size>MAX_UN) refus.push(f.name+' dépasse 10 Mo');
      else if(choisis.length>=MAX_N) refus.push(f.name+' : maximum 8 fichiers');
      else if(tot+f.size>MAX_TOT) refus.push(f.name+' : maximum 25 Mo au total');
      else choisis.push(f);
    });
    dessine();
    var et=d.getElementById('etat');
    if(refus.length){et.className='etat ko';et.textContent='Fichier refusé : '+refus.join(' · ')+'. Envoie-le par courriel à info@takedownstudio.com si tu en as besoin.'}
    else if(et.className==='etat ko') {et.className='etat';et.textContent=''}
  };
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
      if(form.dataset.merci){location.href=form.dataset.merci;return}
      form.hidden=true;
      etat.className='etat ok';
      etat.textContent='Merci pour ta demande. Nous allons regarder les informations reçues et te contacter pour discuter de ton projet.';
      etat.scrollIntoView({behavior:'smooth',block:'center'});
    }).catch(function(err){
      etat.className='etat ko';
      if(String(err&&err.message)==='413'){etat.textContent='Tes fichiers sont trop lourds (10 Mo par fichier, 25 Mo au total). Retire-en un ou envoie-le par courriel à info@takedownstudio.com.';return}
      if(String(err&&err.message)==='429'){etat.textContent='Trop d’envois en peu de temps. Réessaie dans quelques minutes.';return}
      etat.innerHTML='L’envoi n’a pas fonctionné. Réessaie dans un instant ou écris-nous à <a href="mailto:info@takedownstudio.com" style="text-decoration:underline">info@takedownstudio.com</a>.';
    }).then(function(){bouton.disabled=false;bouton.textContent='Envoyer ma demande'});
  });
})();
