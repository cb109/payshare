# -*- coding: utf-8 -*-
import uuid

from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from djmoney.models.fields import MoneyField


class PayShareError(Exception):
    pass


class UserNotMemberOfCollectiveError(PayShareError):

    def __init__(self, user, collective):
        message = "{} is not part of collective {}".format(user, collective)
        super(UserNotMemberOfCollectiveError, self).__init__(message)


class LiquidationNeedsTwoDifferentUsersError(PayShareError):

    def __init__(self, user):
        message = "{} cannot be both debtor and creditor".format(user)
        super(LiquidationNeedsTwoDifferentUsersError, self).__init__(message)


class TimestampMixin(models.Model):
    """Add created and modified timestamps to a model."""
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(models.Model):
    """A model to attach additional data to a Django User."""

    user = models.OneToOneField("auth.User",
                                on_delete=models.CASCADE,
                                related_name="profile")

    avatar_image_url = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return u"Profile for {} ".format(self.user)


@receiver(post_save, sender=User)
def create_userprofile_when_user_created(
        sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Collective(TimestampMixin, models.Model):
    """A collective groups users that want to share payments.

    Its key is used as an identifier e.g. in URLs. Its token is used to
    authenticate as a User for this Collective instead of having to
    provide key and password everytime. The token updates when the
    password is changed.
    """
    name = models.CharField(max_length=100)
    key = models.UUIDField(default=uuid.uuid4, editable=False)
    password = models.CharField(max_length=128)
    token = models.UUIDField(default=uuid.uuid4, editable=False)

    def set_password(self, password):
        self.password = make_password(password)
        self.token = uuid.uuid4()

    def check_password(self, password):
        return check_password(password, self.password)

    def save(self, *args, **kwargs):
        """Make sure to save changed password hashes, not as plain text."""
        if not self.id:
            self.set_password(self.password)
        else:
            password_in_db = Collective.objects.get(id=self.id).password
            if password_in_db != self.password:
                self.set_password(self.password)
        return super(Collective, self).save(*args, **kwargs)

    def is_member(self, user):
        try:
            Membership.objects.get(collective=self, member=user)
            return True
        except Membership.DoesNotExist:
            return False

    def add_member(self, user):
        if not self.is_member(user):
            Membership.objects.create(collective=self, member=user)

    @property
    def members(self):
        return User.objects.filter(membership__collective__id=self.id)

    def __str__(self):
        return u"{}".format(self.name)


class Membership(TimestampMixin, models.Model):
    """A membership is a mapping of a user to a collective."""
    member = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    collective = models.ForeignKey("purchases.Collective",
                                   on_delete=models.CASCADE)

    class Meta:
        unique_together = ("member", "collective")

    def __str__(self):
        return u"{} in {}".format(self.member.username,
                                  self.collective.name)


class Purchase(TimestampMixin, models.Model):
    """A purchase describes a certain payment of a member of a collective."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = MoneyField(max_digits=10,
                       decimal_places=2,
                       default_currency="EUR")
    buyer = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    collective = models.ForeignKey("purchases.Collective",
                                   on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return u"{} for {} by {} in {}".format(self.price,
                                               self.name,
                                               self.buyer.username,
                                               self.collective.name)

    @property
    def kind(self):
        return "purchase"

    def delete(self):
        self.deleted = True
        self.save()


@receiver(pre_save, sender=Purchase)
def purchase_pre_save_ensure_membership(sender, instance, *args, **kwargs):
    if not instance.collective.is_member(instance.buyer):
        raise UserNotMemberOfCollectiveError(instance.buyer,
                                             instance.collective)


class Liquidation(TimestampMixin, models.Model):
    """A liquidation describes a repayment of one member to another."""
    description = models.TextField(blank=True, null=True)
    amount = MoneyField(max_digits=10,
                        decimal_places=2,
                        default_currency="EUR")
    debtor = models.ForeignKey("auth.User", related_name="debtor",
                               on_delete=models.CASCADE)
    creditor = models.ForeignKey("auth.User", related_name="creditor",
                                 on_delete=models.CASCADE)
    collective = models.ForeignKey("purchases.Collective",
                                   on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return u"{} from {} to {} in {}".format(self.amount,
                                                self.creditor.username,
                                                self.debtor.username,
                                                self.collective.name)

    @property
    def kind(self):
        return "liquidation"

    def delete(self):
        self.deleted = True
        self.save()


@receiver(pre_save, sender=Liquidation)
def liquidation_pre_save_ensure_constraints(sender, instance, *args, **kwargs):
    if instance.debtor == instance.creditor:
        raise LiquidationNeedsTwoDifferentUsersError(instance.debtor)
    for user in [instance.debtor, instance.creditor]:
        if not instance.collective.is_member(user):
            raise UserNotMemberOfCollectiveError(user, instance.collective)
