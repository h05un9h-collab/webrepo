menuNoClass="menuNo";
menuOverClass="menuOver";
menuClickClass="menuClick";

function menuBG_out(obj) {
if (obj.className==menuClickClass) return;
else obj.className=menuNoClass;
}
function menuBG_over(obj) {
if (obj.className==menuClickClass) return;
else obj.className=menuOverClass;
}
function menuBG_click(obj) {
if (obj.className==menuClickClass) return;
else {
for(i=0;i<menuTr.length;i++){
menuTr(i).className=menuNoClass
}
obj.className=menuClickClass;
}
return;
}
