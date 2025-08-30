CREATE TABLE users(
	id SERIAL PRIMARY KEY,
	first_name VARCHAR NOT NULL,
	last_name VARCHAR NOT NULL,
	card_number VARCHAR(6) NOT NULL UNIQUE CHECK (card_number ~ '^[0-9]{6}$'),
);


CREATE TABLE IF NOT EXISTS books(
	id SERIAL PRIMARY KEY,
	serial_number VARCHAR(6) NOT NULL UNIQUE CHECK (serial_number ~ '^[0-9]{6}$'),
	author VARCHAR NOT NULL,
	title VARCHAR NOT NULL,
	is_borrowed BOOLEAN DEFAULT FALSE,
	borrow_date DATE,
	borrower_card_number VARCHAR(6) REFERENCES users(card_number) 
);


-- data population with some data to work with 
INSERT INTO users (first_name, last_name, card_number) VALUES
('Anna', 'Kowalska', '123456'),
('Jan', 'Nowak', '234567'),
('Maria', 'Wiśniewska', '345678'),
('Piotr', 'Wójcik', '456789'),
('Katarzyna', 'Kowalczyk', '567890')
ON CONFLICT (card_number) DO NOTHING;

INSERT INTO books (serial_number, author, title, is_borrowed, borrow_date, borrower_card_number) VALUES
('100001', 'Adam Mickiewicz', 'Pan Tadeusz', false, NULL, NULL),
('100002', 'Henryk Sienkiewicz', 'Quo Vadis', true, '2024-01-15', '123456'),
('100003', 'Bolesław Prus', 'Lalka', false, NULL, NULL),
('100004', 'Stanisław Lem', 'Solaris', true, '2024-01-10', '345678'),
('100005', 'Olga Tokarczuk', 'Księgi Jakubowe', false, NULL, NULL),
('100006', 'Andrzej Sapkowski', 'Wiedźmin: Ostatnie życzenie', true, '2024-01-20', '234567'),
('100007', 'Wisława Szymborska', 'Wiersze wybrane', false, NULL, NULL),
('100008', 'Stephen King', 'To', true, '2024-01-05', '456789'),
('100009', 'J.K. Rowling', 'Harry Potter i Kamień Filozoficzny', false, NULL, NULL),
('100010', 'George Orwell', 'Rok 1984', true, '2024-01-18', '567890')
ON CONFLICT (serial_number) DO NOTHING;

INSERT INTO books (serial_number, author, title) VALUES
('100011', 'Fiodor Dostojewski', 'Zbrodnia i kara'),
('100012', 'Franz Kafka', 'Proces'),
('100013', 'Ernest Hemingway', 'Stary człowiek i morze'),
('100014', 'Gabriel García Márquez', 'Sto lat samotności'),
('100015', 'Umberto Eco', 'Imię róży'),
('100016', 'J.R.R. Tolkien', 'Władca Pierścieni'),
('100017', 'Isaac Asimov', 'Fundacja'),
('100018', 'Philip K. Dick', 'Czy androidy marzą o elektrycznych owcach?'),
('100019', 'Neil Gaiman', 'American Gods'),
('100020', 'Terry Pratchett', 'Kolor magii')
ON CONFLICT (serial_number) DO NOTHING;
