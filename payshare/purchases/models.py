# -*- coding: utf-8 -*-
import uuid
from decimal import Decimal
from statistics import median

from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from djmoney.models.fields import MoneyField
from filer.fields.image import FilerImageField

from payshare.purchases.calc import calc_paybacks


DEFAULT_AVATAR_URL = "https://avataaars.io/?avatarStyle=Circle&topType=NoHair&accessoriesType=Blank&facialHairType=Blank&clotheType=ShirtCrewNeck&clotheColor=Black&eyeType=Default&eyebrowType=DefaultNatural&mouthType=Default&skinColor=Light"  # noqa


class PayShareError(Exception):
    pass


class CollectiveReadOnlyError(PayShareError):
    def __init__(self, collective):
        message = "{} is read-only".format(collective)
        super(CollectiveReadOnlyError, self).__init__(message)


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

    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, related_name="profile"
    )

    avatar_image_url = models.CharField(
        max_length=1024, null=True, blank=True, default=DEFAULT_AVATAR_URL
    )

    paypal_me_username = models.CharField(
        max_length=64, null=True, blank=True, default=None
    )

    def __str__(self):
        return u"Profile for {} ".format(self.user)


@receiver(post_save, sender=User)
def create_userprofile_when_user_created(sender, instance, created, **kwargs):
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
    currency_symbol = models.CharField(default="€", max_length=3)
    readonly = models.BooleanField(default=False)
    logo_image = FilerImageField(
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="logo_collective",
    )

    def save(self, *args, **kwargs):
        """Make sure to save changed password hashes, not as plain text."""
        if not self.id:
            self._set_password(self.password)
        else:
            password_in_db = Collective.objects.get(id=self.id).password
            if password_in_db != self.password:
                self._set_password(self.password)
        return super(Collective, self).save(*args, **kwargs)

    def check_password(self, password):
        return check_password(password, self.password)

    def is_member(self, user):
        return Membership.objects.filter(collective=self, member=user).exists()

    def add_member(self, user):
        if not self.is_member(user):
            Membership.objects.create(collective=self, member=user)

    @property
    def members(self):
        return User.objects.filter(
            membership__collective__id=self.id, is_active=True
        ).order_by("username", "first_name", "last_name")

    @property
    def stats(self):
        """Calculate financial status for each member of the Collective.

        Returns:

            {
                'median_debt': 50.00,
                'median_purchased': 15.95,
                'overall_debt': 50.00,
                'overall_purchased': 603.45,
                'member_id_to_balance': {
                    '<member1-id>': -140.23,
                    '<member2-id>': 67.04,
                    ...
                },
                'cashup': [
                    {'debtor': ..., 'creditor': ..., 'amount': ...},
                    ...
                ],
            }

        """

        collective = self

        members = collective.members
        num_members = len(members)

        purchases = collective.purchases
        num_purchases = purchases.count()

        liquidations = collective.liquidations
        num_liquidations = liquidations.count()

        prices = [purchase.price.amount for purchase in purchases]
        overall_purchased = sum(prices)

        debts = [liquidation.amount.amount for liquidation in liquidations]
        overall_debt = sum(debts)

        median_purchased = 0
        if prices:
            median_purchased = median(prices)

        median_debt = 0
        if debts:
            median_debt = median(debts)

        member_id_to_balance = {}
        for member in members:
            owed_to_collective = sum(
                [
                    get_member_share_of_purchase(purchase, member, num_members)
                    for purchase in purchases.exclude(buyer=member)
                ]
            )
            owed_from_collective = sum(
                [
                    purchase.price.amount
                    - get_member_share_of_purchase(purchase, member, num_members)
                    for purchase in purchases.filter(buyer=member)
                ]
            )

            credit = sum(
                [liq.amount.amount for liq in liquidations.filter(creditor=member)]
            )
            debt = sum(
                [liq.amount.amount for liq in liquidations.filter(debtor=member)]
            )
            has_to_pay = owed_to_collective - owed_from_collective - credit + debt

            balance = has_to_pay * -1
            if balance == 0:  # Avoid minus sign on display.
                balance = 0
            member_id_to_balance[member.id] = float(balance)

        sorted_member_balances = sorted(
            member_id_to_balance.items(), key=lambda item: item[1], reverse=True
        )

        serialized_paybacks = [
            payback.to_json() for payback in calc_paybacks(collective)
        ]

        stats = {
            "median_debt": float(median_debt),
            "median_purchased": float(median_purchased),
            "num_liquidations": num_liquidations,
            "num_purchases": num_purchases,
            "overall_debt": float(overall_debt),
            "overall_purchased": float(overall_purchased),
            "sorted_balances": sorted_member_balances,
            "cashup": serialized_paybacks,
        }
        return stats

    @property
    def liquidations(self):
        """Return Liquidations for all current members."""
        members = self.members
        queries = [
            Q(collective=self, deleted=False),
            Q(Q(creditor__in=members) | Q(debtor__in=members)),
        ]
        return Liquidation.objects.filter(*queries)

    @property
    def purchases(self):
        """Return Purchases for all current members."""
        return Purchase.objects.filter(
            collective=self, buyer__in=self.members, deleted=False
        )

    def __str__(self):
        return u"{}".format(self.name)

    def _set_password(self, password):
        """Convert plain text password to a salted hash and rotate token."""
        self.password = make_password(password)
        self.token = uuid.uuid4()


