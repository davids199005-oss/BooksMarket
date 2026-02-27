/**
 * Global toast notifications. Requires #toast-container in DOM.
 * Usage: showToast('Message text');
 */
(function () {
    'use strict';

    var CONTAINER_ID = 'toast-container';
    var TOAST_DURATION_MS = 3000;

    function getContainer() {
        return document.getElementById(CONTAINER_ID);
    }

    window.showToast = function (text) {
        var container = getContainer();
        if (!container || !text) return;

        var el = document.createElement('div');
        el.className = 'toast';
        el.setAttribute('role', 'status');
        el.textContent = text;

        function dismiss() {
            el.classList.add('is-hidden');
            setTimeout(function () {
                if (el.parentNode) el.parentNode.removeChild(el);
            }, 260);
        }

        el.addEventListener('click', dismiss);

        var timeout = setTimeout(dismiss, TOAST_DURATION_MS);

        el.addEventListener('mouseenter', function () {
            clearTimeout(timeout);
        });
        el.addEventListener('mouseleave', function () {
            timeout = setTimeout(dismiss, TOAST_DURATION_MS);
        });

        container.appendChild(el);
    };
})();
