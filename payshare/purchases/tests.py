import json

import pytest
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError
from model_mommy import mommy
from rest_framework import status

from payshare.purchases.models import CollectiveReadOnlyError
from payshare.purchases.models import Reaction
from payshare.purchases.calc import calc_paybacks


def test_collective_password_not_saved_as_plain_text(db):
    collective = mommy.make("purchases.Collective")
    collective.password = "foobar"
    collective.save()
    assert collective.password != "foobar"
    assert check_password("foobar", collective.password)


@pytest.fixture
def collective(db):
    collective = mommy.make("purchases.Collective", password="foobar")
    return collective


def test_collective_check_password(collective):
    assert collective.check_password("foobar")


def test_collective_change_password(collective):
    assert collective.check_password("foobar")
    collective.password = "test"
    collective.save()
    assert collective.check_password("test")


def test_collective_token_changes_on_password_changed(collective):
    old_token = collective.token
    assert old_token is not None

    collective.password = "some_other_password"
    collective.save()
    assert collective.token != old_token


def test_collective_add_member(collective):
    user = mommy.make("auth.User")
    assert not collective.is_member(user)

    collective.add_member(user)
    assert collective.is_member(user)

    collective.add_member(user)
    assert collective.is_member(user)


@pytest.fixture
def collective_with_members(collective):
    user_1 = mommy.make("auth.User", username="user_1")
    user_2 = mommy.make("auth.User", username="user_2")
    collective.add_member(user_1)
    collective.add_member(user_2)
    return collective, user_1, user_2


def test_collective_members(collective_with_members):
    collective, user_1, user_2 = collective_with_members
    assert len(collective.members) == 2
    assert user_1 in collective.members
    assert user_2 in collective.members

    user_1.is_active = False
    user_1.save()
    assert len(collective.members) == 1
    assert user_2 in collective.members


@pytest.fixture
def transfers(collective_with_members):
    collective, user_1, user_2 = collective_with_members
    purchase = mommy.make("purchases.Purchase",
                          name="my cool purchase",
                          collective=collective,
                          buyer=user_1,
                          price=45.50)
    liquidation = mommy.make("purchases.Liquidation",
                             name="my nifty liquidation",
                             collective=collective,
                             creditor=user_2,
                             debtor=user_1,
                             amount=350.0)
    return purchase, liquidation


def test_collective_purchases(collective_with_members, transfers):
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = transfers

    assert collective.purchases.count() == 1
    assert purchase in collective.purchases


def test_collective_liquidations(collective_with_members, transfers):
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = transfers

    assert collective.liquidations.count() == 1
    assert liquidation in collective.liquidations


