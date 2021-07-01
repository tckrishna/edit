class MapsHandler {
    constructor(map_id, search_id, api_key, libraries=[], default_center={lat: 0.0, lng: 0.0}, default_zoom=0, map_blindspot={top: 0, bottom: 0, left: 0, right: 0}, map_listeners={}, marker=false, marker_callback=null) {
        this.map_id = map_id;
        this.search_id = search_id;
        this.api_key = api_key;
        this.libraries = ['places'].concat(libraries);
        this.default_zoom = default_zoom;
        this.default_center = default_center;
        this.map_blindspot = map_blindspot;
        this.map_listeners = map_listeners;
        this.marker = marker;
        this.marker_callback = marker_callback;
        this.selected_marker = undefined;

        this.MAP_STYLE = [
            {"elementType":"geometry","stylers":[{"color":"#ebe3cd"}]},
            {"elementType":"labels.text.fill","stylers":[{"color":"#523735"}]},
            {"elementType":"labels.text.stroke","stylers":[{"color":"#f5f1e6"}]},
            {"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#c9b2a6"}]},
            {"featureType":"administrative.land_parcel","elementType":"geometry.stroke","stylers":[{"color":"#dcd2be"}]},
            {"featureType":"administrative.land_parcel","elementType":"labels.text.fill","stylers":[{"color":"#ae9e90"}]},
            {"featureType":"landscape.natural","elementType":"geometry","stylers":[{"color":"#dfd2ae"}]},
            {"featureType":"poi","elementType":"geometry","stylers":[{"color":"#dfd2ae"}]},
            {"featureType":"poi","elementType":"labels.text.fill","stylers":[{"color":"#93817c"}]},
            {"featureType":"poi.business","stylers":[{"visibility":"off"}]},
            {"featureType":"poi.park","elementType":"geometry.fill","stylers":[{"color":"#a5b076"}]},
            {"featureType":"poi.park","elementType":"labels.text","stylers":[{"visibility":"off"}]},
            {"featureType":"poi.park","elementType":"labels.text.fill","stylers":[{"color":"#447530"}]},
            {"featureType":"road","elementType":"geometry","stylers":[{"color":"#f5f1e6"}]},
            {"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#fdfcf8"}]},
            {"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#f8c967"}]},
            {"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#e9bc62"}]},
            {"featureType":"road.highway.controlled_access","elementType":"geometry","stylers":[{"color":"#e98d58"}]},
            {"featureType":"road.highway.controlled_access","elementType":"geometry.stroke","stylers":[{"color":"#db8555"}]},
            {"featureType":"road.local","elementType":"labels.text.fill","stylers":[{"color":"#806b63"}]},
            {"featureType":"transit.line","elementType":"geometry","stylers":[{"color":"#dfd2ae"}]},
            {"featureType":"transit.line","elementType":"labels.text.fill","stylers":[{"color":"#8f7d77"}]},
            {"featureType":"transit.line","elementType":"labels.text.stroke","stylers":[{"color":"#ebe3cd"}]},
            {"featureType":"transit.station","elementType":"geometry","stylers":[{"color":"#dfd2ae"}]},
            {"featureType":"water","elementType":"geometry.fill","stylers":[{"color":"#b9d3c2"}]},
            {"featureType":"water","elementType":"labels.text.fill","stylers":[{"color":"#92998d"}]}
        ]

    }

    initMap(center, zoom) {
        if (center == undefined || zoom == undefined) {
            center = this.default_center;
            zoom = this.default_zoom;
        }
        var options = {
            center: center,
            zoom: zoom,
            maxZoom: 16,
            styles: this.MAP_STYLE,
            zoomControl: true,
            zoomControlOptions: {
                position: google.maps.ControlPosition.RIGHT_CENTER,
            },
            fullscreenControl: false,
            streetViewControl: false,
            mapTypeControl: false,
            rotateControl: false,
            gestureHandling: 'greedy' // Single finger gestures
        };
        this.map = new google.maps.Map(document.getElementById(this.map_id), options);
        if (this.marker) {
            var self = this;
            this.map.addListener('click', function(e) {
                self.setMarker(e.latLng);
            });
        }
        for (var key of Object.keys(this.map_listeners)) {
            this.map.addListener(key, this.map_listeners[key]);
        }
    }

    initSearchBox() {
        // Link search box to map
        var input = document.getElementById(this.search_id);
        var searchBox = new google.maps.places.SearchBox(input); 
        // Bias search to current viewport
        this.map.addListener('bounds_changed', function() {
            searchBox.setBounds(this.getBounds());
        });
        // Add listner to change to place
        var self = this;
        searchBox.addListener('places_changed', function() {
            document.getElementById(self.search_id).blur();
            var places = searchBox.getPlaces();
            // Only searches with results
            if (places.length == 0) {
                return;
            }
            var place = places[0]
            // Set adres in searchbox
            document.getElementById(self.search_id).value = place.formatted_address;
            // Set bounds for place
            var bounds = new google.maps.LatLngBounds();
            if (!place.geometry) {
                console.warn("Place has no geometry")
                return; // Returned place contains no geometry
            }
            if (place.geometry.viewport) {
                // Only geocodes have viewport.
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
            // Place marker
            if (self.marker) {
                self.setMarker(place.geometry.location);
            }
            self.map.fitBounds(bounds, self.map_blindspot);
        });
    }

    initCheckCenter(){
        var map_region =[{lat: 51.42754,lng: 2.93734},{lat: 51.20781,lng: 6.23324},{lat: 49.42623,lng: 6.07943},{lat: 50.98703,lng: 1.94857}];
        var polygon = new google.maps.Polygon({path: map_region});
        if(navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var user_loc = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                if (google.maps.geometry.poly.containsLocation(user_loc, polygon)) {
                    this.default_center = {lat: position.coords.latitude, lng: position.coords.longitude};
                }
            });
        }   
    }

    setMarker(position) {
        // Set map selected_marker null and create new marker
        if(this.selected_marker != undefined) {
            this.selected_marker.setMap(null);
        }
        this.selected_marker = new google.maps.Marker({
            position: position,
            map: this.map
        });
        if (this.marker_callback != null) {
            this.marker_callback();
        }
    }

    init(center, zoom) {
        this.initMap(center, zoom);
        this.initSearchBox();
    }

    reloadScripts() {
        // Destroy old API
        document.querySelectorAll('script[src^="https://maps.googleapis.com"]').forEach(script => {
            script.remove();
        });
        if(typeof(google) != 'undefined') {
            delete google.maps;
        }
        var elements = document.getElementsByClassName("div pac-container pac-logo");
        while (elements.length > 0) elements[0].remove();
        // Generate new Google Maps API script
        let newAPI = document.createElement('script');
        newAPI.src = 'https://maps.googleapis.com/maps/api/js?libraries=' + this.libraries.join(',') + '&key=' + this.api_key + '&language=' + this.language + '&callback=googleMapsAPILoaded';
        // Callback for the Google Maps API src
        window.googleMapsAPILoaded = () => {
            let event = new CustomEvent('googleMapsAPILoaded');
            window.dispatchEvent(event);
        }
        // Wait for the callback to be executed
        let apiLoaded = new Promise(resolve => {
            window.addEventListener('googleMapsAPILoaded', () => {
                resolve();
            });
        });
        // Start the script
        document.querySelector('head').appendChild(newAPI);
        return apiLoaded;
    }

    setLanguage(language, callback=undefined) {
        if (this.language != language) {
            this.language = language;
            var center = undefined;
            var zoom = undefined;
            if (this.map != undefined) {
                var c = this.map.getCenter();
                center = {lat: c.lat(), lng: c.lng()};
                zoom = this.map.getZoom();
            }
            this.reloadScripts().then(() => {
                this.init(center=center, zoom=zoom);
                this.preCallback(callback)
            });
        }
        else if (callback != undefined) {
            callback();
        }
    }

    preCallback(callback) {
        if (callback != undefined) {
            callback();
        }
    }

    reset() {
        this.selected_marker = undefined;
        document.getElementById(this.search_id).value = '';
        if (this.map != undefined) {
            this.map.setCenter(this.default_center);
            this.map.setZoom(this.default_zoom);
        }
    }

}

