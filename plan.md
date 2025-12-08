# Tech Stack

- python
- pip (or uv) for dependency management
- fastapi
- sqlalchemy (greenlet for async)
- postgres
- docker
- pytest (unit testing)
- hey (a/b testing)

# Flow

- Generation: User sends long url (POST /url) -> we do some business logic -> send back short url
- Redirect: User sends short url (GET /{short_url}) -> business logic -> redirect | error

# Logic

- there are 26 lower & 26 upper case letters in the english alphabet
- and 10 numbers: 0~9
- we would have 62 variants
- assuming the length of short url is 6, we will have 62^6 = 56,800,235,584 (combinations)

Tasks:

- [ ] dockerize and add docs on how to start up the app
- [ ] test coverage >= 70%
- [ ] url validation
- [ ] option to request custom URLs - to make generated short url human readable
- [ ] perform load tests to check read load
- [ ] upload to free hosting - GC, AWS, etc.
