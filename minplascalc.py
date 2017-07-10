#!/usr/bin/env python3
#
# Classes for gas/plasma data and LTE calculations with simple species
#
# Q Reynolds 2017

import json
import numpy as np
import collections
import logging
import warnings

# utility functions ############################################################


def molar_mass_calculator(protons, neutrons, electrons):
    """Estimate the molar mass in kg/mol of a species based on its nuclear and
    electronic structure, if you can't get it anywhere else for some reason.
    """

    return constants.avogadro * (protons * constants.protonMass
                                 + electrons * constants.electronMass
                                 + neutrons * (constants.protonMass
                                               + constants.electronMass))


def parse_values(nist_line):
    """Helper function to tidy up a string of data copied from NIST online
    databases.
    """

    table = str.maketrans('', '', '+x?[]')
    line = "".join(nist_line.split()).translate(table)
    records = line.split("|")[:-1]

    values = []
    for record in records:
        if "/" in record:
            num, den = record.split("/")
            value = float(num) / float(den)
        else:
            value = float(record)
        values.append(value)
    return values


def read_energylevels(datafile):
    """ Read a NIST energy level file

    Parameters
    ----------
    datafile : str
        Filename of a NIST energy level file


    Return
    ------
    energylevels : list of dict
         Energy levels. Each dict contains fields J and Ei.
    """
    energylevels = []

    with open(datafile) as data:
        for i, line in enumerate(data):
            try:
                J, Ei = parse_values(line)
                energylevels.append({"J": J, "Ei": Ei})
            except ValueError as exception:
                logging.debug("Ignoring line %i in %s", i, datafile)
                logging.debug(exception)

    return energylevels


def buildMonatomicSpeciesJSON(name, stoichiometry, molarMass, chargeNumber,
                              ionisationEnergy, nistDataFile, sources=None):
    """Function to take text data retrieved from NIST websites or other sources

    and build a JSON object file for a monatomic plasma species, with specified
    electron energy levels and degeneracies.

    Parameters
    ----------
    name : string
        A unique identifier for the species (also the name of the JSON output
        file)
    stoichiometry : dictionary
        Dictionary describing the elemental stoichiometry of the species (e.g.
        {"O": 1} for O or O+)
    molarMass : float
        Molar mass of the species in kg/mol
    chargeNumber : int
        Charge on the species (in integer units of the fundamental charge)
    ionisationEnergy : float
        Ionisation energy of the species in 1/cm
    nistDataFile : string
        Path to text file containing raw energy level data (in NIST Atomic
        Spectra Database format)
    sources : list of dictionaries
        Each dictionary represents a reference source from which the data was
        obtained (defaults to NIST Atomic Spectra Database)
    """

    if sources is None:
        sources = [collections.OrderedDict([
            ("title", "NIST Atomic Spectra Database (ver. 5.3), [Online]."),
            ("author", "A Kramida, Yu Ralchenko, J Reader, and NIST ASD Team"),
            ("publicationInfo", "National Institute of Standards and Technology, Gaithersburg, MD."),
            ("http", "http://physics.nist.gov/asd"),
            ("doi", "NA"),
        ])]

    speciesDict = collections.OrderedDict([
        ("name", name),
        ("stoichiometry", stoichiometry),
        ("molarMass", molarMass),
        ("chargeNumber", chargeNumber),
        ("monatomicData", collections.OrderedDict([
            ("ionisationEnergy", ionisationEnergy),
            ("energyLevels", read_energylevels(nistDataFile)),
        ])),
        ("energyUnit", "1/cm"),
        ("molarMassUnit", "kg/mol"),
        ("sources", sources),
    ])

    with open(speciesDict["name"] + ".json", "w") as jf:
        json.dump(speciesDict, jf, indent=4)


