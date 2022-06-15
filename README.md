# HOSTING LOCALLY
The designated database is postgres
To set up database to be used, first make sure postgres is install and then go to the psql shell.
After accessing psql shell, do the following:

```bash
CREATE DATABASE yourdatabasename;
CREATE USER youruser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE yourdatabasename TO youruser;
```

If postgis and citext extensions are not default to your postgres template you might also have to do the following:

```bash
\c yourdatabasename;
CREATE EXTENSION POSTGIS;
CREATE EXTENSION CITEXT;
```

Create a ```.env``` file at the root of this project, and in it, define the following:

    DB_NAME - [Compulsory] Db name on PostgreSQL

    DB_USER - [Compulsory] User of PostreSQL db with admin permissions

    DB_PASSWORD - [Compulsory] DB User's password

    DB_HOST - [Compulsory] HOST where PostgreSQL db is located


**Note** replace every ```your...``` with the actual names you used or intend to use.


# API ENDPOINTS

## Authentication Endpoints

### Register User
` POST /api/auth/registration/`

User registers to the fanatasy league as a team owner. A team will be autogenerated on successful registration with 20 players to go with it

#### Payload
```
{
    "email": "someemail@test.com",
    "password1": "atleast8chars",
    "password2": "atleast8chars",
    "first_name": "some",   # OPTIONAL
    "last_name": "one       # OPTIONAL
}
```

#### Response
```

{
    "id": <user_id>,
    "email": "someemail@test.com",
    "first_name": "some",   # could be null
    "last_name": "one       # could be null
}

```

### User Login
` POST /api/auth/login/`

#### Payload
```
{
	"email": "someemail@test.com",
	"password": "atleast8chars",
}
```

#### Response
```

{
	"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjU1Mjg5MzEzLCJlbWFpbCI6InRlc3RyZWdpc3RlcjFAdGVzdC5jb20ifQ.tYCf93o1eI6eVw70TwvnGRxooAmt5ZYr2r0dMx6FraQ",
	"user": {
		"id": <user_id>,
		"email": "someemail@test.com",
		"first_name": "some",   # could be null
		"last_name": "one",   # could be null
	}
}

```

## League Endpoints

### Retrieve My Team
`GET /api/league/my_team/`

Gets logged in users team if they have one else will return a 404

#### Response

```
{
	"id": <team_id>,
	"name": "East Jenniferberg CIFXBBJREM",
	"country": "Kenya",
	"budget": "5000000.00",
	"value": "20000000.00"
}
```

### List Teams
`GET /api/league/teams/`

Logged in users can list teams currently available in the league

#### Filters and Pagination
`?page=<int>&page_size=<int>&country=<country_code>`

#### Response

```
[
	{
		"id": <team_id>,
		"name": "MAN Utd",
		"country": "United Kingdom",
		"value": "20000000.00"
	},
	{
		"id": <team_id>,
		"name": "MAN city",
		"country": "United Kingdom",
		"value": "19636160.00"
	}
    ...
]
```

### Retrieve Team
`GET /api/league/teams/<team_id>/`

Logged in user can retrieves team's information whose primary key equals provided <team_id> in request url else 404

#### Response

```
{
	"id": <team_id>,
	"name": "MAN city",
	"country": "United Kingdom",
	"budget": "5000000.00",
	"value": "19636160.00",
	"owner": {
		"first_name": null,
		"last_name": null
	}
}
```

### Update Team
`PATCH /api/league/teams/<team_id>/`

Logged in team owner can update a team's information whose primary key equals provided <team_id> in request url
Updatable fields are name and country only.

#### Payload
```
{
	"name": "AC Milan",
	"country": "ita"
}
```

#### Response

```
{
	"id": <team_id>,
	"name": "AC Milan",
	"country": "Italy",
	"budget": "5000000.00",
	"value": "20000000.00",
	"owner": {
		"first_name": "user5",
		"last_name": null
	}
}
```

### List Team Players
`GET /api/league/teams/<team_id>/players/`

