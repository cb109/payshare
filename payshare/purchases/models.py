# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from djmoney.models.fields import MoneyField


class PayShareError(Exception):
    pass


class BuyerNotMemberOfCollectiveError(PayShareError):
    pass


class TimestampMixin(models.Model):
    """Add created and modified timestamps to a model."""
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Collective(TimestampMixin, models.Model):
    """A collective groups users that want to share payments."""
    name = models.CharField(max_length=100)

    def is_member(self, user):
        try:
            Membership.objects.get(collective=self, member=user)
            return True
        except Membership.DoesNotExist:
            return False

    def __unicode__(self):
        return u"{}".format(self.name)


class Membership(TimestampMixin, models.Model):
    """A membership is a mapping of a user to a collective."""
    member = models.ForeignKey("auth.User")
    collective = models.ForeignKey("purchases.Collective")

    def __unicode__(self):
        return u"{} in {}".format(self.member.username,
                                  self.collective.name)


class Purchase(TimestampMixin, models.Model):
    """A purchase describes a certain payment of a member of a collective."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = MoneyField(max_digits=10,
                       decimal_places=2,
                       default_currency='EUR')
    buyer = models.ForeignKey("auth.User")
    collective = models.ForeignKey("purchases.Collective")

    def __unicode__(self):
        return u"{} for {} by {} in {}".format(self.price,
                                               self.name,
                                               self.buyer.username,
                                               self.collective.name)


@receiver(pre_save, sender=Purchase)
def purchase_pre_save_ensure_membership(sender, instance, *args, **kwargs):
    if not instance.collective.is_member(instance.buyer):
        raise BuyerNotMemberOfCollectiveError()
