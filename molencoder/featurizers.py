import numpy as np

__all__ = ["OneHotFeaturizer"]


class Featurizer(object):
    """
    Abstract class for calculating a set of features for a molecule.
    Child classes implement the _featurize method for calculating features
    for a single molecule.
    """

    def featurize(self, mols, verbose=True, log_every_n=1000):
        """
        Calculate features for molecules.
        Parameters
        ----------
        mols : iterable
            RDKit Mol objects.
        """
        mols = list(mols)
        features = []
        for i, mol in enumerate(mols):
            if mol is not None:
                features.append(self._featurize(mol))
            else:
                features.append(np.array([]))

        features = np.asarray(features)
        return features

    def _featurize(self, mol):
        """
        Calculate features for a single molecule.
        Parameters
        ----------
        mol : RDKit Mol
            Molecule.
        """
        raise NotImplementedError('Featurizer is not defined.')

    def __call__(self, mols):
        """
        Calculate features for molecules.
        Parameters
        ----------
        mols : iterable
            RDKit Mol objects.
        """
        return self.featurize(mols)


class OneHotFeaturizer(Featurizer):
    """
    NOTE(LESWING) Not Thread Safe in initialization of charset
    """

    def __init__(self, charset=None, padlength=120):
        """
        Parameters
        ----------
        charset: obj:`list` of obj:`str`
          Each string is length 1
        padlength: int
          length to pad the smile strings to
        """
        self.charset = charset
        self.pad_length = padlength

    def featurize(self, smiles, verbose=True, log_every_n=1000):
        """
        Parameters
        ----------
        mols: obj
          List of rdkit Molecule Objects
        verbose: bool
          How much logging
        log_every_n:
          How often to log
        Returns
        -------
        obj
          numpy array of features
        """
        if self.charset is None:
            self.charset = self._create_charset(smiles)
        return np.array([self.one_hot_encoded(smile) for smile in smiles])

    def one_hot_array(self, i):
        """
        Create a one hot array with bit i set to 1
        Parameters
        ----------
        i: int
          bit to set to 1
        Returns
        -------
        obj:`list` of obj:`int`
          length len(self.charset)
        """
        return [int(x) for x in [ix == i for ix in range(len(self.charset))]]

    def one_hot_index(self, c):
        """
        TODO(LESWING) replace with map lookup vs linear scan
        Parameters
        ----------
        c
          character whose index we want
        Returns
        -------
        int
          index of c in self.charset
        """
        return self.charset.index(c)

    def pad_smile(self, smile):
        """
        Pad A Smile String to self.pad_length
        Parameters
        ----------
        smile: str
        Returns
        -------
        str
          smile string space padded to self.pad_length
        """

        return smile.ljust(self.pad_length)

    def one_hot_encoded(self, smile):
        """
        One Hot Encode an entire SMILE string
        Parameters
        ----------
        smile: str
          smile string to encode
        Returns
        -------
        object
          np.array of one hot encoded arrays for each character in smile
        """
        return np.array([
            self.one_hot_array(self.one_hot_index(x)) for x in self.pad_smile(smile)
        ])

    def untransform(self, z):
        """
        Convert from one hot representation back to SMILE
        Parameters
        ----------
        z: obj:`list`
          list of one hot encoded features
        Returns
        -------
        Smile Strings picking MAX for each one hot encoded array
        """
        z1 = []
        for i in range(len(z)):
            s = ""
            for j in range(len(z[i])):
                oh = np.argmax(z[i][j])
                s += self.charset[oh]
            z1.append([s.strip()])
        return z1

    def _create_charset(self, smiles):
        """
        create the charset from smiles
        Parameters
        ----------
        smiles: obj:`list` of obj:`str`
          list of smile strings
        Returns
        -------
        obj:`list` of obj:`str`
          List of length one strings that are characters in smiles.  No duplicates
        """
        s = set()
        for smile in smiles:
            for c in smile:
                s.add(c)
        return [' '] + sorted(list(s))
