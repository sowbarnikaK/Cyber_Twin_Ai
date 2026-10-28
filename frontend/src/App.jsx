
import { useState } from 'react'
import './App.css'

function App() {
  const [page, setPage] = useState('Dashboard')
  const [simulations, setSimulations] = useState([])
  const [scenario, setScenario] = useState('Port Scan')
  const [running, setRunning] = useState(false)

  const menu = [
    'Dashboard',
    'Network Topology',
    'Attack Simulation',
    'Simulation History',
    'Settings',
  ]

  function runSimulation() {
    setRunning(true)
    setTimeout(() => {
      const result = {
        id: Date.now(),
        scenario,
        status: 'Completed',
        time: new Date().toLocaleString(),
        risk: scenario === 'Brute Force' ? 'HIGH' : scenario === 'Port Scan' ? 'MEDIUM' : 'LOW',
      }
      setSimulations(previous => [result, ...previous])
      setRunning(false)
    }, 700)
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>⚡ CyberTwin AI</h2>
        <p className="menu-title">MAIN MENU</p>

        {menu.map(item => (
          <button
            key={item}
            className={`menu ${page === item ? 'active' : ''}`}
            onClick={() => setPage(item)}
          >
            {item === 'Dashboard' ? '▦' :
             item === 'Network Topology' ? '⌘' :
             item === 'Attack Simulation' ? '⚔' :
             item === 'Simulation History' ? '◷' : '⚙'}
            {' '}{item}
          </button>
        ))}

        <div className="profile">🟢 Demo System Online</div>
      </aside>

      <main className="main">
        <header>
          <div>
            <p className="eyebrow">CYBERSECURITY DIGITAL TWIN</p>
            <h1>{page === 'Dashboard' ? 'Security Command Center' : page}</h1>
            <p className="subtitle">Monitor, simulate and understand your security environment.</p>
          </div>
          <div className="status">● DEMO MODE</div>
        </header>

        {page === 'Dashboard' && (
          <>
            <section className="welcome">
              <div>
                <p className="eyebrow">WELCOME TO CYBERTWIN</p>
                <h2>Your security. Simulated smarter.</h2>
                <p>Explore your virtual network and run safe, controlled security scenarios.</p>
                <button className="primary" onClick={() => setPage('Attack Simulation')}>
                  Start Simulation →
                </button>
              </div>
              <div className="orb">⬡</div>
            </section>

            <section className="stats">
              <article className="stat"><span>NETWORK NODES</span><h2>12</h2><p>Sample virtual devices</p></article>
              <article className="stat"><span>THREATS DETECTED</span><h2 className="amber">03</h2><p>Sample threat data</p></article>
              <article className="stat"><span>SIMULATIONS RUN</span><h2>{24 + simulations.length}</h2><p>Includes this session</p></article>
              <article className="stat"><span>SECURITY SCORE</span><h2 className="green">92%</h2><p>Demo score</p></article>
            </section>

            <section className="bottom">
              <article className="panel">
                <h3>Network Overview</h3>
                <p className="muted">Virtual infrastructure status</p>
                <div className="network">
                  <div className="node">🌐<span>Gateway</span></div>
                  <div className="connection"></div>
                  <div className="node">🖥️<span>Server</span></div>
                  <div className="connection"></div>
                  <div className="node">💻<span>Client</span></div>
                </div>
                <p className="green">● Sample nodes connected</p>
              </article>
              <article className="panel">
                <h3>Recent Activity</h3>
                {simulations.length === 0 ? (
                  <p className="muted">No new simulations in this session. Start one to see activity.</p>
                ) : simulations.slice(0, 3).map(item => (
                  <p className="activity" key={item.id}>🟢 <span>{item.scenario}<small>{item.time}</small></span></p>
                ))}
              </article>
            </section>
          </>
        )}

        {page === 'Network Topology' && (
          <section className="panel page-panel">
            <h2>Virtual Network Map</h2>
            <p className="muted">Illustrative topology for the CyberTwin AI demo.</p>
            <div className="network topology">
              <div className="node">🌐<span>Gateway</span></div>
              <div className="connection"></div>
              <div className="node">🧱<span>Firewall</span></div>
              <div className="connection"></div>
              <div className="node">🖥️<span>Server</span></div>
              <div className="connection"></div>
              <div className="node">💻<span>Client</span></div>
            </div>
            <p className="green">● Illustrative nodes · No live network scan performed</p>
          </section>
        )}

        {page === 'Attack Simulation' && (
          <section className="panel page-panel">
            <h2>Security Scenario Simulator</h2>
            <p className="muted">Run a local, rule-based demo. This does not send attacks or scan any real system.</p>
            <label className="field-label" htmlFor="scenario">Choose a scenario</label>
            <select id="scenario" value={scenario} onChange={e => setScenario(e.target.value)}>
              <option>Port Scan</option>
              <option>Brute Force</option>
              <option>Traffic Anomaly</option>
            </select>
            <div className="scenario-info">
              <p><strong>Scenario:</strong> {scenario}</p>
              <p><strong>Purpose:</strong> Demonstrate how a simulated security event may be classified.</p>
              <p><strong>Mode:</strong> Safe local demo only</p>
            </div>
            <button className="primary" onClick={runSimulation} disabled={running}>
              {running ? 'Running Demo...' : '▶ Run Simulation'}
            </button>
            {simulations.length > 0 && (
              <div className="result">
                <h3>Latest Demo Result</h3>
                <p>Scenario: {simulations[0].scenario}</p>
                <p>Risk classification: <strong className={simulations[0].risk === 'HIGH' ? 'amber' : 'green'}>{simulations[0].risk}</strong></p>
                <p>Status: {simulations[0].status}</p>
                <p className="muted">Rule-based example only; not a real detection.</p>
              </div>
            )}
          </section>
        )}

        {page === 'Simulation History' && (
          <section className="panel page-panel">
            <h2>Simulation History</h2>
            <p className="muted">Results from this browser session.</p>
            {simulations.length === 0 ? (
              <p>No simulations yet. Go to Attack Simulation and run a demo.</p>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Scenario</th><th>Risk</th><th>Status</th><th>Time</th></tr></thead>
                  <tbody>
                    {simulations.map(item => (
                      <tr key={item.id}>
                        <td>{item.scenario}</td>
                        <td className={item.risk === 'HIGH' ? 'amber' : 'green'}>{item.risk}</td>
                        <td>{item.status}</td>
                        <td>{item.time}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}

        {page === 'Settings' && (
          <section className="panel page-panel">
            <h2>Settings</h2>
            <p>Application: CyberTwin AI</p>
            <p>Environment: Local demo</p>
            <p>Backend connection: Not connected yet</p>
            <p className="muted">We will connect your friend's FastAPI backend in a later step.</p>
          </section>
        )}

        <footer>CyberTwin AI · Academic Project · Demo Data</footer>
      </main>
    </div>
  )
}

export default App

