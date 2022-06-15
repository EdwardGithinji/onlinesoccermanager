from celery import shared_task
from league.services import generate_team_with_players

@shared_task()
def create_team_with_players_on_user_registration(user):
    generate_team_with_players(user)
