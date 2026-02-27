/**
 * Mobile nav: toggle menu (hamburger), close on outside click or link click.
 */
(function () {
    'use strict';

    var nav = document.querySelector('.nav');
    var toggle = document.querySelector('.nav-toggle');
    var list = document.getElementById('nav-list');

    if (!nav || !toggle || !list) return;

    function open() {
        nav.classList.add('is-open');
        toggle.setAttribute('aria-expanded', 'true');
        toggle.setAttribute('aria-label', 'Close menu');
    }

    function close() {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('aria-label', 'Open menu');
    }

    toggle.addEventListener('click', function () {
        if (nav.classList.contains('is-open')) {
            close();
        } else {
            open();
        }
    });

    document.addEventListener('click', function (e) {
        if (!nav.classList.contains('is-open')) return;
        if (nav.contains(e.target)) return;
        close();
    });

    list.addEventListener('click', function (e) {
        if (e.target.closest('a')) close();
    });
})();
