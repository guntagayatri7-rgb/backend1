"""
Run all microservices locally for development.
Each service runs on a different port:
  - API Gateway: 5000
  - Auth: 5001
  - Users: 5002
  - Vendors: 5003
  - Events: 5004
  - Bookings: 5005
  - Payments: 5006
  - Reviews: 5007
  - Analytics: 5008
"""

import subprocess
import sys
import os
import signal

SERVICES = [
    ("API Gateway", "api_gateway.app", 5000),
    ("Auth Service", "auth_service.app", 5001),
    ("User Service", "user_service.app", 5002),
    ("Vendor Service", "vendor_service.app", 5003),
    ("Event Service", "event_service.app", 5004),
    ("Booking Service", "booking_service.app", 5005),
    ("Payment Service", "payment_service.app", 5006),
    ("Review Service", "review_service.app", 5007),
    ("Analytics Service", "analytics_service.app", 5008),
]

processes = []


def run_service(name, module, port):
    env = os.environ.copy()
    env["SERVICE_PORT"] = str(port)
    env["FLASK_ENV"] = "development"
    proc = subprocess.Popen(
        [sys.executable, "-c", f"from {module} import create_app; app = create_app(); app.run(host='0.0.0.0', port={port}, debug=True)"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc


def main():
    print("Starting CelebrateHub Microservices...")
    print("=" * 60)

    for name, module, port in SERVICES:
        print(f"Starting {name} on port {port}...")
        proc = run_service(name, module, port)
        processes.append((name, proc))

    print("=" * 60)
    print("All services started!")
    print("API Gateway: http://localhost:5000")
    print("Press Ctrl+C to stop all services.")
    print("=" * 60)

    def signal_handler(sig, frame):
        print("\nShutting down all services...")
        for name, proc in processes:
            print(f"Stopping {name}...")
            proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        for name, proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
