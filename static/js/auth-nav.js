/**
 * Nav auth state: show/hide login, register, logout by access token.
 * Logout click: POST refresh to API, clear tokens, redirect to home.
 * Expects window.APP_CONFIG = { homeUrl: string, logoutApiPath: string }.
 */
(function () {
    var config = window.APP_CONFIG || {};
    var homeUrl = config.homeUrl || '/';
    var logoutApiPath = config.logoutApiPath || '/api/auth/logout/';

    var hasToken = !!localStorage.getItem('access');
    var loginLi = document.getElementById('nav-login');
    var registerLi = document.getElementById('nav-register');
    var logoutLi = document.getElementById('nav-logout');
    var logoutLink = document.getElementById('nav-logout-link');

    if (hasToken) {
        if (loginLi) loginLi.style.display = 'none';
        if (registerLi) registerLi.style.display = 'none';
        if (logoutLi) logoutLi.classList.add('is-visible');
    } else {
        if (loginLi) loginLi.style.display = '';
        if (registerLi) registerLi.style.display = '';
        if (logoutLi) logoutLi.classList.remove('is-visible');
    }

    if (logoutLink) {
        logoutLink.addEventListener('click', function (e) {
            e.preventDefault();
            var refresh = localStorage.getItem('refresh');
            if (refresh) {
                var url = (window.location.origin || '') + logoutApiPath;
                fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh: refresh })
                }).catch(function () {});
            }
            localStorage.removeItem('access');
            localStorage.removeItem('refresh');
            window.location.href = homeUrl;
        });
    }
})();
