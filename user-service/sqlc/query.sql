-- name: GetUserByUsername :one
SELECT * FROM users
WHERE username = $1 LIMIT 1;

-- name: GetUserByEmail :one
SELECT * FROM users
WHERE email = $1 LIMIT 1;

-- name: GetUserByEmailOrUsername :one
SELECT * FROM users
WHERE email = $1 OR username = $1 LIMIT 1;

-- name: ListUsers :many
SELECT * FROM users
ORDER BY username;

-- name: CreateUser :one
INSERT INTO users (
  username, email, password, user_type
) VALUES (
  $1, $2, $3, $4
)
RETURNING *;

-- name: CreateActivity :one
INSERT INTO activities (
  id, user_id, category, date, price, name, description, total_places, status
) VALUES (
  $1, $2, $3, $4, $5, $6, $7, $8, $9
)
RETURNING *;

-- name: CreateReservation :one
INSERT INTO reservations (
  id, participant_id, activity_id, date
) VALUES (
  $1, $2, $3, $4
)
RETURNING *;

-- name: CreateSubscription :one
INSERT INTO subscriptions (
  id, participant_id, organizer_id, date, active
) VALUES (
  $1, $2, $3, $4, $5
)
RETURNING *;

-- name: UpdateActivity :exec
UPDATE activities
  set user_id = $2,
  category = $3,
  date = $4,
  price = $5,
  name = $6,
  description = $7,
  total_places = $8,
  status = $9
WHERE id = $1;

-- name: DeleteActivity :exec
DELETE FROM activities
WHERE id = $1;


-- name: UpdateReservation :exec
UPDATE reservations
  set participant_id = $2,
  activity_id = $3,
  date = $4
WHERE id = $1;

-- name: DeleteReservation :exec
DELETE FROM reservations
WHERE id = $1;


-- name: UpdateSubscription :exec
UPDATE subscriptions
  set participant_id = $2,
  organizer_id = $3,
  date = $4,
  active = $5
WHERE id = $1;

-- name: DeleteSubscription :exec
DELETE FROM subscriptions
WHERE id = $1;

-- name: UpdateUser :exec
UPDATE users
  set username = $2,
  email = $3,
  password = $4,
  user_type = $5
WHERE id = $1;

-- name: DeleteUser :exec
DELETE FROM users
WHERE id = $1;

