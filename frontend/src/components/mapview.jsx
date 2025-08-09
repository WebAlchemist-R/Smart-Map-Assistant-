import React, { useEffect, useState } from 'react';
import { GoogleMap, LoadScript, DirectionsService, DirectionsRenderer } from '@react-google-maps/api';

const G_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

export default function MapView(){
  const [map, setMap] = useState(null);
  const [directions, setDirections] = useState(null);
  const [origin, setOrigin] = useState(null);
  const [destination, setDestination] = useState('Marine Lines, Mumbai');

  useEffect(()=>{
    if(navigator.geolocation){
      navigator.geolocation.getCurrentPosition(pos=>{
        setOrigin({lat: pos.coords.latitude, lng: pos.coords.longitude});
      }, ()=>{ /* permission denied or unavailable */});
    }
  },[]);

  return (
    <div style={{height:'100%', width:'100%'}}>
      {G_API_KEY ? (
        <LoadScript googleMapsApiKey={G_API_KEY}>
          <GoogleMap center={origin || {lat:19.0760, lng:72.8777}} zoom={13} mapContainerStyle={{width:'100%',height:'100%'}} onLoad={m=>setMap(m)}>
            {origin && destination && (
              <DirectionsService
                options={{
                  destination,
                  origin,
                  travelMode: 'DRIVING',
                  provideRouteAlternatives: true
                }}
                callback={res=>{
                  if(res !== null && res.status === 'OK'){
                    setDirections(res);
                  }
                }}
              />
            )}
            {directions && <DirectionsRenderer directions={directions} />}
          </GoogleMap>
        </LoadScript>
      ) : (
        <div style={{padding:20}}>No Google Maps API key provided. Add VITE_GOOGLE_MAPS_API_KEY to your frontend env.</div>
      )}
    </div>
  )
}
