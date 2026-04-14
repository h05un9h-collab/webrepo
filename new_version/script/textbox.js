var sRepeat=null;
function doScrollerIE(dir, src, amount) {
	if (amount==null) amount=10;
	if (dir=="up")
		document.all[src].scrollTop-=amount;
	else
		document.all[src].scrollTop+=amount;
	if (sRepeat==null)
		sRepeat = setInterval("doScrollerIE('" + dir + "','" + src + "'," + amount + ")",100);
	return false
}
window.document.onmouseout = new Function("clearInterval(sRepeat);sRepeat=null");
window.document.ondragstart = new Function("return false");