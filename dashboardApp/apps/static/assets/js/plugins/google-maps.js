function initMap() {
    var defaultLocation = { lat: -6.2088, lng: 106.8456 }; // Jakarta

    var map = new google.maps.Map(document.getElementById('map'), {
        center: defaultLocation,
        zoom: 15
    });

    var marker = new google.maps.Marker({
        position: defaultLocation,
        map: map,
        draggable: true
    });

    // Event saat peta diklik
    google.maps.event.addListener(map, 'click', function(event) {
        var clickedLocation = event.latLng;
        marker.setPosition(clickedLocation);
        document.getElementById('alamat_maps').value = clickedLocation.lat() + ', ' + clickedLocation.lng();
    });

    // Event saat marker digeser
    google.maps.event.addListener(marker, 'dragend', function(event) {
        document.getElementById('alamat_maps').value = event.latLng.lat() + ', ' + event.latLng.lng();
    });
}