import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
/* Same rules as Django modals — bundled so cache-busted index.css always matches. */
import '../../css/accounts-auth-landing.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
