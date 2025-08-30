CREATE TABLE books(
	id SERIAL PRIMARY KEY,
	serial_number VARCHAR(6) NOT NULL UNIQUE CHECK (serial_number ~ '^[0-9]{6}$'),
	author VARCHAR NOT NULL,
	title VARCHAR NOT NULL);

CREATE TABLE users(
	id SERIAL PRIMARY KEY,
	card_number VARCHAR(6) NOT NULL UNIQUE CHECK (card_number ~ '^[0-9]{6}$'),
	created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE loan_status AS ENUM ('borrowed', 'returned', 'overdue');
CREATE TABLE bookloans (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    loan_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE,
    return_date DATE,
    status loan_status DEFAULT 'borrowed',

);
