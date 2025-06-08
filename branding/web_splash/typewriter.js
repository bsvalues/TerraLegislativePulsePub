const text = 'AI That Understands Land... Frequency. Function. Fusion.';
const el = document.getElementById('typewriter');
let i = 0;
function type() {
  if (i < text.length) {
    el.innerHTML += text.charAt(i);
    i++;
    setTimeout(type, 38);
  }
}
type(); 