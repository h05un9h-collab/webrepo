// assets/js/nav.js
document.addEventListener('DOMContentLoaded', function () {
  var path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(function (link) {
    var href = link.getAttribute('href');
    if (href && path.indexOf(href.replace(/^(\.\.\/)+/, '').replace(/\/$/, '')) !== -1) {
      link.classList.add('active');
    }
  });
});
