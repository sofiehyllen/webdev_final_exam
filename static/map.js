var map = L.map('map', {
  center: [55.6845, 12.564148],  
  zoom: 13,                   
  maxBounds: L.latLngBounds([54.5, 8.1], [57.8, 14]), 
  maxBoundsViscosity: 1.0
});

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
  maxZoom: 20,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


// Create a custom icon for the marker
var customIcon = L.icon({
  iconUrl: 'static/svg/pin.svg', 
  iconSize: [32, 32], 
  iconAnchor: [16, 32], 
  popupAnchor: [0, -32] 
});

// Marker cluster group 
var markers = L.markerClusterGroup();

// Add loading message
var loadingMessage = L.control({ position: 'topright' });
loadingMessage.onAdd = function () {
  var div = L.DomUtil.create('div', 'loading');
  div.innerHTML = 'Loading markers...';
  return div;
};
loadingMessage.addTo(map);

// Function to fetch and load markers asynchronously
function loadMarkers() {
  fetch('/map-locations')
      .then(response => {
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          return response.json();
      })
      .then(markerLocations => {
          // For each location, immediately add a marker
          markerLocations.forEach(function (location) {
              // Only add the marker if the coordinates are valid
              if (location.coords[0] !== null && location.coords[1] !== null) {
                  var marker = L.marker(location.coords, { icon: customIcon })
                      .bindPopup(location.popup);
                  
                  // Add the marker to the cluster group (or directly to the map if no clustering)
                  markers.addLayer(marker);
              } else {
                  console.log("Geocoding failed for:", location.popup);
              }
          });
          // Add the markers to the map (this will add them as they are loaded)
          map.addLayer(markers);

          // Remove the loading message after markers are loaded
          map.removeControl(loadingMessage);
      })
      .catch(error => {
          console.error('Error fetching marker locations:', error);
          map.removeControl(loadingMessage);
      });
}

// Load markers when the map is ready
loadMarkers();