// attaches events to menu
function openLink(url) {
  window.open(url, '_blank', 'noopener');
}

// Search and Filter
// toggle collapse box arrows
function toggleDropArrow(itemID) {
  const el = document.getElementById(itemID);
  const icon = el.getElementsByTagName('span');
  if (icon[0].classList.contains('arrow')) {
    if (icon[0].classList.contains('down')) {
      icon[0].classList.remove('down');
      icon[0].innerHTML = 'arrow_right';
    } else {
      icon[0].classList.add('down');
      icon[0].innerHTML = 'arrow_drop_down';
    }
  }
}