from turtle import delay
from urllib.parse import uses_params
import eth_keys
from eth_account._utils.signing import sign_message_hash
from hexbytes import HexBytes
from brownie import accounts, reverts


def test_payout(admin, payouts, busd, user0, chain):
    busd.transfer(payouts, 10**6 * 10**18, {'from': admin})

    winner = user0
    server = accounts.add(private_key='b25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')
    amount = 10 * 10**18
    payout_id = 42

    payouts.addServer(server, {"from": admin})

    digest = payouts.payoutDigest(
        payout_id,
        winner,
        amount
    )
    eth_private_key = eth_keys.keys.PrivateKey(HexBytes(server.private_key))
    (v, r, s, eth_signature_bytes) = sign_message_hash(eth_private_key, digest)

    tx = payouts.registerPayoutMeta(
        payout_id,
        winner,
        amount,
        server,
        v,
        r,
        s,
        {"from": admin}
    )
    assert 'PayoutRegistered' in tx.events

    balance_before = busd.balanceOf(winner)
    payouts.claimUserPayouts({"from": winner})
    balance_after = busd.balanceOf(winner)
    assert balance_after - balance_before == 0

    chain.sleep(payouts.delay())
    chain.mine()

    balance_before = busd.balanceOf(winner)
    payouts.claimUserPayouts({"from": winner})
    balance_after = busd.balanceOf(winner)
    assert balance_after - balance_before == amount


def test_payout_already_set(admin, payouts, busd, user0, chain):
    busd.transfer(payouts, 10**6 * 10**18, {'from': admin})

    winner = user0
    server = accounts.add(private_key='b25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')
    amount = 10 * 10**18
    payout_id = 42

    payouts.addServer(server, {"from": admin})

    digest = payouts.payoutDigest(
        payout_id,
        winner,
        amount
    )
    eth_private_key = eth_keys.keys.PrivateKey(HexBytes(server.private_key))
    (v, r, s, eth_signature_bytes) = sign_message_hash(eth_private_key, digest)

    tx = payouts.registerPayoutMeta(
        payout_id,
        winner,
        amount,
        server,
        v,
        r,
        s,
        {"from": admin}
    )
    assert 'PayoutRegistered' in tx.events

    balance_before = busd.balanceOf(winner)
    payouts.claimUserPayouts({"from": winner})
    balance_after = busd.balanceOf(winner)
    assert balance_after - balance_before == 0

    chain.sleep(payouts.delay())
    chain.mine()

    balance_before = busd.balanceOf(winner)
    payouts.claimUserPayouts({"from": winner})
    balance_after = busd.balanceOf(winner)
    assert balance_after - balance_before == amount



    busd.transfer(payouts, 10**6 * 10**18, {'from': admin})

    winner = user0
    server = accounts.add(private_key='b25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')
    amount = 10 * 10**18
    payout_id = 42
    with reverts('already set'):
        payouts.addServer(server, {"from": admin})


def test_payout_already_exists(admin, payouts, busd, user0, chain):
    busd.transfer(payouts, 10**6 * 10**18, {'from': admin})

    winner = user0
    server = accounts.add(private_key='b25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')
    amount = 10 * 10**18
    payout_id = 42

    payouts.addServer(server, {"from": admin})

    digest = payouts.payoutDigest(
        payout_id,
        winner,
        amount
    )
    eth_private_key = eth_keys.keys.PrivateKey(HexBytes(server.private_key))
    (v, r, s, eth_signature_bytes) = sign_message_hash(eth_private_key, digest)

    tx = payouts.registerPayoutMeta(
        payout_id,
        winner,
        amount,
        server,
        v,
        r,
        s,
        {"from": admin}
    )
    assert 'PayoutRegistered' in tx.events

    with reverts('Payouts: already exists'):
        tx = payouts.registerPayoutMeta(
        payout_id,
        winner,
        amount,
        server,
        v,
        r,
        s,
        {"from": admin}
    )


def test_payout_caller_is_not_the_owner(admin, payouts, busd, user0, chain):
    busd.transfer(payouts, 10**6 * 10**18, {'from': admin})

    winner = user0
    server = accounts.add(private_key='b25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')
    amount = 10 * 10**18
    payout_id = 42

    with reverts('Ownable: caller is not the owner'):
        payouts.addServer(server, {"from": user0})


def test_payout_signer_is_not_owner(admin, payouts, busd, user0, users):
    busd.transfer(payouts, 10**6 * 10**18, {'from': admin})

    winner = user0
    server = accounts.add(private_key='b25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')
    amount = 10 * 10**18
    payout_id = 42

    payouts.addServer(server, {"from": admin})

    digest = payouts.payoutDigest(
        payout_id,
        winner,
        amount
    )
    eth_private_key = eth_keys.keys.PrivateKey(HexBytes(server.private_key))
    (v, r, s, eth_signature_bytes) = sign_message_hash(eth_private_key, digest)

    with reverts('Payouts: signer is not server or owner'):
        tx = payouts.registerPayoutMeta(
        payout_id,
        winner,
        amount,
        users[0],
        v,
        r,
        s,
        {"from": admin}
    )


def test_cancelPayout(admin, payouts, busd, user0, chain):
    busd.transfer(payouts, 10**6 * 10**18, {'from': admin})

    winner = user0
    server = accounts.add(private_key='b25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')
    amount = 10 * 10**18
    payout_id = 42

    payouts.addServer(server, {"from": admin})

    digest = payouts.payoutDigest(
        payout_id,
        winner,
        amount
    )
    eth_private_key = eth_keys.keys.PrivateKey(HexBytes(server.private_key))
    (v, r, s, eth_signature_bytes) = sign_message_hash(eth_private_key, digest)

    tx = payouts.registerPayoutMeta(
        payout_id,
        winner,
        amount,
        server,
        v,
        r,
        s,
        {"from": admin}
    )
    assert 'PayoutRegistered' in tx.events

    tx = payouts.cancelPayout(42, {"from": admin})
    assert 'PayoutCancelled' in tx.events


def test_fail_newDelay(admin, payouts, busd, user0, chain):
    busd.transfer(payouts, 10**6 * 10**18, {'from': admin})

    winner = user0
    server = accounts.add(private_key='b25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')
    amount = 10 * 10**18
    payout_id = 42

    payouts.addServer(server, {"from": admin})
    with reverts('Payouts: fail newDelay <= MAX_DELAY'):
        tx = payouts.setDelay(2000000, {"from": admin})


def test_newDelay(admin, payouts, busd, user0, chain):
    busd.transfer(payouts, 10**6 * 10**18, {'from': admin})

    winner = user0
    server = accounts.add(private_key='b25c7db31feed9122727bf0939dc769a96564b2de4c4726d035b36ecf1e5b364')
    amount = 10 * 10**18
    payout_id = 42

    payouts.addServer(server, {"from": admin})
    tx = payouts.setDelay(100001, {"from": admin})