from __future__ import annotations

from decimal import Decimal
from typing import Any
from django.core.cache import cache
from django.db import models
from django_countries.fields import CountryField


class AbstractSettingModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        pass

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.pk = 1
        super(AbstractSettingModel, self).save(*args, **kwargs)
        self.set_cache()

    @classmethod
    def load(cls) -> LeagueSettings:
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)


class LeagueSettings(AbstractSettingModel):
    initial_player_value = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal(1000000))
    initial_team_budget = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal(5000000))
    default_country = CountryField(default='KE')