def buildDiatomicSpeciesJSON(name, stoichiometry, molarMass, chargeNumber,
                             ionisationEnergy, dissociationEnergy, sigmaS,
                             g0, we, Be, sources=None):
    """Function to take text data retrieved from NIST websites or other sources
    and build a JSON object file for a diatomic plasma species, with specified
    ground state degeneracy and rotational & vibrational parameters.

    Parameters
    ----------
    name : string
        A unique identifier for the species (also the name of the JSON output
        file)
    stoichiometry : dictionary
        Dictionary describing the elemental stoichiometry of the species (e.g.
        {"Si": 1, "O": 1} for SiO or SiO+)
    molarMass : float
        Molar mass of the species in kg/mol
    chargeNumber : int
        Charge on the species (in integer units of the fundamental charge)
    ionisationEnergy : float
        Ionisation energy of the species in 1/cm
    dissociationEnergy : float
        Dissociation energy of the species in 1/cm
    sigmaS : int
        Symmetry constant (=2 for homonuclear molecules, =1 for heteronuclear)
    g0 : float
        Ground state electronic energy level degeneracy
    we : float
        Vibrational energy level constant in 1/cm
    Be : float
        Rotational energy level constant in 1/cm
    sources : list of dictionaries
        Each dictionary represents a reference source from which the data was
        obtained (defaults to NIST Chemistry Webbook)
    """
    if sources is None:
        sources = [collections.OrderedDict([
            ("title", "NIST Chemistry WebBook, NIST Standard Reference Database Number 69"),
            ("author", "PJ Linstrom and WG Mallard (Editors)"),
            ("publicationInfo", "National Institute of Standards and Technology, Gaithersburg MD., 20899"),
            ("http", "http://webbook.nist.gov/chemistry/"),
            ("doi", "10.18434/T4D303"),
        ])]

    speciesDict = collections.OrderedDict([
        ("name", name),
        ("stoichiometry", stoichiometry),
        ("molarMass", molarMass),
        ("chargeNumber", chargeNumber),
        ("diatomicData", collections.OrderedDict([
            ("ionisationEnergy", ionisationEnergy),
            ("dissociationEnergy", dissociationEnergy),
            ("sigmaS", sigmaS),
            ("g0", g0),
            ("we", we),
            ("Be", Be),
        ])),
        ("energyUnit", "1/cm"),
        ("molarMassUnit", "kg/mol"),
        ("sources", sources),
    ])

    with open(speciesDict["name"] + ".json", "w") as jf:
        json.dump(speciesDict, jf, indent=4)


# classes ######################################################################


class constants:
    """A collection of physical and unit-conversion constants useful in plasma
    calculations.
    """

    protonMass = 1.6726219e-27
    electronMass = 9.10938356e-31
    fundamentalCharge = 1.60217662e-19
    avogadro = 6.0221409e23
    boltzmann = 1.38064852e-23
    planck = 6.62607004e-34
    c = 2.99792458e8
    eVtoK = 11604.505
    eVtoJ = 1.60217653e-19
    invCmToJ = 1.9864456e-23
    JperMolToInvCm = 0.0835934811
    eVtoInvCm = 8065.54446


def species_from_file(dataFile, numberofparticles=0, x0=0):
    """Create a species from a data file.

    Parameters
    ----------
    dataFile : string
        Path to a JSON data file describing the electronic and molecular
        properties of the species
    numberofparticles : float
        Initial particle count (default 0)
    x0 : float
        initial x
    """
    # Construct a data object from JSON data file
    with open(dataFile) as df:
        jsonData = json.load(df)

    if 'monatomicData' in jsonData:
        return MonatomicSpecies(jsonData, numberofparticles, x0)
    else:
        return DiatomicSpecies(jsonData, numberofparticles, x0)


class BaseSpecies:
    def totalPartitionFunction(self, V, T):
        return (V * self.translationalPartitionFunction(T)
                * self.internalPartitionFunction(T))

    def translationalPartitionFunction(self, T):
        return ((2 * np.pi * self.molarMass * constants.boltzmann * T)
                / (constants.avogadro * constants.planck ** 2)) ** 1.5

    def internalPartitionFunction(self, T):
        raise NotImplementedError

    def internal_energy(self, T):
        raise NotImplementedError


# Diatomic molecules, single atoms, and ions
class Species(BaseSpecies):
    def __init__(self, jsonData, numberOfParticles=0, x0=0):
        """Base class for species. Either single monatomic or diatomic chemical
        species in the plasma, eg O2 or Si+

        Parameters
        ----------
        jsonData : dict
            JSON data describing the electronic and molecular
            properties of the species
        numberOfParticles : float
            Initial particle count (default 0)
        x0 : float
        """

        self.numberOfParticles = numberOfParticles
        self.numberDensity = 0.
        self.x0 = x0

        # General species data
        self.name = jsonData["name"]
        self.stoichiometry = jsonData["stoichiometry"]
        self.molarMass = jsonData["molarMass"]
        self.chargeNumber = jsonData["chargeNumber"]

        if self.chargeNumber < 0:
            # TODO is this the right exception to raise?
            raise ValueError("Error! Negatively charged ions not implemented yet.")


