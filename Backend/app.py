from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import time
# Import your logic from your existing preprocessor.py
from preprocessor import vedic_bigint_engine

app = Flask(__name__)
# CORS is essential to allow your React app (Port 3000) 
# to talk to your Flask app (Port 5000)
CORS(app)

@app.route('/api/process', methods=['POST'])
def process_data():
    try:
        # Check if user uploaded a file or sent raw JSON
        data = request.json
        input_digits = np.array(data.get('digits', []), dtype=np.uint64)

        if len(input_digits) == 0:
            return jsonify({"error": "No data provided"}), 400

        # Call your NJIT-optimized Vedic function
        # result = vedic_bigint_engine(input_digits)
        # For demo purposes, we call the core logic
        processed_result = vedic_bigint_engine(input_digits)

        return jsonify({
            "status": "success",
            "result": processed_result.tolist()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/benchmark', methods=['GET'])
def get_benchmark():
    precisions = [10, 50, 100, 200, 500, 1000]
    benchmark_data = []

    for d in precisions:
        digit_vector = np.random.randint(0, 10, size=d).astype(np.uint64)
        
        # Warmup
        _ = vedic_bigint_engine(digit_vector)

        # Vedic Time
        t0 = time.perf_counter()
        for _ in range(30): # Reduced iterations for faster UI response
            _ = vedic_bigint_engine(digit_vector)
        v_time = (time.perf_counter() - t0) / 30

        # NumPy Time
        t0 = time.perf_counter()
        for _ in range(30):
            _ = np.convolve(digit_vector, digit_vector)
        n_time = (time.perf_counter() - t0) / 30

        benchmark_data.append({
            "digits": d,
            "vedic": v_time,
            "numpy": n_time,
            "standardOps": d * d,
            "vedicOps": (d * d) // 2
        })

    return jsonify(benchmark_data)



if __name__ == '__main__':
    app.run(debug=True, port=5000)