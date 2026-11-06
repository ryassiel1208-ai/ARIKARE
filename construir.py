import os,json,shutil
from PIL import Image,ImageDraw
v=os.environ['VARIANTE']  # lector | admin
ADMIN=(v=='admin')

# ---- 1) Página web -> www/index.html (con el puente nativo para Android)
html=open('Ka-Ngabere-%s.html'%v.capitalize(),encoding='utf-8').read()
SHIM="""<script>
(function(){
 var C=window.Capacitor;
 if(!C||!C.isNativePlatform||!C.isNativePlatform())return;
 var P=C.Plugins||{};
 window.AndroidBridge={
  pantalla:function(on){try{if(P.StatusBar){on?P.StatusBar.hide():P.StatusBar.show()}}catch(e){}},
  guardar:function(nm,txt){
   var F=P.Filesystem,S=P.Share;
   function fallo(){alert('No se pudo exportar el respaldo.')}
   if(F&&S){
    F.writeFile({path:nm,data:txt,directory:'CACHE',encoding:'utf8'})
     .then(function(r){return S.share({title:nm,url:r.uri,dialogTitle:'Guardar respaldo'})})
     .catch(function(){S.share({title:nm,text:txt}).catch(fallo)});
   }else if(S){S.share({title:nm,text:txt}).catch(fallo)}else fallo();
  }
 };
 if(P.App)P.App.addListener('backButton',function(){
  var h=false;try{h=window.atras&&window.atras()}catch(e){}
  if(!h)P.App.exitApp();
 });
})();
</script>
"""
assert html.count('<script>')==1
html=html.replace('<script>',SHIM+'<script>',1)
shutil.rmtree('www',ignore_errors=True);os.makedirs('www')
open('www/index.html','w',encoding='utf-8').write(html)

# ---- 2) Nombre e identificador de la app
cfg=json.load(open('capacitor.config.json',encoding='utf-8'))
cfg['appId']='com.ngabere.himnario.admin' if ADMIN else 'com.ngabere.himnario'
cfg['appName']='Ka Ngäbere Admin' if ADMIN else 'Ka Ngäbere'
json.dump(cfg,open('capacitor.config.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)

# ---- 3) Iconos (1024 px) para @capacitor/assets
S=1024
big=Image.open('icono-%s-512.png'%v).convert('RGBA').resize((S,S),Image.LANCZOS)
rgb=big.convert('RGB')
shutil.rmtree('assets',ignore_errors=True);os.makedirs('assets')
# icono completo con esquinas redondeadas transparentes
m=Image.new('L',(S,S),0);ImageDraw.Draw(m).rounded_rectangle([0,0,S-1,S-1],radius=int(S*.22),fill=255)
only=big.copy();only.putalpha(m);only.save('assets/icon-only.png')
# fondo liso del color del borde + primer plano sin las esquinas negras
pts=[(120,512),(904,512),(512,120),(512,904)]
bg=tuple(sum(rgb.getpixel(p)[i] for p in pts)//4 for i in range(3))
Image.new('RGB',(S,S),bg).save('assets/icon-background.png')
inner=rgb.crop((90,90,S-90,S-90));k=int(S*.62)
fg=Image.new('RGBA',(S,S),(0,0,0,0));fg.paste(inner.resize((k,k),Image.LANCZOS),((S-k)//2,(S-k)//2));fg.save('assets/icon-foreground.png')
print('preparado:',v,cfg['appId'],cfg['appName'],'fondo',bg)
