package main


type LoginRequest struct {
	EmailOrUsername string `json:"email_or_username"`
	Password string `json:"password"`
}

type RegisterRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
	RepeatPassword string `json:"repeat_password"`
	Email    string `json:"email"`
	UserType string `json:"user_type"`
}

type LoginResponse struct {
	Token string `json:"token"`
	Email string `json:"email"`
	Username string `json:"username"`
	UserType string `json:"user_type"`
}