class MonatomicSpecies(Species):
    def __init__(self, jsonData, numberOfParticles=0, x0=0):
        super().__init__(jsonData, numberOfParticles, x0)

        self.ionisationEnergy = constants.invCmToJ * jsonData["monatomicData"]["ionisationEnergy"]
        self.deltaIonisationEnergy = 0.
        self.energyLevels = []
        for energylevel in jsonData["monatomicData"]["energyLevels"]:
            self.energyLevels.append([2. * energylevel["J"] + 1.,
                                      constants.invCmToJ * energylevel["Ei"]])
        self.E0 = 0

    def internalPartitionFunction(self, T):
        partitionVal = 0.
        for twoJplusone, Ei_J in self.energyLevels:
            if Ei_J < (self.ionisationEnergy - self.deltaIonisationEnergy):
                partitionVal += twoJplusone * np.exp(-Ei_J / (constants.boltzmann * T))
        return partitionVal

    def internal_energy(self, T):
        translational_energy = 1.5 * constants.boltzmann * T
        electronic_energy = 0.
        for twoJplusone, Ei_J in self.energyLevels:
            if Ei_J < (self.ionisationEnergy - self.deltaIonisationEnergy):
                electronic_energy += twoJplusone * Ei_J * np.exp(-Ei_J / (constants.boltzmann * T))
        electronic_energy /= self.internalPartitionFunction(T)
        return translational_energy + electronic_energy


class DiatomicSpecies(Species):
    def __init__(self, jsonData, numberOfParticles=0, x0=0):
        super().__init__(jsonData, numberOfParticles, x0)

        self.dissociationEnergy = constants.invCmToJ * jsonData["diatomicData"][
            "dissociationEnergy"]
        self.ionisationEnergy = constants.invCmToJ * jsonData["diatomicData"][
            "ionisationEnergy"]
        self.deltaIonisationEnergy = 0.
        self.sigmaS = jsonData["diatomicData"]["sigmaS"]
        self.g0 = jsonData["diatomicData"]["g0"]
        self.we = constants.invCmToJ * jsonData["diatomicData"]["we"]
        self.Be = constants.invCmToJ * jsonData["diatomicData"]["Be"]
        self.E0 = -self.dissociationEnergy

    def internalPartitionFunction(self, T):
        electronicPartition = self.g0
        vibrationalPartition = 1. / (1. - np.exp(-self.we / (constants.boltzmann * T)))
        rotationalPartition = constants.boltzmann * T / (self.sigmaS * self.Be)
        return electronicPartition * vibrationalPartition * rotationalPartition

    def internal_energy(self, T):
        translational_energy = 1.5 * constants.boltzmann * T
        electronic_energy = 0.
        rotational_energy = constants.boltzmann * T
        vibrational_energy = self.we * np.exp(-self.we / (constants.boltzmann * T)) / (1. - np.exp(-self.we / (constants.boltzmann * T)))
        return translational_energy + electronic_energy + rotational_energy + vibrational_energy


class ElectronSpecies(BaseSpecies):
    def __init__(self, numberOfParticles=0):
        """Class describing electrons as a species in the plasma.

        Parameters
        ----------
        numberOfParticles : float
            Initial particle count (default 0)
        """

        self.name = "e"
        self.stoichiometry = {}
        self.molarMass = constants.electronMass * constants.avogadro
        self.chargeNumber = -1
        self.numberOfParticles = numberOfParticles
        self.numberDensity = 0.
        self.E0 = 0
        self.x0 = 0

    # noinspection PyUnusedLocal
    def internalPartitionFunction(self, T):
        return 2.

    def internal_energy(self, T):
        translational_energy = 1.5 * constants.boltzmann * T
        electronic_energy = 0.
        return translational_energy + electronic_energy


class Element:
    def __init__(self, name="", stoichiometricCoeffts=None, totalNumber=0.):
        """Class acting as struct to hold some information about different
        elements in the plasma.

        Parameters
        ----------
        name : string
            Name of element, eg "O" (default empty string)
        stoichiometricCoeffts : array_like
            List of number of atoms of this element present in each species, in
            same order as Mixture.species (default empty list)
        totalNumber : float
            Total number of atoms of this element present in the simulation
            (conserved), calculated from initial conditions during instantiation
            of Mixture (default 0)
        """

        self.name = name
        self.stoichiometricCoeffts = [] if stoichiometricCoeffts is None else stoichiometricCoeffts
        self.totalNumber = totalNumber