def test_api_list_collective_needs_password(
        collective_with_members, transfers, client):
    collective, user_1, user_2 = collective_with_members

    url = "/api/v1/{}".format(collective.key)
    response = client.get(url, follow=True)  # No password via header.
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_api_list_collective(collective_with_members, client):
    collective, user_1, user_2 = collective_with_members

    url = "/api/v1/{}".format(collective.key)
    response = client.get(url, follow=True, HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == collective.id
    assert response.data["name"] == collective.name
    assert response.data["key"] == str(collective.key)

    assert len(response.data["members"]) == 2
    member_identifiers = [
        (member["username"], member["id"])
        for member in response.data["members"]
    ]
    assert (user_1.username, user_1.id) in member_identifiers
    assert (user_2.username, user_2.id) in member_identifiers


def test_api_list_transfers_needs_password_or_token(
        collective_with_members, transfers, client):
    collective, user_1, user_2 = collective_with_members
    url = "/api/v1/{}/transfers".format(collective.key)

    response = client.get(url, follow=True)  # No password via header.
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.get(url, follow=True, HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK

    response = client.get(
        url,
        follow=True,
        HTTP_AUTHORIZATION="Token {}".format(collective.token))
    assert response.status_code == status.HTTP_200_OK


def test_api_list_transfers(collective_with_members, transfers, client):
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = transfers

    url = "/api/v1/{}/transfers".format(collective.key)
    response = client.get(url, follow=True, HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK

    transfers = response.data["results"]
    assert len(transfers) == 2
    transfer_identifiers = [(obj["kind"], obj["id"]) for obj in transfers]
    assert (purchase.kind, purchase.id) in transfer_identifiers
    assert (liquidation.kind, liquidation.id) in transfer_identifiers


def test_api_list_transfers_with_search(collective_with_members,
                                        transfers,
                                        client):
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = transfers
    url = "/api/v1/{}/transfers".format(collective.key)

    # Match the purchase name only.
    response = client.get(url,
                          {"search": "cool"},
                          follow=True,
                          HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK
    transfers = response.data["results"]
    assert len(transfers) == 1
    assert transfers[0]["kind"] == purchase.kind
    assert transfers[0]["id"] == purchase.id

    # Match the liquidation name only.
    response = client.get(url,
                          {"search": "nifty"},
                          follow=True,
                          HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK
    transfers = response.data["results"]
    assert len(transfers) == 1
    assert transfers[0]["kind"] == liquidation.kind
    assert transfers[0]["id"] == liquidation.id

    # Match both via username.
    response = client.get(url,
                          {"search": user_1.username},
                          follow=True,
                          HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK
    transfers = response.data["results"]
    assert len(transfers) == 2


@pytest.fixture
def softdeleted_transfers(collective_with_members):
    collective, user_1, user_2 = collective_with_members
    purchase = mommy.make("purchases.Purchase",
                          collective=collective,
                          price=10,
                          buyer=user_1,
                          deleted=True)
    liquidation = mommy.make("purchases.Liquidation",
                             collective=collective,
                             debtor=user_1,
                             creditor=user_2,
                             amount=20,
                             deleted=True)
    return purchase, liquidation


def test_api_list_transfers_skips_softdeleted(collective_with_members,
                                              softdeleted_transfers,
                                              client):
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = softdeleted_transfers

    url = "/api/v1/{}/transfers".format(collective.key)
    response = client.get(url, follow=True, HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK

    transfers = response.data["results"]
    assert len(transfers) == 0


def test_api_create_purchase(collective_with_members, client):
    collective, user_1, user_2 = collective_with_members

    url = "/api/v1/{}/purchase".format(collective.key)
    payload = {
        "name": "Groceries",
        "buyer": user_1.id,
        "price": 15.38,
    }
    response = client.post(url,
                           json.dumps(payload),
                           content_type="application/json",
                           follow=True,
                           HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK

    purchase = response.data
    assert purchase["name"] == payload["name"]


def test_api_softdelete_purchase(collective_with_members, transfers, client):
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = transfers

    url = "/api/v1/{}/{}/{}".format(collective.key,
                                    purchase.kind,
                                    purchase.id)
    response = client.delete(url,
                             follow=True,
                             HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_api_update_purchase(collective_with_members, transfers, client):
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = transfers

    url = "/api/v1/{}/purchase/{}".format(collective.key, purchase.id)
    payload = {
        "name": "Groceries 2",
        "buyer": user_2.id,
        "price": 100.0,
    }
    response = client.put(url,
                          data=json.dumps(payload),
                          content_type="application/json",
                          follow=True,
                          HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK

    assert response.data["name"] == payload["name"]
    assert response.data["buyer"] == user_2.id
    assert float(response.data["price"]["amount"]) == payload["price"]


def test_api_create_liquidation(collective_with_members, client):
    collective, user_1, user_2 = collective_with_members

    url = "/api/v1/{}/liquidation".format(collective.key)
    payload = {
        "name": "Rent",
        "creditor": user_1.id,
        "debtor": user_2.id,
        "amount": 200.00,
    }
    response = client.post(url,
                           json.dumps(payload),
                           content_type="application/json",
                           follow=True,
                           HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK

    purchase = response.data
    assert purchase["name"] == payload["name"]


def test_api_create_reaction(collective_with_members, transfers, client):
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = transfers

    url = "/api/v1/{}/reaction".format(collective.key)
    payload = {
        "transfer_id": purchase.id,
        "transfer_kind": purchase.kind,
        "meaning": "positive",
        "member": user_2.id,
    }
    response = client.post(url,
                           json.dumps(payload),
                           content_type="application/json",
                           follow=True,
                           HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK

    reaction = response.data
    assert reaction["created_at"] is not None
    assert reaction["id"] is not None
    assert reaction["member"] == payload["member"]
    assert reaction["meaning"] == payload["meaning"]


def test_cannot_create_multiple_reactions_for_member_on_same_transfer(
        collective_with_members, transfers):
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = transfers

    Reaction.objects.create(member=user_1,
                            content_object=purchase,
                            meaning="positive")

    with pytest.raises(IntegrityError):
        Reaction.objects.create(member=user_1,
                                content_object=purchase,
                                meaning="negative")


def test_api_delete_reaction(collective_with_members, transfers, client):
    # Setup
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = transfers
    reaction = Reaction.objects.create(member=user_1,
                                       content_object=purchase,
                                       meaning="positive")

    # Test
    url = "/api/v1/{}/reaction/{}".format(collective.key, reaction.id)
    response = client.delete(url,
                             follow=True,
                             HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert Reaction.objects.count() == 0


def test_api_stats(collective_with_members, transfers, client):
    collective, user_1, user_2 = collective_with_members
    purchase, liquidation = transfers

    url = "/api/v1/{}/stats".format(collective.key)
    response = client.get(url,
                          follow=True,
                          HTTP_AUTHORIZATION="foobar")
    assert response.status_code == status.HTTP_200_OK

    stats = response.data

    assert stats["overall_debt"] == 350
    assert stats["overall_purchased"] == 45.50
    assert stats["sorted_balances"] == [
        (user_2.id, 327.25), (user_1.id, -327.25)]


def test_api_version(client):
    url = "/api/v1/version"
    response = client.get(url, follow=True)
    assert response.status_code == status.HTTP_200_OK
    import payshare  # noqa
    assert response.data == str(payshare.__version__)


@pytest.fixture
def collective_with_transfers_for_payback(collective):
    user_1 = mommy.make("auth.User", username="user_1")
    user_2 = mommy.make("auth.User", username="user_2")
    user_3 = mommy.make("auth.User", username="user_3")

    collective.add_member(user_1)
    collective.add_member(user_2)
    collective.add_member(user_3)

    mommy.make("purchases.Purchase",
               collective=collective,
               buyer=user_1,
               name="Beer",
               price=120.00)
    mommy.make("purchases.Purchase",
               collective=collective,
               buyer=user_2,
               name="Meat",
               price=90.00)
    mommy.make("purchases.Purchase",
               collective=collective,
               buyer=user_3,
               name="Sweets",
               price=5.00)

    mommy.make("purchases.Liquidation",
               collective=collective,
               creditor=user_3,
               debtor=user_2,
               amount=10.0)
    mommy.make("purchases.Liquidation",
               collective=collective,
               creditor=user_2,
               debtor=user_1,
               amount=50.0)

    return collective, user_1, user_2, user_3


def test_paybacks(collective_with_transfers_for_payback):
    collective, user_1, user_2, user_3 = collective_with_transfers_for_payback

    paybacks = calc_paybacks(collective)
    assert len(paybacks) == 3

    assert paybacks[0].debtor == user_3
    assert paybacks[0].creditor == user_1
    assert paybacks[0].amount == 48.33333333333333

    assert paybacks[1].debtor == user_3
    assert paybacks[1].creditor == user_2
    assert paybacks[1].amount == 8.333333333333329

    assert paybacks[2].debtor == user_1
    assert paybacks[2].creditor == user_2
    assert paybacks[2].amount == 50.0

    # Adding a Liquidation can flip the creditor/debtor relation,
    # as otherwise the balance would become negative.
    mommy.make("purchases.Liquidation",
               collective=collective,
               creditor=user_1,
               debtor=user_2,
               amount=60.0)
    paybacks = calc_paybacks(collective)
    assert len(paybacks) == 3

    assert paybacks[0].debtor == user_3
    assert paybacks[0].creditor == user_1
    assert paybacks[0].amount == 48.33333333333333

    assert paybacks[1].debtor == user_3
    assert paybacks[1].creditor == user_2
    assert paybacks[1].amount == 8.333333333333329

    assert paybacks[2].debtor == user_2
    assert paybacks[2].creditor == user_1
    assert paybacks[2].amount == 10.0


def test_calc_paybacks_with_negative_transfers(collective):
    user_1 = mommy.make("auth.User", username="user_1")
    user_2 = mommy.make("auth.User", username="user_2")
    user_3 = mommy.make("auth.User", username="user_3")

    collective.add_member(user_1)
    collective.add_member(user_2)
    collective.add_member(user_3)

    mommy.make("purchases.Purchase",
               collective=collective,
               buyer=user_1,
               name="Electricty Bill Refund",
               price=-90.00)

    mommy.make("purchases.Purchase",
               collective=collective,
               buyer=user_2,
               name="Pizza",
               price=15.00)

    mommy.make("purchases.Liquidation",
               collective=collective,
               creditor=user_2,
               debtor=user_3,
               name="This makes no sense, but hey",
               amount=-5.00)

    paybacks = calc_paybacks(collective)
    assert len(paybacks) == 3

    data = [
        (payback.debtor, payback.creditor, payback.amount)
        for payback in paybacks
    ]
    assert (user_1, user_2, 40.00) in data
    assert (user_1, user_3, 25.00) in data
    assert (user_2, user_3, 5.00) in data


class TestReadOnlyMiddleware:

    @pytest.fixture
    def readonly_collective(self, collective_with_members):
        collective, user_1, user_2 = collective_with_members
        collective.readonly = True
        collective.save()
        return collective

    def test_GET(self, readonly_collective, client):
        url = "/api/v1/{}".format(readonly_collective.key)
        response = client.get(url, follow=True, HTTP_AUTHORIZATION="foobar")
        assert response.status_code == status.HTTP_200_OK

    def test_OPTIONS(self, readonly_collective, client):
        url = "/api/v1/{}".format(readonly_collective.key)
        response = client.options(url,
                                  follow=True, HTTP_AUTHORIZATION="foobar")
        assert response.status_code == status.HTTP_200_OK

    def test_POST(self, readonly_collective, client):
        with pytest.raises(CollectiveReadOnlyError):
            url = "/api/v1/{}/purchase".format(readonly_collective.key)
            client.post(url, {}, follow=True, HTTP_AUTHORIZATION="foobar")

    def test_PUT(self, readonly_collective, client):
        with pytest.raises(CollectiveReadOnlyError):
            url = "/api/v1/{}/purchase".format(readonly_collective.key)
            client.put(url, {}, follow=True, HTTP_AUTHORIZATION="foobar")

    def test_PATCH(self, readonly_collective, client):
        with pytest.raises(CollectiveReadOnlyError):
            url = "/api/v1/{}/purchase".format(readonly_collective.key)
            client.patch(url, {}, follow=True, HTTP_AUTHORIZATION="foobar")

    def test_DELETE(self, readonly_collective, client):
        with pytest.raises(CollectiveReadOnlyError):
            url = "/api/v1/{}/purchase".format(readonly_collective.key)
            client.delete(url, {}, follow=True, HTTP_AUTHORIZATION="foobar")
