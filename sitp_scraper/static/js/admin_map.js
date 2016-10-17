/*jshint strict:true, browser:true, jquery:true */

$(document).ready(function() {
  'use strict';

  //4.630323835305307,-74.09008026123047
  var latitude = $('#id_latitude').val();
  var longitude = $('#id_longitude').val();
  console.log(latitude, longitude)

  L.mapbox.accessToken = 'pk.eyJ1IjoidmVybzRrYSIsImEiOiJjYWNlMWY0Zjk0MGJhNWRmNDIzNmVjNjc0NDRhMjllOCJ9.fRmHavGBvl6wWemwMZBbfA';
  var map = L.mapbox.map('map', 'mapbox.streets').setView([latitude, longitude], 16);
  var geocoder = L.mapbox.geocoder('mapbox.places');
  var myLayer = L.mapbox.featureLayer().addTo(map);
  var marker = L.marker([
    latitude, longitude
  ], {
    icon: L.mapbox.marker.icon({
      'marker-color': '#f86767',
      'marker-size': 'large',
      'marker-symbol': 'bus'
    }),
    draggable: true
  }).addTo(map);

  marker.on('dragend', updateAddress);

  function updateAddress() {
    var m = marker.getLatLng();
    $('#id_latitude').val(m.lat);
    $('#id_longitude').val(m.lng);
  }

});