class Mixture:
    def __init__(self, mixture_file, T=10000., P=101325):
        """Class representing a thermal plasma specification with multiple
        species, and methods for calculating equilibrium species concentrations
        at different temperatures and pressures using the principle of Gibbs
        free energy minimisation.

        Parameters
        ----------
        mixture_file : string
            Path to a JSON data file containing species and initial mole
            fractions
        T : float
            Temperature value in K, for initialisation (default 10000)
        P : float
            Pressure value in Pa, for initialisation (default 101325)
        """

        self.T = T
        self.P = P

        with open(mixture_file) as sf:
            jsonData = json.load(sf)

        # Random order upsets the nonlinearities in the minimiser resulting in
        # non-reproducibility between runs. Make sure this order is maintained
        self.species = [species_from_file(spData["species"], x0=spData["x0"])
                        for spData in jsonData["speciesList"]]
        self.species.append(ElectronSpecies())

        # Random order upsets the nonlinearities in the minimiser resulting in
        # non-reproducibility between runs
        elementset = sorted(set(s for sp in self.species
                                for s in sp.stoichiometry))
        self.elements = tuple(Element(name=element) for element in elementset)

        self.maxChargeNumber = max(sp.chargeNumber for sp in self.species)
        # Set species which each +ve charged ion originates from
        for sp in self.species:
            if sp.chargeNumber > 0:
                for sp2 in self.species:
                    if sp2.stoichiometry == sp.stoichiometry and sp2.chargeNumber == sp.chargeNumber - 1:
                        sp.ionisedFrom = sp2

        # Set stoichiometry and charge coefficient arrays for mass action and
        # electroneutrality constraints
        for elm in self.elements:
            elm.stoichiometricCoeffts = [sp.stoichiometry.get(elm.name, 0.)
                                         for sp in self.species]

        self.chargeCoeffts = [sp.chargeNumber for sp in self.species]

        # Set element totals for constraints from provided initial conditions
        nT0 = self.P / (constants.boltzmann * self.T)
        for elm in self.elements:
            elm.totalNumber = sum(nT0 * c * sp.x0
                                  for c, sp in zip(elm.stoichiometricCoeffts,
                                                   self.species))

        # Set up A matrix, b and ni vectors for GFE minimiser
        minimiserDOF = len(self.species) + len(self.elements) + 1
        self.gfeMatrix = np.zeros((minimiserDOF, minimiserDOF))
        self.gfeVector = np.zeros(minimiserDOF)
        self.ni = np.zeros(len(self.species))

        for i, elm in enumerate(self.elements):
            self.gfeVector[len(self.species) + i] = elm.totalNumber
            for j, sC in enumerate(elm.stoichiometricCoeffts):
                self.gfeMatrix[len(self.species) + i, j] = sC
                self.gfeMatrix[j, len(self.species) + i] = sC
        for j, qC in enumerate(self.chargeCoeffts):
            self.gfeMatrix[-1, j] = qC
            self.gfeMatrix[j, -1] = qC

    def initialiseNi(self, ni):
        for j, sp in enumerate(self.species):
            self.ni[j] = ni[j]
            sp.numberOfParticles = ni[j]

    def readNi(self):
        for j, sp in enumerate(self.species):
            self.ni[j] = sp.numberOfParticles

    def writeNi(self):
        for j, sp in enumerate(self.species):
            sp.numberOfParticles = self.ni[j]

    def writeNumberDensity(self):
        V = self.ni.sum() * constants.boltzmann * self.T / self.P
        for j, sp in enumerate(self.species):
            sp.numberDensity = self.ni[j] / V

    def recalcE0i(self):
        # deltaIonisationEnergy recalculation, using limitation theory of
        # Stewart & Pyatt 1966
        ni = self.ni
        T = self.T
        P = self.P

        V = ni.sum() * constants.boltzmann * T / P
        weightedChargeSumSqd = 0
        weightedChargeSum = 0
        for j, sp in enumerate(self.species):
            if sp.chargeNumber > 0:
                weightedChargeSum += (ni[j] / V) * sp.chargeNumber
                weightedChargeSumSqd += (ni[j] / V) * sp.chargeNumber ** 2
        zStar = weightedChargeSumSqd / weightedChargeSum
        debyeD = np.sqrt(constants.boltzmann * T
                         / (4. * np.pi * (zStar + 1.) * (ni[-1] / V)
                            * constants.fundamentalCharge ** 2))
        for j, sp in enumerate(self.species):
            if sp.name != "e":
                ai = (3. * (sp.chargeNumber + 1.)
                      / (4. * np.pi * (ni[-1] / V))) ** (1 / 3)
                sp.deltaIonisationEnergy = constants.boltzmann * T * (((ai / debyeD) ** (2 / 3) + 1) - 1) / (2. * (zStar + 1))

        for cn in range(1, self.maxChargeNumber + 1):
            for sp in self.species:
                if sp.chargeNumber == cn:
                    sp.E0 = (sp.ionisedFrom.E0
                             + sp.ionisedFrom.ionisationEnergy
                             - sp.ionisedFrom.deltaIonisationEnergy)

    def recalcGfeArrays(self):
        ni = self.ni
        T = self.T
        P = self.P

        niSum = ni.sum()
        V = niSum * constants.boltzmann * T / P
        offDiagonal = -constants.boltzmann * T / niSum
        nspecies = len(self.species)

        onDiagonal = constants.boltzmann * T / ni
        self.gfeMatrix[:nspecies, :nspecies] = offDiagonal + np.diag(onDiagonal)
        total = [sp.totalPartitionFunction(V, T) for sp in self.species]
        E0 = [sp.E0 for sp in self.species]
        mu = -constants.boltzmann * T * np.log(total / ni) + E0
        self.gfeVector[:nspecies] = -mu


    def solveGfe(self, relativeTolerance=1e-10, maxIters=1000):
        self.readNi()

        governorFactors = np.linspace(0.9, 0.1, 9)
        successYN = False
        governorIters = 0
        while not successYN and governorIters < len(governorFactors):
            successYN = True
            governorFactor = governorFactors[governorIters]
            relTol = relativeTolerance * 10.
            minimiserIters = 0
            while relTol > relativeTolerance:
                self.recalcE0i()
                self.recalcGfeArrays()

                solution = np.linalg.solve(self.gfeMatrix, self.gfeVector)

                new_ni = solution[0:len(self.species)]
                deltaNi = abs(new_ni - self.ni)
                maxAllowedDeltaNi = governorFactor * self.ni

                maxNiIndex = new_ni.argmax()
                relTol = deltaNi[maxNiIndex] / solution[maxNiIndex]

                deltaNi = deltaNi.clip(min=maxAllowedDeltaNi)
                newRelaxFactors = maxAllowedDeltaNi / deltaNi
                relaxFactor = newRelaxFactors.min()

                self.ni = (1. - relaxFactor) * self.ni + relaxFactor * new_ni

                minimiserIters += 1
                if minimiserIters > maxIters:
                    successYN = False
                    break

            governorIters += 1

        if not successYN:
            warnings.warn("Minimiser could not find a converged solution, results may be inaccurate.")

        # noinspection PyUnboundLocalVariable
        logging.debug(governorIters, relaxFactor, relTol)
        logging.debug(self.ni)

        self.writeNi()
        self.writeNumberDensity()

    def calculateDensity(self):
        """Calculate the density of the plasma in kg/m3 based on current
        conditions and species composition.
        """

        return sum(sp.numberDensity * sp.molarMass / constants.avogadro
                   for sp in self.species)

    def calculate_heat_capacity(self, init_ni=1e20, rel_delta_t=0.001):
        """Calculate the heat capacity at constant pressure of the plasma in
        J/kg.K based on current conditions and species composition. Note that
        this is done by performing two full composition simulations when this
        function is called - can be time-consuming.
        """

        T = self.T

        self.initialiseNi([init_ni for i in range(len(self.species))])
        self.T = (1 - rel_delta_t) * T
        self.solveGfe()
        enthalpy_low = self.calculate_enthalpy()

        self.initialiseNi([init_ni for i in range(len(self.species))])
        self.T = (1 + rel_delta_t) * T
        self.solveGfe()
        enthalpy_high = self.calculate_enthalpy()

        self.T = T

        return (enthalpy_high - enthalpy_low) / (2. * rel_delta_t * T)

    def calculate_enthalpy(self):
        """Calculate the enthalpy of the plasma in J/kg based on current
        conditions and species composition. Note that the value returned is not
        absolute, it is relative to an arbitrary reference which may be
        negative or positive depending on the reference energies of the diatomic
        species present.
        """

        T = self.T
        weighted_enthalpy = sum(constants.avogadro * sp.numberOfParticles * (sp.internal_energy(T) + sp.E0 + constants.boltzmann * T)
                                for sp in self.species)
        weighted_molmass = sum(sp.numberOfParticles * sp.molarMass
                               for sp in self.species)
        return weighted_enthalpy / weighted_molmass

    def calculateViscosity(self):
        """Calculate the viscosity of the plasma in Pa.s based on current
        conditions and species composition.
        """

        raise NotImplementedError

    def calculateThermalConductivity(self):
        """Calculate the thermal conductivity of the plasma in W/m.K based on
        current conditions and species composition.
        """

        raise NotImplementedError

    def calculateElectricalConductivity(self):
        """Calculate the electrical conductivity of the plasma in 1/ohm.m based
        on current conditions and species composition.
        """

        raise NotImplementedError

    def calculateTotalEmissionCoefficient(self):
        """Calculate the total radiation emission coefficient of the plasma in
        W/m3 based on current conditions and species composition.
        """

        raise NotImplementedError