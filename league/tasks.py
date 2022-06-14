import string
from random import choices, randint
from faker import Faker
from league.constants import PlayerPosition
from league.models import Team, Player
from users.models import User

NUMBER_OF_GOALKEEPERS = 3
NUMBER_OF_MIDFIELDERS = 6
NUMBER_OF_DEFENDERS = 6
NUMBER_OF_ATTACKERS = 5


def generate_team_with_players(user: User):
    fake = Faker()
    team_names_set = set(Team.objects.values_list('name', flat=True))
    abbrev_size = 10
    team_name = fake.city() + ' ' + ''.join(choices(string.ascii_uppercase, k=abbrev_size))

    while team_name in team_names_set:
        abbrev_size += 1
        team_name = fake.city() + ' ' + ''.join(choices(string.ascii_uppercase, k=abbrev_size))

    team = Team.objects.create(owner=user, name=team_name)
    players_list = []

    for i in range(20):
        if 0 <= i < 3:
            player_position = PlayerPosition.GOALKEEPER
        elif 3 <= i < 9:
            player_position = PlayerPosition.DEFENDER
        elif 9 <= i < 15:
            player_position = PlayerPosition.MIDFIELDER
        else:
            player_position = PlayerPosition.ATTACKER

        player = Player(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            position=player_position,
            team=team,
            age=randint(18,40)
            )
        players_list.append(player)

    Player.objects.bulk_create(players_list)


