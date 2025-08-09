import React from 'react'
import MapView from './components/MapView'
import ChatWidget from './components/ChatWidget'

export default function App(){
  return (
    <div className="app-root">
      <header className="app-header">RealtimeMaps</header>
      <main className="app-main">
        <div className="map-container"><MapView /></div>
        <div className="chat-container"><ChatWidget /></div>
      </main>
    </div>
  )
}
