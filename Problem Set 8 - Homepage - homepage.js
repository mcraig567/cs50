/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function myFunction() {
  document.getElementById("dropdown").classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}

function backgroundToggle() {
  let bg = document.querySelector('.bg')
  if (bg.style.visibility === 'hidden') {
    bg.style.visibility = 'visible';
    bg.style.height = '50%';
  }
  else {
    bg.style.visibility = 'hidden';
    bg.style.height = '0%';
  }
}
