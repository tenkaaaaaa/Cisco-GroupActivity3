function initMap(mapCoords, startCoord, endCoord) {
    // Initialize Map
    var map = L.map('map').setView(startCoord, 10);
    
      // Dark theme map (Free, no API key required)
    L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', {
        maxZoom: 20,
        attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);

    
    // Custom Neon Markers
    var greenIcon = L.divIcon({
        className: 'custom-icon',
        html: '<div style="background-color: #00ffcc; width: 15px; height: 15px; border-radius: 50%; box-shadow: 0 0 10px #00ffcc;"></div>',
        iconSize: [15, 15]
    });
    
    var pinkIcon = L.divIcon({
        className: 'custom-icon',
        html: '<div style="background-color: #ff00cc; width: 15px; height: 15px; border-radius: 50%; box-shadow: 0 0 10px #ff00cc;"></div>',
        iconSize: [15, 15]
    });
    
    // Add Start and End Markers
    L.marker(startCoord, {icon: greenIcon}).addTo(map).bindPopup("Start");
    L.marker(endCoord, {icon: pinkIcon}).addTo(map).bindPopup("Destination");
    
    // Draw the Route Line
    var routeLine = L.polyline(mapCoords, {
        color: '#00f2fe', 
        weight: 5,
        opacity: 0.8,
        lineJoin: 'round'
    }).addTo(map);
    
    // Zoom the map to fit the route
    map.fitBounds(routeLine.getBounds(), {padding: [50, 50]});
}