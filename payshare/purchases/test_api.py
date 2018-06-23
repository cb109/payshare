import json

import pytest
from django.contrib.auth.hashers import check_password
from model_mommy import mommy
from rest_framework import status


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
                          collective=collective,
                          buyer=user_1,
                          price=45.50)
    liquidation = mommy.make("purchases.Liquidation",
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


@pytest.fixture
def softdeleted_transfers(collective_with_members):
    collective, user_1, user_2 = collective_with_members
    purchase = mommy.make("purchases.Purchase",
                          collective=collective,
                          buyer=user_1,
                          deleted=True)
    liquidation = mommy.make("purchases.Liquidation",
                             collective=collective,
                             debtor=user_1,
                             creditor=user_2,
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