class MapsHandlerClustering extends MapsHandler {
    constructor(map_id, search_id, api_key, libraries=[], default_center={lat: 0.0, lng: 0.0}, default_zoom=0, map_blindspot={top: 0, bottom: 0, left: 0, right: 0}, map_listeners={}, marker=false, marker_callback=null) {
        super(map_id, search_id, api_key,['geometry'].concat(libraries), default_center, default_zoom, map_blindspot, map_listeners, marker, marker_callback);

        this.selected_marker = undefined;
        this.locations = [];
    }

    preCallback(callback) {
        // Set markers
        this.setMarkers(this.locations);
        if (callback != undefined) {
            callback();
        }
    }

    setMarkers(locations) {
        this.locations = locations;
        if (this.markerClusterer) {
            this.markerClusterer.clearMarkers();
        }
        var markers = [];
        const image = "https://raw.githubusercontent.com/tckrishna/edit/main/pin.svg";
        Object.keys(locations).forEach(id => {
            var marker = new google.maps.Marker({
                position: {lat: locations[id].lat, lng: locations[id].lng},
                id: id,
                icon: image,
            });
            // Add click event
            google.maps.event.addListener(marker, "click", function() {
                setSelected(this.id);
            });
            markers.push(marker);
        });
        this.markerClusterer = new MarkerClusterer(this.map, markers, {
            styles: [{
                width: 30,
                height: 30,
                className: 'custom-clustericon-1'
            }, {
                width: 40,
                height: 40,
                className: 'custom-clustericon-2'
            }, {
                width: 50,
                height: 50,
                className: 'custom-clustericon-3'
            }],
            clusterClass: 'custom-clustericon',
            zoomOnClick: false,
            averageCenter: true,
        });
        google.maps.event.addListener(this.markerClusterer, "click", function(c) {
            var bounds = new google.maps.LatLngBounds();
            // c.getMarkers().forEach(marker => {
            //     bounds.extend(marker.getPosition());
            // });
            // this.map.fitBounds(bounds, this.map_blindspot);
            var m = c.getMarkers();
            setSelected(m[0].id);

        });
    }

    recenter() {
        if (this.markerClusterer) {
            var bounds = new google.maps.LatLngBounds();
            this.markerClusterer.getMarkers().forEach((marker) => {
                bounds.extend(marker.getPosition());
            });
            this.map.fitBounds(bounds, this.map_blindspot);
        }
    }

    markerDistancesToCenter() {
        var center = this.map.getCenter();
        var distances = [];
        // Compute to all
        Object.keys(this.locations).forEach(id => {
            var distance = google.maps.geometry.spherical.computeDistanceBetween(center, new google.maps.LatLng(this.locations[id].lat, this.locations[id].lng));
            distances.push({id: id, distance: distance});
        });
        // Sort by distance
        distances.sort((a, b) => {return (a.distance < b.distance) ? -1 : 1});
        return distances;
    }

}