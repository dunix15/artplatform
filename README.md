
# Art Platform

The Art Platform exposes an API through which customers will be able to participate in a two-way market:
- artists can offer items for sale,
- customers can place orders to buy them.


Participants from either side of the market need to be able to accomplish four main tasks:
- List artwork `GET /v1/artworks/`
- Place an artwork `POST /v1/artworks/`
- Place an order `POST /v1/orders/`
- Cancel an order `POST /v1/orders/{order_id}/cancel`
- View open orders `GET /v1/orders/`
- View completed orders (transactions) `GET /v1/transactions/?user_id={user_id}`

## Run Locally

Clone the project

```bash
  git clone git@github.com:dunix15/artplatform.git
```

Go to the project directory

```bash
  cd artplatform
```

### Docker
Install [docker](https://docs.docker.com/engine/install/)


Start the server

```bash
  docker-compose up
```

### Swagger
Open in browser:
[http://localhost:8000/swagger
](http://localhost:8000/swagger)


### Django Rest Framework
Open in browser:
[http://localhost:8000/v1
](http://localhost:8000/v1)

### Django Admin
Create superuser:
```bash
docker exec -it artplatform-app python manage.py createsuperuser
```
Open in browser:
[http://localhost:8000/admin
](http://localhost:8000/admin)

### Tests
```bash
docker exec -it artplatform-app pytest
```
