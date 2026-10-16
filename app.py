from math import isqrt
from time import perf_counter

from flask import Flask, jsonify, request

app = Flask(__name__)


def is_prime(number: int) -> bool:
    """Return whether number is prime using trial division up to its square root."""
    if number < 2:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False

    for divisor in range(3, isqrt(number) + 1, 2):
        if number % divisor == 0:
            return False
    return True


@app.get("/")
def index():
    return jsonify({"status": "ok", "message": "API is running"})


@app.get("/is-prime")
def check_prime():
    raw_number = request.args.get("n")
    if raw_number is None:
        return jsonify({"error": "Missing required query parameter: n"}), 400

    try:
        number = int(raw_number)
    except ValueError:
        return jsonify({"error": "Query parameter n must be an integer"}), 400

    started_at = perf_counter()
    result = is_prime(number)
    processing_time_ms = (perf_counter() - started_at) * 1000

    return jsonify(
        {
            "input": number,
            "is_prime": result,
            "processing_time_ms": round(processing_time_ms, 6),
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
