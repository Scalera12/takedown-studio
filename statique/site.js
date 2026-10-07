/* Takedown Studio · comportements communs */
(function(){
  var d=document, qsa=function(s,r){return Array.prototype.slice.call((r||d).querySelectorAll(s))};

  /* intro officielle de l'accueil, faite avec les vrais dessins de Takedown.
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
    var ov=d.createElement('div'); ov.className='intro'; ov.setAttribute('aria-hidden','true');
    var hasard=function(a,b){return a+Math.random()*(b-a)};
    var eclats='';
    for(var e2=0;e2<18;e2++){var ang=e2/18*Math.PI*2+hasard(-.25,.25), dist=hasard(26,50);
      eclats+='<span class="eclat" style="--t:'+hasard(6,24).toFixed(0)+'px;--ex:'+(Math.cos(ang)*dist).toFixed(1)+'vmin;--ey:'+(Math.sin(ang)*dist).toFixed(1)+'vmin"></span>'}
    ov.innerHTML=
      '<div class="b mot"><img src="'+im('logo-texte-blanc-1000.webp')+'" alt=""></div>'+
      '<div class="b encre"><img src="'+im('illustration-encre-blanc-800.webp')+'" alt=""></div>'+
      '<div class="b pinceau"><img src="'+im('illustration-pinceau-blanc-800.webp')+'" alt=""></div>'+
      eclats+
      '<div class="b logo" style="left:'+cible.left+'px;top:'+cible.top+'px;width:'+cible.width+'px"><img src="'+racine+'" alt=""></div>'+
      '<span class="leg mono">Takedown Studio · Bromont</span><button class="passer" type="button">Passer ›</button>';
    d.body.appendChild(ov);

    /* « line boil » : chaque dessin tremble un peu, comme un dessin animé fait à la main */
    var traits=Array.prototype.slice.call(ov.querySelectorAll('.b img'));
    var boil=setInterval(function(){traits.forEach(function(i){
      i.style.transform='translate('+hasard(-1.6,1.6).toFixed(1)+'px,'+hasard(-1.6,1.6).toFixed(1)+'px) rotate('+hasard(-.7,.7).toFixed(2)+'deg)'})},110);

    var minuteries=[], fini=false, evts=['click','keydown','wheel','touchstart'];
    var plus=function(f,ms){minuteries.push(setTimeout(f,ms))};
    var choc=function(){ov.classList.remove('choc');void ov.offsetWidth;ov.classList.add('choc')};
    var fin=function(){
      if(fini)return; fini=true; minuteries.forEach(clearTimeout); clearInterval(boil);
      evts.forEach(function(ev){removeEventListener(ev,fin)});
      traits.forEach(function(i){i.style.transform='none'});
      var l=ov.querySelector('.logo'); l.style.animation='none'; l.style.opacity='1';
      ov.classList.add('sort'); html.classList.remove('intro-on');
      setTimeout(function(){ov.remove()},700);
    };
    plus(choc,1560);
    plus(fin,2950);
    evts.forEach(function(ev){addEventListener(ev,fin,{passive:true})});
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
