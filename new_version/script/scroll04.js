var x = 0;
var dest = 0;
var distance = 0;
var step = 0;
var destination = 0; 
function scrollit(destination) {
step = 3;
dest = destination;
if (x<dest) {
while (x<dest) {
step += (step / 40);
x += step;
this.frames.mainF.scroll(x,0);
} 
this.frames.mainF.scroll(dest,0);
x = dest;
}

if (x > dest) {
while (x>dest) {
step += (step / 40);
if(x >= (0+step))
{
x -= step; 
this.frames.mainF.scroll(x,0);
}
else { break; }
} 
if(dest >= 0) { this.frames.mainF.scroll(dest,0); }
x = dest;
} 
if (x<1) {x=1}
if (x>2600) {x=1950} 
}

