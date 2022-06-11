from django.db import models
from django.utils.translation import gettext_lazy as _


class PlayerPosition(models.TextChoices):
    GOALKEEPER = "goalkeeper", _("GoalKeeper")
    DEFENDER = "defender", _("Defender")
    MIDFIELDER = "midfielder", _("Midfielder")
    ATTACKER = "attacker", _("Attacker")


class TransferStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    COMPLETE = "complete", _("Complete")
