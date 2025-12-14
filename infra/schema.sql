CREATE TABLE IF NOT EXISTS machines (
  machine_id SERIAL PRIMARY KEY,
  machine_type TEXT NOT NULL,
  factory_id INT NOT NULL,
  install_date DATE NOT NULL,
  status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
  product_id SERIAL PRIMARY KEY,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL,
  unit_cost NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS production_orders (
  order_id BIGSERIAL PRIMARY KEY,
  product_id INT NOT NULL REFERENCES products(product_id),
  machine_id INT NOT NULL REFERENCES machines(machine_id),
  order_start_time TIMESTAMPTZ NOT NULL,
  order_end_time TIMESTAMPTZ,
  planned_qty INT NOT NULL,
  actual_qty INT,
  order_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS machine_events (
  event_id BIGSERIAL PRIMARY KEY,
  machine_id INT NOT NULL REFERENCES machines(machine_id),
  event_type TEXT NOT NULL,
  event_time TIMESTAMPTZ NOT NULL,
  error_code TEXT,
  payload JSONB
);

CREATE INDEX IF NOT EXISTS idx_machine_events_time ON machine_events(event_time);
CREATE INDEX IF NOT EXISTS idx_machine_events_machine_time ON machine_events(machine_id, event_time);
