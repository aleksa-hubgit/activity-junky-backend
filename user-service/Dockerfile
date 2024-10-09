FROM golang:1.23-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download && go mod verify

COPY . ./

RUN go build -o /user-service

FROM alpine:latest

WORKDIR /

COPY --from=builder /user-service /user-service

EXPOSE 8082

CMD ["./user-service"]