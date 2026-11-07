function initMap(mapCoords, startCoord, endCoord) {
    var map = L.map('map').setView(startCoord, 10);

    // OpenStreetMap tiles (no API key needed)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Route: white casing underneath an orange line, so it stands out on any map color
    var casing = L.polyline(mapCoords, {
        color: '#ffffff', weight: 10, opacity: 0.95, lineCap: 'round', lineJoin: 'round', interactive: false
    }).addTo(map);

    L.polyline(mapCoords, {
        color: '#d9461c', weight: 5, opacity: 1, lineCap: 'round', lineJoin: 'round', interactive: false
    }).addTo(map);

    // Pins (styled in style.css): dark = start, orange = destination
    function pin(type) {
        return L.divIcon({
            className: 'pin pin-' + type,
            html: '<span></span>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
    }

    L.marker(startCoord, { icon: pin('start') }).addTo(map).bindPopup('Start location');
    L.marker(endCoord, { icon: pin('end') }).addTo(map).bindPopup('Destination');

    // Fit the map to the route
    map.fitBounds(casing.getBounds(), { padding: [50, 50] });
}