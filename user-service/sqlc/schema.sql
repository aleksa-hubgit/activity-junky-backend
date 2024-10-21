CREATE TYPE user_type AS ENUM ('participant', 'organizer');
CREATE TYPE activity_status AS ENUM ('available', 'finished', 'canceled');


CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(30) NOT NULL,
    email VARCHAR(30) NOT NULL,
    password VARCHAR(100) NOT NULL,
    user_type user_type NOT NULL
);

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    category VARCHAR(30) NOT NULL,
    date VARCHAR(30) NOT NULL,
    price FLOAT NOT NULL,
    name VARCHAR(30) NOT NULL,
    description TEXT NOT NULL,
    total_places INT NOT NULL,
    status activity_status DEFAULT 'available' NOT NULL
);

CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY,
    participant_id INT REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    activity_id INT REFERENCES activities(id) ON DELETE CASCADE NOT NULL,
    date VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY,
    participant_id INT REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    organizer_id INT REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    date VARCHAR(30) NOT NULL,
    active BOOLEAN NOT NULL
);


