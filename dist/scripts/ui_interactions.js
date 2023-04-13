// attaches events to menu
function logout() {
  window.open('?gcp-iap-mode=CLEAR_LOGIN_COOKIE', '_self');
};
function openLink(url) {
  window.open(url, '_blank', 'noopener');
}

// toggle About text
function toggleBtnShow() {
  const el = document.getElementById('btnShow');
  if (el.innerHTML.includes('expand_more')) {
    el.innerHTML = 'Show Less<span class="material-symbols-outlined" data-toggle="collapse" data-target="#collapseAbout">expand_less</span>';
  } else {
    el.innerHTML = 'Show More<span class="material-symbols-outlined" data-toggle="collapse" data-target="#collapseAbout">expand_more</span>';
  }
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