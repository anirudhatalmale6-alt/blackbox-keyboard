#!/usr/bin/env python3
"""Add inline onscreen keyboard to login.html"""

KEYBOARD_SCRIPT = '''<script>
/* On-Screen Keyboard */
(function(){
var ai=null,sh=false;
var kb=document.createElement('div');
kb.id='osk-overlay';
kb.style.cssText='display:none;position:fixed;bottom:0;left:0;width:100%;z-index:9999;background:#111;border-top:2px solid #c00;padding:5px;box-sizing:border-box;';
var rows=[['1','2','3','4','5','6','7','8','9','0'],['Q','W','E','R','T','Y','U','I','O','P'],['A','S','D','F','G','H','J','K','L','@'],['SHIFT','Z','X','C','V','B','N','M','.','DEL'],['SPACE','DONE']];
var h='';
for(var r=0;r<rows.length;r++){
h+='<div style="display:flex;gap:3px;margin-bottom:3px;justify-content:center;">';
for(var k=0;k<rows[r].length;k++){
var ky=rows[r][k];var w='9%',fs='14px';
if(ky=='SPACE')w='60%';else if(ky=='DONE')w='35%';else if(ky=='SHIFT'||ky=='DEL'){w='14%';fs='11px';}
var bg='#222',bc='#600',tc='#fff';
if(ky=='DONE'){bg='#030';bc='#0c0';tc='#0c0';}
else if(ky=='DEL'){bg='#300';bc='#c00';tc='#c00';}
else if(ky=='SHIFT'){bg='#220';bc='#660';tc='#fc0';}
var lb=ky;
if(ky=='SPACE')lb='SPATIE';else if(ky=='DEL')lb='WISSEN';else if(ky=='DONE')lb='KLAAR';else if(ky=='SHIFT')lb='A/a';
h+='<button type="button" data-key="'+ky+'" style="width:'+w+';height:42px;background:'+bg+';border:1px solid '+bc+';color:'+tc+';font-size:'+fs+';font-weight:bold;border-radius:4px;touch-action:manipulation;">'+lb+'</button>';
}
h+='</div>';
}
kb.innerHTML=h;
document.body.appendChild(kb);
function pk(key){
if(!ai)return;
if(key=='DONE'){hk();return;}
if(key=='DEL'){ai.value=ai.value.slice(0,-1);fi();return;}
if(key=='SHIFT'){sh=!sh;us();return;}
if(key=='SPACE')ai.value+=' ';
else ai.value+=sh?key.toUpperCase():key.toLowerCase();
fi();
}
function fi(){if(ai){var e=new Event('input',{bubbles:true});ai.dispatchEvent(e);}}
kb.addEventListener('touchstart',function(e){
var b=e.target.closest?e.target.closest('button'):e.target;
if(b&&b.tagName=='BUTTON'){e.preventDefault();e.stopPropagation();pk(b.getAttribute('data-key'));}
},{passive:false});
kb.addEventListener('mousedown',function(e){
var b=e.target.closest?e.target.closest('button'):e.target;
if(b&&b.tagName=='BUTTON'){e.preventDefault();e.stopPropagation();pk(b.getAttribute('data-key'));}
});
function us(){
var bs=kb.querySelectorAll('button');
for(var i=0;i<bs.length;i++){var k=bs[i].getAttribute('data-key');if(k&&k.length==1&&k.match(/[A-Z]/))bs[i].textContent=sh?k.toUpperCase():k.toLowerCase();}
var sb=kb.querySelector('[data-key="SHIFT"]');if(sb)sb.style.background=sh?'#440':'#220';
}
function sk(inp){ai=inp;kb.style.display='block';}
function hk(){kb.style.display='none';ai=null;}
var ins=document.querySelectorAll('input[type="text"],input[type="password"]');
for(var i=0;i<ins.length;i++){
ins[i].setAttribute('inputmode','none');
ins[i].addEventListener('touchstart',function(e){e.preventDefault();sk(this);this.focus();},{passive:false});
ins[i].addEventListener('mousedown',function(e){e.preventDefault();sk(this);this.focus();});
}
document.addEventListener('touchstart',function(e){
if(kb.style.display=='block'&&!kb.contains(e.target)&&e.target!==ai)hk();
});
us();
})();
</script>'''

import os

for path in ['/var/www/html/theblackbox/login.html', '/opt/theblackbox/html/login.html']:
    if not os.path.exists(path):
        print(f"SKIP: {path} not found")
        continue

    with open(path, 'r') as f:
        content = f.read()

    # Remove any old external keyboard script references
    content = content.replace('<script src="onscreen-keyboard.js"></script>\n', '')
    content = content.replace('<script src="onscreen-keyboard.js"></script>', '')
    content = content.replace('<script src="kb-test.js"></script>\n', '')
    content = content.replace('<script src="kb-test.js"></script>', '')
    content = content.replace('<script>document.title="KB LOADED";</script>\n', '')
    content = content.replace('<script>document.title="KB LOADED";</script>', '')

    # Remove any previously added inline keyboard
    if 'osk-overlay' in content:
        # Find and remove old inline keyboard script
        start = content.find('<script>\n/* On-Screen Keyboard */')
        if start == -1:
            start = content.find('<script>\n(function(){var ai=')
        if start > -1:
            end = content.find('</script>', start)
            if end > -1:
                content = content[:start] + content[end+9:]

    # Clean up extra blank lines before </body>
    while '\n\n\n</body>' in content:
        content = content.replace('\n\n\n</body>', '\n\n</body>')

    # Add keyboard before </body>
    content = content.replace('</body>', KEYBOARD_SCRIPT + '\n</body>')

    with open(path, 'w') as f:
        f.write(content)

    print(f"OK: {path}")

print("Done! Run: sudo bash /opt/theblackbox/restart.sh")
