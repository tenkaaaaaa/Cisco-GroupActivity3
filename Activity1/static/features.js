(function () {
    // ---------- Settings you can edit ----------
    // Gasoline (RON 91) common price in Metro Manila, PHP per liter.
    // Source: DOE-based weekly estimates, Nov 3-9, 2026. Pump prices change weekly, so update this number.
    var FUEL_PRICE_PER_LITER = 86.80;
    // Typical fuel economy of a car. Change to match your vehicle.
    var CAR_KM_PER_LITER = 12;

    var KM_PER_MILE = 1.609344;

    var QUOTES = [
        { text: 'A journey of a thousand miles begins with a single step.', author: 'Lao Tzu' },
        { text: 'The world is a book, and those who do not travel read only one page.', author: 'Saint Augustine' },
        { text: 'I travel not to go anywhere, but to go. I travel for travel\u2019s sake.', author: 'Robert Louis Stevenson' },
        { text: 'Every day is a journey, and the journey itself is home.', author: 'Matsuo Bash\u014d' },
        { text: 'Travel makes one modest. You see what a tiny place you occupy in the world.', author: 'Gustave Flaubert' },
        { text: 'To travel is to live.', author: 'Hans Christian Andersen' },
        { text: 'Adventure is worthwhile in itself.', author: 'Amelia Earhart' }
    ];

    // Words that signal toll roads or major highways in the turn-by-turn text
    var TOLL_PATTERN = /\b(toll|tollway|tollgate|expressway|skyway|slex|nlex|tplex|sctex|calax|cavitex|cclex|clex|star tollway|e[1-6])\b/i;
    var HIGHWAY_PATTERN = /\b(highway|diversion road|maharlika|national road|circumferential|radial road|c-?[1-6]|r-?(?:10|[1-9])|ah\d+)\b/i;

    // ---------- Quote of the session ----------
    // Picked at random the first time the site is opened, then kept for the rest of the session.
    function showQuote() {
        var box = document.getElementById('quote');
        if (!box) return;

        var index = null;
        try {
            var saved = sessionStorage.getItem('quoteIndex');
            if (saved !== null && QUOTES[+saved]) index = +saved;
        } catch (e) { /* storage unavailable */ }

        if (index === null) {
            index = Math.floor(Math.random() * QUOTES.length);
            try { sessionStorage.setItem('quoteIndex', index); } catch (e) { /* ignore */ }
        }

        document.getElementById('quote-text').textContent = '\u201C' + QUOTES[index].text + '\u201D';
        document.getElementById('quote-author').textContent = '\u2014 ' + QUOTES[index].author;
        box.hidden = false;
    }

    // ---------- Helpers ----------
    function parseDistance(text) {
        var m = /([\d,]*\.?\d+)\s*(km|mi)/i.exec(text || '');
        if (!m) return null;
        var value = parseFloat(m[1].replace(/,/g, ''));
        var unit = m[2].toLowerCase();
        return { value: value, unit: unit, km: unit === 'mi' ? value * KM_PER_MILE : value };
    }

    function parseSeconds(text) {
        var m = /^\s*(\d+):(\d{2})(?::(\d{2}))?\s*$/.exec(text || '');
        if (!m) return null;
        if (m[3] !== undefined) return (+m[1]) * 3600 + (+m[2]) * 60 + (+m[3]);
        return (+m[1]) * 60 + (+m[2]);
    }

    function pad(n) { return (n < 10 ? '0' : '') + n; }

    function formatSeconds(total) {
        var h = Math.floor(total / 3600);
        var m = Math.floor((total % 3600) / 60);
        var s = Math.round(total % 60);
        return pad(h) + ':' + pad(m) + ':' + pad(s);
    }

    function peso(amount) {
        return '\u20B1' + Math.round(amount).toLocaleString('en-PH');
    }

    function setText(id, text) {
        var el = document.getElementById(id);
        if (el) el.textContent = text;
    }

    // ---------- Fuel cost + round trip ----------
    function renderCostAndRoundTrip(vehicle) {
        var distanceEl = document.querySelector('.metric:nth-child(1)');
        var timeEl = document.querySelector('.metric:nth-child(2)');
        var distText = distanceEl ? distanceEl.childNodes[distanceEl.childNodes.length - 1].textContent.trim() : '';
        var timeText = timeEl ? timeEl.childNodes[timeEl.childNodes.length - 1].textContent.trim() : '';

        var dist = parseDistance(distText);
        var seconds = parseSeconds(timeText);

        // Round trip
        if (dist) {
            var rtValue = (dist.value * 2).toFixed(1);
            setText('rt-distance', rtValue + ' ' + dist.unit);
        } else {
            setText('rt-distance', '2 \u00D7 ' + distText);
        }
        setText('rt-time', seconds !== null
            ? 'About ' + formatSeconds(seconds * 2) + ' of driving there and back (' + distText + ' each way).'
            : 'Twice the one-way trip.');

        // Fuel cost (cars only)
        if (vehicle !== 'car') {
            setText('cost-oneway', 'Car only');
            setText('cost-note', 'Fuel cost is estimated for car routes. Pick Car to see it.');
            return;
        }
        if (!dist) {
            setText('cost-oneway', 'Unavailable');
            return;
        }

        var liters = dist.km / CAR_KM_PER_LITER;
        var oneWay = liters * FUEL_PRICE_PER_LITER;
        setText('cost-oneway', peso(oneWay));
        setText('cost-note',
            'One way. Round trip is about ' + peso(oneWay * 2) + '. ' +
            'Based on ' + CAR_KM_PER_LITER + ' km/L and \u20B1' + FUEL_PRICE_PER_LITER.toFixed(2) + ' per liter of gasoline.');
    }

    // ---------- Smart route warnings ----------
    function renderWarnings() {
        var list = document.getElementById('warn-list');
        if (!list) return;

        var steps = document.querySelectorAll('.steps .step-text');
        var found = [];
        var seen = {};

        steps.forEach(function (el, i) {
            var text = el.textContent.trim();
            var type = TOLL_PATTERN.test(text) ? 'toll' : (HIGHWAY_PATTERN.test(text) ? 'highway' : null);
            if (!type || seen[text]) return;
            seen[text] = true;
            found.push({ type: type, step: i + 1, text: text });
        });

        list.innerHTML = '';

        if (!found.length) {
            var ok = document.createElement('li');
            ok.className = 'ok';
            ok.textContent = 'No toll roads or major highways found in these directions.';
            list.appendChild(ok);
            return;
        }

        // Toll roads first, then highways
        found.sort(function (a, b) { return (a.type === 'toll' ? 0 : 1) - (b.type === 'toll' ? 0 : 1); });

        found.slice(0, 4).forEach(function (w) {
            var li = document.createElement('li');
            var tag = document.createElement('span');
            tag.className = 'tag tag-' + w.type;
            tag.textContent = w.type === 'toll' ? 'Toll road' : 'Major highway';
            var msg = document.createElement('span');
            msg.textContent = 'Step ' + w.step + ': ' + w.text;
            li.appendChild(tag);
            li.appendChild(msg);
            list.appendChild(li);
        });

        if (found.length > 4) {
            var more = document.createElement('li');
            more.className = 'ok';
            more.textContent = '+' + (found.length - 4) + ' more in the directions.';
            list.appendChild(more);
        }

        if (found.some(function (w) { return w.type === 'toll'; })) {
            var tip = document.createElement('li');
            tip.className = 'ok';
            tip.textContent = 'Toll fees are not included in the fuel cost. Keep your RFID tag or cash ready.';
            list.appendChild(tip);
        }
    }

    // ---------- Start ----------
    showQuote();

    var insights = document.getElementById('insights');
    if (insights) {
        renderCostAndRoundTrip(insights.getAttribute('data-vehicle') || 'car');
        renderWarnings();
    }
})();