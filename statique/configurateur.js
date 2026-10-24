/* Configurateur de casquette (page Casquettes 100 % personnalisées).
   Version de démonstration : formes en SVG simplifiées, à remplacer par les vrais visuels avec Takedown. */
(function(){
  var root=document.getElementById('configurateur');
  if(!root) return;

  var COULEURS=[['Noir','#161616'],['Blanc','#f4f4f2'],['Crème','#e8dfcc'],['Kaki','#6b6b3a'],['Marine','#1d2a44'],
                ['Gris','#8d8d90'],['Rouge','#c0262d'],['Rose patch','#F59FC1'],['Brun','#6a4a35'],['Vert forêt','#1f4d3a']];
  var PIECES=[['couronne','Couronne'],['visiere','Visière'],['bouton','Bouton'],['coutures','Coutures']];
  var FORMES={
    dad:{nom:'Dad cap',
      crown:'M70 262 C68 142 168 82 300 82 C424 82 486 152 492 262 Z',
      brim:'M468 250 C522 236 586 248 594 280 C542 294 482 288 436 272 Z',
      under:'M436 272 C482 288 542 294 594 280 L594 286 C540 301 480 295 432 279 Z',
      bouton:[300,82],logo:{devant:[404,176],cote:[262,188],derriere:[140,205]}},
    structuree:{nom:'Structurée',
      crown:'M78 270 C72 112 186 46 308 46 C432 46 494 124 494 270 Z',
      brim:'M470 262 L596 274 L590 296 L440 288 Z',
      under:'M440 288 L590 296 L590 303 L436 295 Z',
      bouton:[308,46],logo:{devant:[408,170],cote:[266,176],derriere:[140,200]}},
    trucker:{nom:'Trucker',mesh:true,
      crown:'M76 268 C70 122 184 58 306 58 C430 58 494 128 494 268 Z',
      brim:'M470 258 C524 244 590 254 596 286 C544 300 484 294 440 278 Z',
      under:'M440 278 C484 294 544 300 596 286 L596 292 C542 307 482 301 436 285 Z',
      bouton:[306,58],logo:{devant:[408,176],cote:[300,190],derriere:[140,205]}},
    cinq:{nom:'Cinq panneaux',
      crown:'M84 266 C90 154 190 108 300 108 C412 108 486 154 492 266 Z',
      brim:'M476 256 L596 262 L592 282 L452 276 Z',
      under:'M452 276 L592 282 L592 289 L448 283 Z',
      bouton:[300,108],logo:{devant:[404,190],cote:[262,196],derriere:[140,214]}}
  };
  var TISSUS=[['coton','Coton'],['serge','Sergé'],['maille','Maille'],['velours','Velours côtelé']];
  var POS=[['devant','Devant'],['cote','Côté'],['derriere','Derrière']];
  var TAILLES=[['s','Petit'],['m','Moyen'],['l','Grand']];
  var METHODES=[['brode','Brodé'],['patch','Patch'],['imprime','Imprimé']];
  var FERMETURES=[['snapback','Snapback'],['boucle','Boucle en métal'],['velcro','Velcro']];
  var DESSOUS=[['meme','Même couleur'],['noir','Noir'],['rose','Rose']];
  var ETIQUETTES=[['non','Aucune'],['oui','Étiquette tissée']];

  var st={forme:'dad',piece:'couronne',tissu:'coton',pos:'devant',taille:'m',methode:'brode',
          fermeture:'snapback',dessous:'meme',etiquette:'non',logo:null,
          couleurs:{couronne:'#e8dfcc',visiere:'#1d2a44',bouton:'#1d2a44',coutures:'#F59FC1'}};

  function nomDe(liste,v){for(var i=0;i<liste.length;i++){if(liste[i][0]===v||liste[i][1]===v)return liste[i][1]}return v}
  function nomCouleur(h){for(var i=0;i<COULEURS.length;i++){if(COULEURS[i][1]===h)return COULEURS[i][0]}return h}
  function seams(f){
    var b=f.bouton, y=264;
    return ['M'+b[0]+' '+b[1]+' C'+(b[0]-18)+' '+(b[1]+70)+' '+(b[0]-24)+' '+(b[1]+130)+' '+(b[0]-14)+' '+y,
            'M'+b[0]+' '+b[1]+' C'+(b[0]+44)+' '+(b[1]+66)+' '+(b[0]+64)+' '+(b[1]+126)+' '+(b[0]+68)+' '+y,
            'M'+b[0]+' '+b[1]+' C'+(b[0]-70)+' '+(b[1]+40)+' '+(b[0]-140)+' '+(b[1]+110)+' '+(b[0]-160)+' '+y];
  }

  function dessous(c){
    if(st.dessous==='noir') return '#161616';
    if(st.dessous==='rose') return '#F59FC1';
    return c.visiere;
  }

  function logoSvg(f){
    if(!st.logo) return '';
    var p=f.logo[st.pos], base={s:64,m:92,l:124}[st.taille];
    if(st.pos!=='devant') base=Math.round(base*.78);
    var w=base, h=Math.round(base*.78), x=p[0]-w/2, y=p[1]-h/2, o='';
    if(st.methode==='patch'){
      o+='<rect x="'+(x-8)+'" y="'+(y-8)+'" width="'+(w+16)+'" height="'+(h+16)+'" rx="12" fill="'+st.couleurs.coutures+'" stroke="#000" stroke-opacity=".4" stroke-width="2"/>'+
         '<rect x="'+(x-4)+'" y="'+(y-4)+'" width="'+(w+8)+'" height="'+(h+8)+'" rx="9" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="4 3"/>';
    }
    var filtre=st.methode==='brode'?' filter="url(#f-brode)"':'';
    return o+'<image href="'+st.logo+'" x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" preserveAspectRatio="xMidYMid meet"'+filtre+'/>';
  }

  function fermeture(){
    var o='';
    if(st.fermeture==='snapback') o='<rect x="58" y="246" width="56" height="20" rx="3" fill="#cfcfd2" stroke="#000" stroke-opacity=".4" stroke-width="2"/><circle cx="72" cy="256" r="3" fill="#555"/><circle cx="86" cy="256" r="3" fill="#555"/><circle cx="100" cy="256" r="3" fill="#555"/>';
    else if(st.fermeture==='boucle') o='<rect x="62" y="244" width="52" height="24" rx="2" fill="none" stroke="#b9b9bd" stroke-width="5"/><rect x="62" y="254" width="52" height="5" fill="#b9b9bd"/>';
    else o='<rect x="58" y="246" width="58" height="18" rx="2" fill="#161616" stroke="#000" stroke-opacity=".5" stroke-width="2"/><path d="M64 255H110" stroke="#6a6a6e" stroke-width="2" stroke-dasharray="3 3"/>';
    return o;
  }

  function dessin(){
    var f=FORMES[st.forme], c=st.couleurs, s='', fond='#000';
    s+='<svg viewBox="0 0 660 360" role="img" aria-label="Aperçu de ta casquette" xmlns="http://www.w3.org/2000/svg">';
    s+='<defs>'+
       '<pattern id="p-serge" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="8" stroke="#000" stroke-opacity=".22" stroke-width="2"/></pattern>'+
       '<pattern id="p-maille" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="4.5" cy="4.5" r="1.7" fill="#000" fill-opacity=".38"/></pattern>'+
       '<pattern id="p-velours" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="3.4" height="10" fill="#000" fill-opacity=".2"/></pattern>'+
       '<linearGradient id="g-vol" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".2"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></linearGradient>'+
       '<clipPath id="cl-crown"><path d="'+f.crown+'"/></clipPath><clipPath id="cl-brim"><path d="'+f.brim+'"/></clipPath>'+
       '<filter id="f-brode" x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="0" dy="1.2" stdDeviation=".7" flood-color="#000" flood-opacity=".55"/></filter>'+
       '</defs>';
    s+='<ellipse cx="335" cy="326" rx="260" ry="12" fill="#000" opacity=".45"/>';
    s+=fermeture();
    s+='<path d="'+f.under+'" fill="'+dessous(c)+'" stroke="#000" stroke-opacity=".4" stroke-width="2"/>';
    s+='<path d="'+f.brim+'" fill="'+c.visiere+'" stroke="#000" stroke-opacity=".4" stroke-width="2"/>';
    s+='<path d="'+f.crown+'" fill="'+c.couronne+'" stroke="#000" stroke-opacity=".4" stroke-width="2"/>';
    if(st.tissu!=='coton'){
      s+='<g clip-path="url(#cl-crown)"><rect x="40" y="20" width="480" height="260" fill="url(#p-'+st.tissu+')"/></g>';
      s+='<g clip-path="url(#cl-brim)"><rect x="420" y="220" width="200" height="100" fill="url(#p-'+st.tissu+')"/></g>';
    }
    if(f.mesh) s+='<g clip-path="url(#cl-crown)"><rect x="40" y="20" width="215" height="260" fill="url(#p-maille)"/><rect x="40" y="20" width="215" height="260" fill="#000" opacity=".12"/></g>';
    s+='<path d="'+f.crown+'" fill="url(#g-vol)"/>';
    var sm=seams(f);
    for(var i=0;i<sm.length;i++) s+='<path d="'+sm[i]+'" fill="none" stroke="'+c.coutures+'" stroke-width="3" stroke-linecap="round" stroke-dasharray="7 6"/>';
    s+='<circle cx="'+f.bouton[0]+'" cy="'+f.bouton[1]+'" r="12" fill="'+c.bouton+'" stroke="#000" stroke-opacity=".4" stroke-width="2"/>';
    if(st.etiquette==='oui') s+='<rect x="238" y="250" width="26" height="14" fill="#f4f4f2" stroke="#000" stroke-opacity=".4"/><path d="M243 257H259" stroke="#161616" stroke-width="2"/>';
    s+=logoSvg(f);
    s+='</svg>';
    return s;
  }

  function btn(k,v,l){return '<button type="button" class="cf-chip" data-k="'+k+'" data-v="'+v+'" aria-pressed="false">'+l+'</button>'}
  function chips(k,liste){var o='';for(var i=0;i<liste.length;i++)o+=btn(k,liste[i][0],liste[i][1]);return '<div class="cf-row">'+o+'</div>'}
  function sw(){
    var o='';
    for(var i=0;i<COULEURS.length;i++)
      o+='<button type="button" class="cf-sw" data-k="couleur" data-v="'+COULEURS[i][1]+'" aria-pressed="false" aria-label="'+COULEURS[i][0]+'" title="'+COULEURS[i][0]+'" style="--c:'+COULEURS[i][1]+'"></button>';
    return '<div class="cf-row">'+o+'</div>';
  }
  function groupe(n,titre,corps){return '<fieldset class="cf-g"><legend class="mono">'+n+' · '+titre+'</legend>'+corps+'</fieldset>'}

  root.innerHTML=
    '<div class="cf-view"><div class="cf-svg" id="cf-svg" aria-live="polite"></div>'+
      '<div class="cf-resume"><p class="mono">Ta casquette</p><ul id="cf-liste"></ul>'+
      '<a class="btn btn-rose" id="cf-soum" href="'+(document.getElementById('cf-soum')?document.getElementById('cf-soum').getAttribute('href'):'#')+'">Demander une soumission avec cette casquette <span class="arr">→</span></a>'+
      '<p class="cf-note">Aperçu de démonstration. Les formes et les tissus réels seront confirmés dans la soumission.</p></div></div>'+
    '<div class="cf-ctrl">'+
      groupe('01','La forme',chips('forme',[['dad','Dad cap'],['structuree','Structurée'],['trucker','Trucker'],['cinq','Cinq panneaux']]))+
      groupe('02','Les couleurs',chips('piece',PIECES)+sw())+
      groupe('03','Le tissu',chips('tissu',TISSUS))+
      groupe('04','Ton logo',
        '<label class="cf-fichier"><input type="file" accept="image/*" id="cf-fichier"><span>Choisir un logo</span></label>'+
        '<button type="button" class="cf-chip" id="cf-retire" hidden>Retirer le logo</button>'+
        '<p class="cf-sous mono">Méthode</p>'+chips('methode',METHODES)+
        '<p class="cf-sous mono">Emplacement</p>'+chips('pos',POS)+
        '<p class="cf-sous mono">Taille</p>'+chips('taille',TAILLES))+
      groupe('05','Les détails',
        '<p class="cf-sous mono">Fermeture</p>'+chips('fermeture',FERMETURES)+
        '<p class="cf-sous mono">Dessous de la visière</p>'+chips('dessous',DESSOUS)+
        '<p class="cf-sous mono">Étiquette</p>'+chips('etiquette',ETIQUETTES))+
    '</div>';

  var elSvg=document.getElementById('cf-svg'), elListe=document.getElementById('cf-liste'),
      elSoum=document.getElementById('cf-soum'), elRetire=document.getElementById('cf-retire');
  var base=elSoum.getAttribute('href').split('?')[0]+'?service=casquettes-100-personnalisees';

  function resume(){
    var c=st.couleurs, l=[
      ['Forme',FORMES[st.forme].nom],['Couronne',nomCouleur(c.couronne)],['Visière',nomCouleur(c.visiere)],
      ['Bouton',nomCouleur(c.bouton)],['Coutures',nomCouleur(c.coutures)],['Tissu',nomDe(TISSUS,st.tissu)],
      ['Logo',st.logo?nomDe(METHODES,st.methode)+', '+nomDe(POS,st.pos).toLowerCase()+', '+nomDe(TAILLES,st.taille).toLowerCase():'Aucun pour l’instant'],
      ['Fermeture',nomDe(FERMETURES,st.fermeture)],['Dessous de la visière',nomDe(DESSOUS,st.dessous)],['Étiquette',nomDe(ETIQUETTES,st.etiquette)]];
    return l;
  }
  function maj(){
    elSvg.innerHTML=dessin();
    var r=resume(), o='', t='Ma casquette sur mesure :\n';
    for(var i=0;i<r.length;i++){o+='<li><span>'+r[i][0]+'</span><b>'+r[i][1]+'</b></li>';t+='- '+r[i][0]+' : '+r[i][1]+'\n'}
    elListe.innerHTML=o;
    elSoum.setAttribute('href',base+'&config='+encodeURIComponent(t+(st.logo?'(Je joins mon logo dans le formulaire.)':'')));
    elRetire.hidden=!st.logo;
    var bs=root.querySelectorAll('[data-k]');
    for(var j=0;j<bs.length;j++){
      var k=bs[j].getAttribute('data-k'), v=bs[j].getAttribute('data-v'), on;
      on=k==='couleur'?st.couleurs[st.piece]===v:st[k]===v;
      bs[j].setAttribute('aria-pressed',on?'true':'false');
    }
  }

  root.addEventListener('click',function(e){
    var b=e.target.closest?e.target.closest('[data-k]'):null;
    if(b){
      var k=b.getAttribute('data-k'), v=b.getAttribute('data-v');
      if(k==='couleur') st.couleurs[st.piece]=v; else st[k]=v;
      maj(); return;
    }
    if(e.target===elRetire){st.logo=null;document.getElementById('cf-fichier').value='';maj()}
  });
  document.getElementById('cf-fichier').addEventListener('change',function(e){
    var f=e.target.files&&e.target.files[0];
    if(!f||f.type.indexOf('image/')!==0||f.size>6*1024*1024) return;
    var r=new FileReader();
    r.onload=function(){st.logo=r.result;maj()};
    r.readAsDataURL(f);
  });
  maj();
})();
