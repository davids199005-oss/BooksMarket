/**
 * Book detail page: favorites and "mark as read" state + API actions.
 * Requires container #book-user-actions and .book-detail-wrap[data-book-slug].
 * Runs only when localStorage has "access" token.
 */
(function () {
    'use strict';

    var BASE_PATH = (typeof window !== 'undefined' && window.location && window.location.origin) ? window.location.origin : '';
    var API_FAVORITES = BASE_PATH + '/api/me/favorites/';
    var API_READ = BASE_PATH + '/api/me/read/';

    var ICONS = {
        heartOutline: '<svg class="icon icon--btn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>',
        heartFilled: '<svg class="icon icon--btn" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>',
        check: '<svg class="icon icon--btn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>'
    };

    function getAuthHeaders() {
        var token = localStorage.getItem('access');
        if (!token) return null;
        return {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        };
    }

    function getBookSlug() {
        var wrap = document.querySelector('.book-detail-wrap');
        return wrap && wrap.getAttribute('data-book-slug') || '';
    }

    // --- API ---
    function fetchFavorites() {
        var headers = getAuthHeaders();
        if (!headers) return Promise.resolve([]);
        return fetch(API_FAVORITES, { headers: headers })
            .then(function (r) { return r.json(); })
            .catch(function () { return []; });
    }

    function fetchReadList() {
        var headers = getAuthHeaders();
        if (!headers) return Promise.resolve([]);
        return fetch(API_READ, { headers: headers })
            .then(function (r) { return r.json(); })
            .catch(function () { return []; });
    }

    function addFavorite(slug) {
        var headers = getAuthHeaders();
        if (!headers) return Promise.reject(new Error('No auth'));
        return fetch(API_FAVORITES, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ book_slug: slug })
        });
    }

    function removeFavorite(slug) {
        var headers = getAuthHeaders();
        if (!headers) return Promise.reject(new Error('No auth'));
        return fetch(API_FAVORITES + encodeURIComponent(slug) + '/', {
            method: 'DELETE',
            headers: headers
        });
    }

    function addRead(slug) {
        var headers = getAuthHeaders();
        if (!headers) return Promise.reject(new Error('No auth'));
        return fetch(API_READ, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ book_slug: slug })
        });
    }

    function removeRead(slug) {
        var headers = getAuthHeaders();
        if (!headers) return Promise.reject(new Error('No auth'));
        return fetch(API_READ + encodeURIComponent(slug) + '/', {
            method: 'DELETE',
            headers: headers
        });
    }

    // --- UI state ---
    function updateFavoriteButton(btn, added) {
        if (!btn) return;
        btn.classList.toggle('is-added', added);
        btn.innerHTML = (added ? ICONS.heartFilled : ICONS.heartOutline) +
            (added ? ' In favorites (remove)' : ' Add to favorites');
        btn.setAttribute('aria-label', added ? 'Remove from favorites' : 'Add to favorites');
    }

    function updateReadButton(btn, added) {
        if (!btn) return;
        btn.classList.toggle('is-added', added);
        btn.innerHTML = ICONS.check + (added ? ' Marked as read (remove)' : ' Mark as read');
        btn.setAttribute('aria-label', added ? 'Remove from read list' : 'Mark as read');
    }

    // --- Init ---
    function bindFavoriteButton(btn, bookSlug, state) {
        if (!btn) return;
        btn.addEventListener('click', function () {
            if (btn.disabled) return;
            btn.disabled = true;
            var next = !state.inFavorites;
            var promise = next ? addFavorite(bookSlug) : removeFavorite(bookSlug);
            promise
                .then(function (r) {
                    if (next && r.ok) {
                        state.inFavorites = true;
                    } else if (!next && r.status === 204) {
                        state.inFavorites = false;
                    }
                    updateFavoriteButton(btn, state.inFavorites);
                })
                .catch(function () { updateFavoriteButton(btn, state.inFavorites); })
                .finally(function () { btn.disabled = false; });
        });
    }

    function bindReadButton(btn, bookSlug, state) {
        if (!btn) return;
        btn.addEventListener('click', function () {
            if (btn.disabled) return;
            btn.disabled = true;
            var next = !state.inRead;
            var promise = next ? addRead(bookSlug) : removeRead(bookSlug);
            promise
                .then(function (r) {
                    if (next && r.ok) {
                        state.inRead = true;
                    } else if (!next && r.status === 204) {
                        state.inRead = false;
                    }
                    updateReadButton(btn, state.inRead);
                })
                .catch(function () { updateReadButton(btn, state.inRead); })
                .finally(function () { btn.disabled = false; });
        });
    }

    function init() {
        var token = localStorage.getItem('access');
        if (!token) return;

        var wrap = document.getElementById('book-user-actions');
        if (!wrap) return;

        var bookSlug = getBookSlug();
        if (!bookSlug) return;

        wrap.classList.add('is-visible');

        var btnFav = document.getElementById('btn-favorite');
        var btnRead = document.getElementById('btn-read');
        var state = { inFavorites: false, inRead: false };

        Promise.all([fetchFavorites(), fetchReadList()]).then(function (results) {
            var favList = Array.isArray(results[0]) ? results[0] : [];
            var readList = Array.isArray(results[1]) ? results[1] : [];
            state.inFavorites = favList.some(function (b) { return b.slug === bookSlug; });
            state.inRead = readList.some(function (b) { return b.slug === bookSlug; });
            updateFavoriteButton(btnFav, state.inFavorites);
            updateReadButton(btnRead, state.inRead);
        });

        bindFavoriteButton(btnFav, bookSlug, state);
        bindReadButton(btnRead, bookSlug, state);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
