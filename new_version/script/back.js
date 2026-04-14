function setVariables() { 
if (navigator.appName == "Netscape") { 
v=".top="; 
dS="document."; 
sD=""; 
y="window.pageYOffset"; 
} 
else { 
v=".pixelTop="; 
dS=""; 
sD=".style"; 
y="document.body.scrollTop"; 
  } 
} 
function checkLocation() { 
object="object1"; 
yy=eval(y); 
eval(dS+object+sD+v+yy); 
setTimeout("checkLocation()",10); 
} 