class Membership(TimestampMixin, models.Model):
    """A membership is a mapping of a user to a collective."""

    member = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    collective = models.ForeignKey("purchases.Collective", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("member", "collective")

    def __str__(self):
        return u"{} in {}".format(self.member.username, self.collective.name)


class Reaction(TimestampMixin, models.Model):
    """A reaction of a User to something else, e.g. a Purchase."""

    REACTION_POSITIVE = "positive"
    REACTION_NEUTRAL = "neutral"
    REACTION_NEGATIVE = "negative"

    REACTION_MEANINGS = (
        (REACTION_POSITIVE, "Positive"),
        (REACTION_NEUTRAL, "Neutral"),
        (REACTION_NEGATIVE, "Negative"),
    )

    meaning = models.CharField(max_length=64, choices=REACTION_MEANINGS)
    member = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    # https://simpleisbetterthancomplex.com/tutorial/2016/10/13/how-to-use-generic-relations.html  # noqa
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    @classmethod
    def get_available_meanings(cls):
        return [raw for raw, human in cls.REACTION_MEANINGS]

    def save(self, *args, **kwargs):
        """Equivalent to unique_together('member', 'content_object').

        Generic relations do not support that constraint, so we
        implement it on this level here ourselves.

        """
        if self.content_object.reactions.filter(member=self.member).exists():
            raise IntegrityError(
                "Reaction for object/member combination already exists"
            )
        super(Reaction, self).save(*args, **kwargs)


class Purchase(TimestampMixin, models.Model):
    """A Purchase describes a certain payment of a member of a Collective."""

    name = models.CharField(max_length=100)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency="EUR")
    buyer = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    collective = models.ForeignKey("purchases.Collective", on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    weights = models.ManyToManyField(
        "auth.User", through="purchases.PurchaseWeight", related_name="weighted_members"
    )
    reactions = GenericRelation(Reaction)

    def __str__(self):
        return u"{} for {} by {} in {}".format(
            self.price, self.name, self.buyer.username, self.collective.name
        )

    @property
    def kind(self):
        return "purchase"

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()


@receiver(pre_save, sender=Purchase)
def purchase_pre_save_ensure_membership(sender, instance, *args, **kwargs):
    if not instance.collective.is_member(instance.buyer):
        raise UserNotMemberOfCollectiveError(instance.buyer, instance.collective)


def get_member_share_of_purchase(
    purchase: Purchase,
    member: User,
    num_members: int,
    fallback_weight: float = 0.0,
) -> Decimal:

    if not purchase.weights.exists():
        return purchase.price.amount / num_members

    weights = PurchaseWeight.objects.filter(purchase=purchase)
    try:
        member_weight = weights.get(member=member.id).weight
    except PurchaseWeight.DoesNotExist:
        member_weight = fallback_weight

    weights_sum = sum([purchase.weight for purchase in weights])
    share_per_weight = purchase.price.amount / Decimal(weights_sum)
    return share_per_weight * Decimal(member_weight)


class PurchaseWeight(TimestampMixin, models.Model):
    purchase = models.ForeignKey("purchases.Purchase", on_delete=models.CASCADE)
    member = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    weight = models.FloatField(default=1.0)


class Liquidation(TimestampMixin, models.Model):
    """A liquidation describes a repayment of one member to another."""

    name = models.CharField(max_length=100)
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency="EUR")
    debtor = models.ForeignKey(
        "auth.User", related_name="debtor", on_delete=models.CASCADE
    )
    creditor = models.ForeignKey(
        "auth.User", related_name="creditor", on_delete=models.CASCADE
    )
    collective = models.ForeignKey("purchases.Collective", on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)

    reactions = GenericRelation(Reaction)

    def __str__(self):
        return u"{} from {} to {} in {}".format(
            self.amount,
            self.creditor.username,
            self.debtor.username,
            self.collective.name,
        )

    @property
    def kind(self):
        return "liquidation"

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()


@receiver(pre_save, sender=Liquidation)
def liquidation_pre_save_ensure_constraints(sender, instance, *args, **kwargs):
    if instance.debtor == instance.creditor:
        raise LiquidationNeedsTwoDifferentUsersError(instance.debtor)
    for user in [instance.debtor, instance.creditor]:
        if not instance.collective.is_member(user):
            raise UserNotMemberOfCollectiveError(user, instance.collective)
