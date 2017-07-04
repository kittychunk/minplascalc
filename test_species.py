import MinPlasCalc as mpc
import pytest


def test_molarmass():
    mm = mpc.molar_mass_calculator(8, 8, 8)
    assert mm == pytest.approx(0.016, abs=1e-3)


@pytest.fixture
def sample_species():
    return mpc.species_from_file(dataFile="NistData/O2.json")


def test_translational_partition_function(sample_species):
    partition_function = sample_species.translationalPartitionFunction(0.)
    assert partition_function == 0.


def test_internal_partition_function(sample_species):
    partition_function = sample_species.internalPartitionFunction(300)
    assert partition_function == pytest.approx(217.6606)