// components/DisasterMap.jsx
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Default icons
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

// Fix default icon (for fallback)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({ iconRetinaUrl, iconUrl, shadowUrl });

// Custom red icon for disaster locations
const redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Custom blue icon for user's current location
const userIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

export function DisasterMap({ disasters }) {
  const [userLocation, setUserLocation] = useState(null);

  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation([
            position.coords.latitude,
            position.coords.longitude,
          ]);
        },
        (err) => {
          console.error('Could not fetch location:', err);
        }
      );
    }
  }, []);

  const defaultCenter = [30.1575, 71.5249];

  return (
    <MapContainer
      center={userLocation || defaultCenter}
      zoom={userLocation ? 6 : 4}
      style={{ height: '250px', width: '100%' }}
      scrollWheelZoom={true}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      {/* Disaster locations */}
      {disasters.map((d, idx) => (
        <Marker key={idx} position={[d.latitude, d.longitude]} icon={redIcon}>
          <Popup>
            <strong>{d.title}</strong><br />
            {d.description || 'No description'}
          </Popup>
        </Marker>
      ))}

      {/* User's current location */}
      {userLocation && (
        <Marker position={userLocation} icon={userIcon}>
          <Popup>You are here</Popup>
        </Marker>
      )}
    </MapContainer>
  );
}
