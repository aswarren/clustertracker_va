// attaches events to menu
function logout() {
  window.open('?gcp-iap-mode=CLEAR_LOGIN_COOKIE', '_self');
};

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

// map button dropdown
function showList() {
  document.getElementById('myDropdown').classList.toggle('show');
}
function hideMapTimeBtns() {
  const dropdowns = document.getElementsByClassName('dropdown-content');
  for (let i = 0; i < dropdowns.length; i++) {
    if (dropdowns[i].classList.contains('show')) {
      dropdowns[i].classList.remove('show');
    }
  }
}
