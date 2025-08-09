import React, { useState, useRef } from 'react'
import axios from 'axios'

export default function ChatWidget(){
  const [messages, setMessages] = useState([{from:'bot', text:'Hello! I can help you find routes, traffic, trains and flights.'}])
  const synthRef = useRef(window.speechSynthesis)
  const utterRef = useRef(null)

  function speak(text){
    if(!text) return
    try{
      if(utterRef.current){
        synthRef.current.cancel()
      }
      const u = new SpeechSynthesisUtterance(text)
      u.onend = ()=>{ utterRef.current = null }
      utterRef.current = u
      synthRef.current.speak(u)
    }catch(e){
      console.error('speech failed', e)
    }
  }

  function stopSpeaking(){
    try{
      if(utterRef.current){
        synthRef.current.cancel()
        utterRef.current = null
      }
    }catch(e){console.error(e)}
  }

  async function sendUser(msg){
    setMessages(prev=>[...prev, {from:'user', text:msg}])
    // Demo: call backend train/flight endpoints when user writes "train 12345" or "flight AI202"
    const lower = msg.toLowerCase()
    if(lower.startsWith('train ')){
      const parts = msg.split(/\s+/)
      const trainNo = parts[1]
      const date = parts[2] || new Date().toLocaleDateString('en-GB').split('/').join('-') // crude DD-MM-YYYY
      try{
        const resp = await axios.get(`/api/train/status`, { params: { train_no: trainNo, date }})
        const txt = `Train ${trainNo} status fetched. See console for payload.`
        setMessages(prev=>[...prev, {from:'bot', text:txt}])
        speak(txt)
        console.log('Train payload', resp.data)
      }catch(e){
        const err = 'Could not fetch train status.'
        setMessages(prev=>[...prev, {from:'bot', text:err}])
        speak(err)
        console.error(e)
      }
      return
    }
    if(lower.startsWith('flight ')){
      const parts = msg.split(/\s+/)
      const flightNo = parts[1]
      try{
        const resp = await axios.get(`/api/flight/summary`, { params: { flight_no: flightNo }})
        const txt = `Flight ${flightNo} summary fetched. See console for payload.`
        setMessages(prev=>[...prev, {from:'bot', text:txt}])
        speak(txt)
        console.log('Flight payload', resp.data)
      }catch(e){
        const err = 'Could not fetch flight info.'
        setMessages(prev=>[...prev, {from:'bot', text:err}])
        speak(err)
        console.error(e)
      }
      return
    }

    // default canned reply
    const reply = `You said: ${msg}. Try 'train 12345' or 'flight AI202' to query transport APIs.`
    setMessages(prev=>[...prev, {from:'bot', text:reply}])
    speak(reply)
  }

  return (
    <div className="chat-widget" aria-live="polite">
      <div className="messages" role="log">
        {messages.map((m,i)=>(
          <div key={i} className={`msg ${m.from}`}>{m.text}</div>
        ))}
      </div>
      <div className="controls">
        <input aria-label="chat input" placeholder="Ask something or 'train 12345' / 'flight AI202'..." onKeyDown={(e)=>{ if(e.key==='Enter'){ sendUser(e.target.value); e.target.value='' }}} />
        <button onClick={()=>speak('This is a demo voice response')}>Speak demo</button>
        <button onClick={stopSpeaking}>Stop</button>
      </div>
    </div>
  )
}