Logged in users can list players of the team whose primary key equals <team_id>

#### Filters and Pagination
`?page=<int>&page_size=<int>&country=<country_code>&position=goalkeeper/attacker/midfielder/defender`

#### Response

```
[
	{
		"id": <player_id>,
		"first_name": "lionel",
		"last_name": "messi",
		"age": 39,
		"position": "attacker",
		"country": "Argentina",
		"value": "1000000.00"
	},
	{
		"id": <player_id>,
		"first_name": "Mary",
		"last_name": "Hart",
		"age": 36,
		"position": "attacker",
		"country": "Kenya",
		"value": "1000000.00"
	},
    ...
]
```

### List Players
`GET /api/league/players/`

Logged in users can list players currently available in the league

#### Filters and Pagination
`?page=<int>&page_size=<int>&team=<team_id>&country=<country_code>&position=goalkeeper/attacker/midfielder/defender`

#### Response

```
[
	{
		"id": <player_id>,
		"first_name": "lionel",
		"last_name": "messi",
		"age": 39,
		"position": "attacker",
		"country": "Argentina",
		"value": "1000000.00"
	},
	{
		"id": <player_id>,
		"first_name": "Mary",
		"last_name": "Hart",
		"age": 36,
		"position": "attacker",
		"country": "Kenya",
		"value": "1000000.00"
	},
    ...
]
```

### Retrieve Player
`GET /api/league/players/<player_id>/`

Logged in users can retrieve player whose id is equal to <player_id>

#### Response

```
{
	"id": <player_id>,
	"first_name": "Andrew",
	"last_name": "Farmer",
	"age": 25,
	"position": "goalkeeper",
	"country": "Kenya",
	"value": "1000000.00",
	"team": <team_id>,
	"team_name": "AC Milan"
}
```

### Update Player
`PUT /api/league/players/<player_id>/`

Logged in team owner can update information for player whose id is equal to <player_id>. Updatable fields are first_name, last_name and country

#### Payload
{
    "first_name": "kylian",
    "last_name": "mbappe",
    "country": "fra"
}

#### Response

```
{
	"id": <player_id>,
	"first_name": "kylian",
	"last_name": "mbappe",
	"age": 25,
	"position": "attacker",
	"country": "France",
	"value": "1000000.00",
	"team": <team_id>,
	"team_name": "PSG"
}
```

### Transfer List Market
`GET /api/league/market/`

Logged in users can list pending transfers available on the league market

#### Filters and Pagination
`?page=<int>&page_size=<int>&seller=<team_id>&player=<player_id>&position=goalkeeper/attacker/midfielder/defender`


#### Response
```
[
	{
		"player": 1,
		"first_name": "lionel",
		"last_name": "messi",
		"position": "attacker",
		"seller": 2,
		"seller_name": "MAN city",
		"price": "2500000.00",
		"status": "pending"
	},
	{
		"player": 2,
		"first_name": "Mary",
		"last_name": "Hart",
		"position": "attacker",
		"seller": 2,
		"seller_name": "MAN city",
		"price": "200000.00",
		"status": "pending"
	}
    ...
]
```

### Put Player on Transfer List
`POST /api/league/players/<player_id>/transfer/`

Logged in team owner can put player whose primary key equals <player_id> on the transfer list

#### Payload
```
{
    "price": "5000000"
}
```

#### Response

```
{
	"player": <player_id>,
	"first_name": "kylian",
	"last_name": "mbappe",
	"position": "goalkeeper",
	"seller": <team_id>,
	"seller_name": "AC Milan",
	"price": "5000000.00",
	"status": "pending"
}
```

### Buy Player
`POST /api/league/players/<player_id>/buy/`

Logged in team owner can buy player whose primary key equals <player_id> from the transfer list


#### Response

```
{
	"id": <player_id>,
	"first_name": "kylian",
	"last_name": "mbappe",
	"age": 25,
	"position": "goalkeeper",
	"country": "France",
	"value": "1850000.00",
	"team": 4,
	"team_name": "Tylerville NV"
}
```