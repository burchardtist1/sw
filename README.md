# How to run the project
Build an image:
```bash
make build
```

run db migrations:
```bash
make recreate-db
```

finally run a server:
```bash
make run
```

and go to `localhost:8000`

# Useful commands
build dockers - `make build`

recreate database - `make recreate-db`

start services as a daemon - `make run`

start services directly - `make up`

format code and imports - `make format`

run tests - `make test`