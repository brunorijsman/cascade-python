from cascade.key import Key
from cascade.mock_classical_channel import MockClassicalChannel
from cascade.reconciliation import Reconciliation
from cascade.shuffle import Shuffle

def create_reconciliation(seed, algorithm, key_size, error_rate):
    Key.set_random_seed(seed)
    Shuffle.set_random_seed(seed + 1)
    correct_key = Key.create_random_key(key_size)
    noisy_key = correct_key.copy(error_rate, Key.ERROR_METHOD_EXACT)
    mock_classical_channel = MockClassicalChannel(correct_key)
    reconciliation = Reconciliation(algorithm, mock_classical_channel, noisy_key, error_rate)
    return (reconciliation, correct_key)

def test_create_reconciliation():
    (_reconciliation, _correct_key) = create_reconciliation(1, "original", 32, 0.1)

def test_get_noisy_key():
    (reconciliation, _correct_key) = create_reconciliation(1, "original", 32, 0.1)
    assert reconciliation.get_noisy_key().__str__() == "00101111001011111001001010100010"

def test_get_reconciled_key():
    (reconciliation, correct_key) = create_reconciliation(1, "original", 32, 0.1)
    assert reconciliation.get_noisy_key().__str__() == "00101111001011111001001010100010"
    assert reconciliation.get_reconciled_key() is None
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == "00101111001011011001000010100110"
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()

def test_reconcile_original():
    (reconciliation, correct_key) = create_reconciliation(2, "original", 10000, 0.01)
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()

def test_reconcile_biconf():
    (reconciliation, correct_key) = create_reconciliation(3, "biconf", 10000, 0.01)
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()

def test_reconcile_yanetal():
    (reconciliation, correct_key) = create_reconciliation(4, "yanetal", 10000, 0.01)
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()

def test_reconcile_option3():
    (reconciliation, correct_key) = create_reconciliation(5, "option3", 10000, 0.01)
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()

def test_reconcile_option4():
    (reconciliation, correct_key) = create_reconciliation(6, "option4", 10000, 0.01)
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()

def test_reconcile_option7():
    (reconciliation, correct_key) = create_reconciliation(7, "option7", 10000, 0.01)
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()

def test_reconcile_option8():
    (reconciliation, correct_key) = create_reconciliation(8, "option8", 10000, 0.01)
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()

def test_reconcile_zero_errors():
    (reconciliation, correct_key) = create_reconciliation(9, "original", 10000, 0.00)
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()

def test_reconcile_many_errors():
    (reconciliation, correct_key) = create_reconciliation(10, "original", 10000, 0.90)
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()

def test_reconcile_tiny_key():
    (reconciliation, correct_key) = create_reconciliation(11, "original", 1, 0.01)
    reconciliation.reconcile()
    assert reconciliation.get_reconciled_key().__str__() == correct_key.__str__()
