import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [benchmark, setBenchmark] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch benchmark data on load
  const runBenchmark = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/api/benchmark');
      setBenchmark(res.data);
    } catch (err) {
      console.error("Benchmark failed", err);
    }
  };

  const processVedicData = async () => {
    setLoading(true);
    const digits = input.split(',').map(num => parseInt(num.trim())).filter(n => !isNaN(n));
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/process', { digits });
      setResult(response.data.result);
    } catch (error) {
      alert("Backend Error");
    }
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Vedabyte Engine Dashboard</h1>
      
      {/* Input Section */}
      <div style={styles.card}>
        <input 
          type="text" value={input} onChange={(e) => setInput(e.target.value)}
          style={styles.input} placeholder="Enter digits (e.g. 12, 45, 7)"
        />
        <button onClick={processVedicData} style={styles.button}>
          {loading ? "Processing..." : "Run Preprocessor"}
        </button>
      </div>

      {/* Graph Section */}
      <div style={{...styles.card, marginTop: '20px'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
           <h3>Performance Benchmark (Log Scale)</h3>
           <button onClick={runBenchmark} style={styles.smallButton}>Refresh Analysis</button>
        </div>
        <div style={{ width: '100%', height: 300, marginTop: '20px' }}>
          <ResponsiveContainer>
            <LineChart data={benchmark}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="digits" stroke="#888" label={{ value: 'Digits', position: 'insideBottom', offset: -5 }} />
              <YAxis scale="log" domain={['auto', 'auto']} stroke="#888" />
              <Tooltip contentStyle={{backgroundColor: '#161b22', border: '1px solid #30363d'}} />
              <Legend />
              <Line type="monotone" dataKey="vedic" stroke="#FFD700" name="Vedic Engine" strokeWidth={3} />
              <Line type="monotone" dataKey="numpy" stroke="#8884d8" name="NumPy Baseline" strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {result && (
        <div style={styles.resultCard}>
          <h3>Processed Output:</h3>
          <code>{JSON.stringify(result)}</code>
        </div>
      )}
    </div>
  );
}

// Add these to your existing styles object
const styles = {
  // ... keep previous styles
  smallButton: {
    backgroundColor: 'transparent',
    color: '#FFD700',
    border: '1px solid #FFD700',
    padding: '5px 10px',
    borderRadius: '4px',
    cursor: 'pointer'
  }
};

export default App;