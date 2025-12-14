import os
import json
import random
import time
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.extras import execute_values

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "manufacturing")
DB_USER = os.getenv("DB_USER", "de_user")
DB_PASS = os.getenv("DB_PASS", "de_pass")

MACHINE_TYPES = ["EXTRUDER", "PACKER", "ROBOT", "CONVEYOR", "PRESS"]
STATUSES = ["ACTIVE", "MAINTENANCE", "DOWN"]
CATEGORIES = ["FOOD", "CHEMICAL", "PLASTIC", "METAL"]
ERROR_CODES = ["E101", "E203", "E404", "E777"]

def conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )

def seed_machines_and_products(n_machines=12, n_products=15):
    with conn() as c, c.cursor() as cur:
        # machines
        cur.execute("SELECT COUNT(*) FROM machines;")
        (mc,) = cur.fetchone()
        if mc == 0:
            machines = []
            today = datetime.now(timezone.utc).date()
            for _ in range(n_machines):
                install_date = today - timedelta(days=random.randint(30, 3650))
                machines.append((
                    random.choice(MACHINE_TYPES),
                    random.randint(1, 3),  # factory_id
                    install_date,
                    random.choice(STATUSES)
                ))
            execute_values(
                cur,
                "INSERT INTO machines (machine_type, factory_id, install_date, status) VALUES %s",
                machines
            )
            print(f"Seeded machines: {n_machines}")
        else:
            print(f"Machines already seeded: {mc}")

        # products
        cur.execute("SELECT COUNT(*) FROM products;")
        (pc,) = cur.fetchone()
        if pc == 0:
            products = []
            for i in range(n_products):
                products.append((
                    f"Product_{i+1:02d}",
                    random.choice(CATEGORIES),
                    round(random.uniform(2.5, 250.0), 2)
                ))
            execute_values(
                cur,
                "INSERT INTO products (product_name, category, unit_cost) VALUES %s",
                products
            )
            print(f"Seeded products: {n_products}")
        else:
            print(f"Products already seeded: {pc}")

def open_order_for_machine(cur, machine_id):
    # Create a RUNNING order (optional but nice)
    cur.execute("SELECT product_id FROM products ORDER BY random() LIMIT 1;")
    (product_id,) = cur.fetchone()
    planned_qty = random.randint(50, 500)
    start = datetime.now(timezone.utc)
    cur.execute(
        """
        INSERT INTO production_orders
          (product_id, machine_id, order_start_time, planned_qty, order_status)
        VALUES
          (%s, %s, %s, %s, 'RUNNING')
        RETURNING order_id;
        """,
        (product_id, machine_id, start, planned_qty)
    )
    return cur.fetchone()[0]

def maybe_close_running_order(cur, machine_id):
    # Close a RUNNING order sometimes
    cur.execute(
        """
        SELECT order_id, planned_qty
        FROM production_orders
        WHERE machine_id=%s AND order_status='RUNNING'
        ORDER BY order_start_time DESC
        LIMIT 1;
        """,
        (machine_id,)
    )
    row = cur.fetchone()
    if not row:
        return None
    order_id, planned_qty = row
    if random.random() < 0.15:  # 15% chance to close
        actual_qty = max(0, int(planned_qty * random.uniform(0.7, 1.05)))
        end = datetime.now(timezone.utc)
        cur.execute(
            """
            UPDATE production_orders
            SET order_end_time=%s, actual_qty=%s, order_status='COMPLETED'
            WHERE order_id=%s;
            """,
            (end, actual_qty, order_id)
        )
        return order_id
    return None

def generate_event(machine_id):
    now = datetime.now(timezone.utc)

    # weighted events
    r = random.random()
    if r < 0.05:
        event_type = "ERROR"
        error_code = random.choice(ERROR_CODES)
        payload = {"severity": random.choice(["LOW", "MEDIUM", "HIGH"]), "temp": round(random.uniform(20, 120), 1)}
    elif r < 0.30:
        event_type = "STOP"
        error_code = None
        payload = {"reason": random.choice(["CHANGEOVER", "MAINTENANCE", "MATERIAL_EMPTY", "UNKNOWN"])}
    elif r < 0.60:
        event_type = "START"
        error_code = None
        payload = {"speed": random.randint(50, 180)}
    else:
        event_type = "HEARTBEAT"
        error_code = None
        payload = {"vibration": round(random.uniform(0.1, 3.5), 2), "amp": round(random.uniform(1.0, 20.0), 2)}

    return (machine_id, event_type, now, error_code, json.dumps(payload))

def run_stream(loop_sleep_sec=2.0, batch_size=20):
    with conn() as c, c.cursor() as cur:
        cur.execute("SELECT machine_id FROM machines ORDER BY machine_id;")
        machine_ids = [r[0] for r in cur.fetchall()]
        if not machine_ids:
            raise RuntimeError("No machines found. Run seed first.")

        # ensure some running orders exist
        for mid in machine_ids[: min(5, len(machine_ids))]:
            cur.execute(
                "SELECT 1 FROM production_orders WHERE machine_id=%s AND order_status='RUNNING' LIMIT 1;",
                (mid,)
            )
            if not cur.fetchone():
                oid = open_order_for_machine(cur, mid)
                print(f"Opened RUNNING order {oid} for machine {mid}")

        print("Streaming events... Ctrl+C to stop.")
        while True:
            events = []
            for _ in range(batch_size):
                mid = random.choice(machine_ids)
                events.append(generate_event(mid))

            execute_values(
                cur,
                """
                INSERT INTO machine_events (machine_id, event_type, event_time, error_code, payload)
                VALUES %s
                """,
                events
            )

            # occasionally close orders / open new ones
            for mid in random.sample(machine_ids, k=min(3, len(machine_ids))):
                closed = maybe_close_running_order(cur, mid)
                if closed is not None and random.random() < 0.5:
                    oid = open_order_for_machine(cur, mid)
                    print(f"Closed order {closed}, opened new RUNNING order {oid} for machine {mid}")

            c.commit()
            print(f"Inserted {len(events)} events at {datetime.now(timezone.utc).isoformat()}")
            time.sleep(loop_sleep_sec)

if __name__ == "__main__":
    seed_machines_and_products()
    run_stream()
