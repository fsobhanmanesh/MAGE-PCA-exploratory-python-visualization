'''
.. module:: GenomeRanges
   :platform: Unix, Windows
   :synopsis: A wrapper for Pandas that teaches DataFrame some new genomics
   tricks.

.. moduleauthor:: Jason Ross <jason.ross@csiro.au>

'''

#import pandas as pd
from pandas import DataFrame, merge, concat
from HTSeq import GenomicInterval, GenomicArrayOfSets
import warnings
import unittest 
#from pandas.tools.plotting import scatter_matrix
#from pandas.tools.plotting import parallel_coordinates
#import matplotlib.pyplot as plt
from numpy import array, invert
from time import localtime, strftime


__title__ = 'GenomeFrame'
__version__ = '0.0.1'
__build__ = 0x000001
__author__ = 'Jason Ross'
__license__ = 'CSIRO'
__copyright__ = 'Copyright 2013 Jason Ross'
__docformat__ = 'restructuredtext'


class GenomeIndex(object):
    '''
    Takes a Pandas DataFrame with minimally a chrom, start and end column
    and optionally a strand column. By default columns with these names are
    searched for, but the name may be overriden with an argument.
    For each row in the DataFrame, an :class:`HTSeq.GenomicInterval` object is
    instantiated. The set of unique chromosome names is used to create a
    :class:`GenomicArrayOfSets` object and this is populated with the set of
    :class:`HTSeq.GenomicInterval` objects.
    If no strand information is present, the missing strand character '.' will
    be used in the creation of GenomicInterval objects.
    If strand is specified then all row members in the column must have the
    characters '+' or '-' otherwise strand information will be ignored. This
    behaviour will also produce a warning.
    '''
    _required_columns = ['chrom', 'start', 'end']
    _legal_strands = ['+', '-']
    _missing_strands = ['.']
    _is_stranded = False
    _all_chroms = []
    index = None

    def __init__(self, df, **kwargs):
        '''
        :param df: A pandas DataFrame containing chrom, start, end and
        optionally a strand column.
        :type df: :class:`pandas,DataFrame`
        :param chrom: The column name for the chromosome information.
        :type chrom: string
        :param start: The column name for the start coordinate.
        :type start: int
        :param end: The column name for the end coordinate.
        :type end: int
        :param strand: The column name for the strand information.
        :type strand: string
        :raises: TypeError, KeyError
        '''
        # Test that columns in _required_columns are present
        mapping = kwargs
        if not isinstance(df, DataFrame):
            raise TypeError("df should be a Pandas DataFrame")
        # if chrom, start or end are not overriden then use the default
        if not mapping:
            mapping = dict(zip(self._required_columns, self._required_columns))
            if 'strand' in df.columns:
                mapping['strand'] = 'strand'
        col_test = [mapping[c] in df.columns for c in self._required_columns]
        if not array(col_test).all():
            raise KeyError("Require keyword args specifying " +
            str(self._required_columns))
        # Now we are sure the DataFrame has the required column names
        self._all_chroms = df[mapping['chrom']].unique().tolist()
        # check if there is a strand kwarg
        try:
            unique_strands = df[mapping['strand']].unique().tolist()
            # if all strand values are missing then ignore the strand column
            if set(unique_strands).issubset(self._missing_strands):
                self._is_stranded = False
            # check if the found strand values are a subset of legal strands
            if set(unique_strands).issubset(self._legal_strands):
                self._is_stranded = True
            else:
                # Warn the user that all strand information will be ignored
                warnings.warn("Strands must be all " + str(self._legal_strands)
                + " or " + str(self._missing_strands) +
                ". Instead these values of strand were given: " +
                str(unique_strands) + ". Strand information will be ignored.")
                self._is_stranded = False
        except KeyError:
            # if the strand column is not specified
            self._is_stranded = False

        self._make_index(df, mapping)

    def _make_index(self, df, mapping):
        index = GenomicArrayOfSets(self._all_chroms,
                                   stranded=self._is_stranded)
        for lab in df.index:
            if self._is_stranded:
                iv = GenomicInterval(chrom=df.loc[lab, mapping['chrom']],
                                     start=df.loc[lab, mapping['start']],
                                     end=df.loc[lab, mapping['end']],
                                     strand=df.loc[lab, mapping['strand']])
            else:
                iv = GenomicInterval(chrom=df.loc[lab, mapping['chrom']],
                                     start=df.loc[lab, mapping['start']],
                                     end=df.loc[lab, mapping['end']])
            # Record the DataFrame index value as a GenomicInterval value
            index[iv] += lab
        #self.index = index
        self = index

    def __repr__(self):
        return("GenomeIndex")

    @property
    def stranded(self):
        return self._is_stranded

    @property
    def chroms(self):
        return self._all_chroms


class GenomeFrame(DataFrame):
    '''
    A thin wrapper around a Pandas DataFrame that adds genomics class
    methods.
    The Pandas DataFrame is split into columns of experimental data and
    phenotype data. This is declared by supplying a list to pcol at
    instantiation, or later by setting the 'pcol' attribute. with a list of
    column names. If pheno is left as None then all columns are assumed to be
    experimental data.
    The class attributes, 'phenodata' and 'experimentdata' return the subset of
    columns specified by pcol or those unspecified by pcol, respectively.
    These two attributes are also in an abbreviated form, pdata and edata,
    respectively.
    The class attribute 'exprs' returns the pcol unspecified columns of the
    Pandas DataFrame coerced to a numpy array. This is useful for analysis
    functions that expect a numpy array.
    In addition to a normal Pandas DataFrame, a GenomeFrame has optional slots
    for featuredata and metadata.
    Featuredata is a Pandas DataFrame with rows that describe experimental data
    columns in the GenomeFrame object. At a minimum, featuredata needs to
    contain a column for chrom, start and end coordinates and optionally a
    strand column. These columns will be used to form a GenomeIndex object.
    Featuredata can also contain an arbitrary number of other
    columns describing the features, such as gene symbols or other identifiers.
    Featuredata can be accessed with the class artribute 'featuredata' and
    abbreviated form, 'fdata'.
    Metadata such as author, platform, run date, etc is kept in the
    metadata (dictionary) slot. The 'GenomeFrame creation date' will be added
    upon instantiation of a GenomeFrame object.
    '''
    #data = pd.DataFrame()
    _featuredata = None
    _metadata = {}
    _experimentcolumns = []
    _phenocolumns = []
    _genomeindex = None
    _genomeindex_columns = {'chrom': 'chrom', 'start': 'start',
                            'end': 'end', 'strand': 'strand'}
    _is_stranded = True

    def __init__(self, data=None, index=None, columns=None, dtype=None,
                 copy=False, pcol=None, featuredata=None, metadata=None):
        super(GenomeFrame, self).__init__(data, index, columns, dtype, copy)
        '''
        :param pcol: An optional list declaring columns as phenotype data, as
        opposed to experimental data.
        :type pcol: list
        :raises: TypeError, ValueError
        :param featuredata: A descriptive table of the features minimally
        containing columns with the names, chrom, start and end.
        :type featuredata: :class:`pandas,DataFrame`
        :raises: TypeError, ValueError
        :param metadata: An optional set of key-value metadata.
        :type metadata: dict
        :raises: TypeError
        '''
        # Set the feature property attribute
        self.fdata = featuredata
        self.mdata = metadata
        # Set the _phenocolumns and _experitmentalcolumns property attribute
        self.pcols = pcol

    def range_join(self):
        pass

    # _constructor is needed here to override the constructor called in
    # the parent frame class.
#    @property
#    def _constructor(self):
#        return super(GenomeFrame, self)._constructor

    @property
    def exprs(self):
        return self.edata.values

    @property
    def samples(self):
        return self.index.tolist()

    @samples.setter
    def samples(self, columns):
        self.index = columns

    @samples.deleter
    def samples(self):
        self.index = None

    @property
    def mdata(self):
        return self._metadata

    @mdata.setter
    def mdata(self, meta):
        if meta is None:
            meta = {}
        try:
            meta['GenomeFrame creation date'] = strftime("%Y-%m-%d %H:%M:%S",
                                                         localtime())
            #meta['GenomeFrame version'] = __version__
        except TypeError:
            raise TypeError("A dict is required for metadata.")
        self._metadata = meta

    @property
    def metadata(self):
        return self.mdata

    @metadata.setter
    def metadata(self, meta):
        self.mdata = meta

    @property
    def ecols(self):
        return self._experimentcolumns

    @property
    def pcols(self):
        return self._phenocolumns

    @pcols.setter
    def pcols(self, pheno):
        '''
        Requires a list.
        '''
        expt_cols = []
        pheno_cols = []
        if pheno is None:
            self._experimentcolumns = self.columns
            self._phenocolumns = None
            return
        if not isinstance(pheno, list):
            raise TypeError("A list is required for setting pheno columns")
        # Create a column name dict for quick lookups
        col_dict = dict(zip(self.columns, range(0, len(self.columns))))
        is_pheno = array([c in pheno for c in col_dict])
        is_expt = invert(is_pheno)
        num_pheno = sum(is_pheno)
        num_expt = sum(is_expt)
        # Sanity check!
        if num_pheno + num_expt != len(self.columns):
            raise ValueError("Not all phenotype columns could be found in \
            the GenomeFrame.")
        # Assign values
        if num_pheno > 0:
            pheno_cols = self.columns[is_pheno].tolist()
        if num_expt > 0:
            expt_cols = self.columns[invert(is_pheno)].tolist()
        self._phenocolumns = pheno_cols
        self._experimentcolumns = expt_cols

    @property
    def pdata(self):
        if len(self._phenocolumns) == 0:
            return None
        else:
            return self[self._phenocolumns]

    @property
    def phenodata(self):
        return self.pdata

    @property
    def edata(self):
        if len(self._experimentcolumns) == 0:
            return None
        else:
            return self[list(self._experimentcolumns)]

    @property
    def experimentdata(self):
        return self.edata

    @property
    def features(self):
        return list(self._experimentcolumns)

    @property
    def fdata(self):
        return self._featuredata

    @property
    def featuredata(self):
        return self.fdata

    @fdata.setter
    def fdata(self, featuredata):
        if featuredata is None:
            self._featuredata = None
            self._genomeindex = None
        else:
            self._featuredata = self._check_fdata(featuredata)
            self._genomeindex = self._form_gindex()

    @featuredata.setter
    def featuredata(self, featuredata):
        self.fdata = featuredata

    def _check_fdata(self, featuredata):
        gindex_columns = [self._genomeindex_columns['chrom'],
                          self._genomeindex_columns['start'],
                          self._genomeindex_columns['end']]

        if not isinstance(featuredata, DataFrame):
            raise TypeError("featuredata should be an instance of a \
            pandas DataFrame")
        # check if the required location columns are present
        if not set(gindex_columns).issubset(featuredata.columns):
            raise ValueError("featuredata needs columns with these names" +
            gindex_columns + " and optinally the strand column " +
            self._genomeindex_columns['strand'])

        if featuredata.shape[0] != len(self._experimentcolumns):
            raise ValueError("The number of featuredata rows does not match \
            the number of experimental columns in the GenomeFrame data (" +
            featuredata.shape[0] + " vs " + len(self._experimentcolumns), ")")
        # Look for identity in the index values
        if (featuredata.index == self._experimentcolumns).sum() == \
        len(self._experimentcolumns):
            return featuredata
        else:
            # Perhaps the feature data is out of order?
            # Try ordering the index as a last ditch effort
            if set(featuredata.index).issubset(self._experimentcolumns):
                ordered_fdata = featuredata.loc[self._experimentcolumns]
                warnings.warn("Recovered out of order feature data.")
                return ordered_fdata
            else:
                raise ValueError("featuredata needs to have the same index \
                values as the experimental data")

    def _form_gindex(self):
        return GenomeIndex(self._featuredata)

    def _concurrency(self):
        pass


class GenomePanel(GenomeFrame):
    '''A thin wrapper around a Pandas DataFrame that adds genomics class
    methods'''
    pass


class AnnotationMapping(object):

    _anno = {}

    def __init__(self):
        pass

    def annotations(self):
        '''Return the names of the mapped annotations'''
        return self._anno.keys()


def TestSuite():
    pass


class Phenotype(object):
    '''
    '''
    data = DataFrame()
    #adata = None

    def __init__(self, data=data):
        pass


class GenomicSet(GenomeFrame):
    '''Accepts a Pandas DataFrame which is composed of a matrix of assaydata \
    where each column is a sample and each row is a feature. \
    and optionally
    '''
    data = DataFrame()
    #adata = None

    def __init__(self, assaydata=data, phenodata=None, featuredata=None,
                 experimentdata=None, genome_coords=None):
        pass

    def assaydata(self):
        pass

    def phenodata(self):
        pass

    def experimentdata(self):
        pass

    def annotation(self):
        pass

    def sample_mask(self):
        pass

    def feature_mask(self):
        pass

    def genomic_interval(self):
        pass

    def feature_mappings(self):
        pass


class GenomeFrame_with_seperate_sampledata(DataFrame):
    '''A thin wrapper around a Pandas DataFrame that adds genomics class
    methods'''
    #data = pd.DataFrame()
    _featuredata = None
    _sampledata = None
    _genomeindex = None
    _genomeindex_columns = {'chrom': 'chrom', 'start': 'start',
                            'end': 'end', 'strand': 'strand'}
    _is_stranded = True

    #def __init__(self, data=None, index=None, columns=None, copy=False,
    #             featuredata=None):
    def __init__(self, data=None, index=None, columns=None, dtype=None,
                 copy=False, featuredata=None, sampledata=None):
        '''If the GenomeFrame is constructed with a DataFrame then don't
        override the indices'''
        #def __init__(self, *args, **kwargs):
            #self.featuredata = kwargs.pop('featuredata', None)
            #super(GenomeFrame, self).__init__(*args, **kwargs)
        #if isinstance(data, DataFrame):
        #    if index is not None or columns is not None:
        #        warnings.warn("Feature and samplenames will be ignored and \
        #        indices from the DataFrame used instead")
        #    super(GenomeFrame, self).__init__(data)
        #if not isinstance(data, DataFrame):
        #    super(GenomeFrame, self).__init__(data, index=index,
        #                                        columns=columns)
        super(GenomeFrame, self).__init__(data, index, columns, dtype, copy)
        # Set the feature and sample property attributes
        self.featuredata = featuredata
        self.sampledata = sampledata

    @classmethod
    def range_join(self):
        pass

    # _constructor is needed here to override the constructor called in
    # the parent frame class.
#    @property
#    def _constructor(self):
#        return super(GenomeFrame, self)._constructor

    @property
    def exprs(self):
        return self.values

    @property
    def samples(self):
        return self.columns.tolist()

    @samples.setter
    def samples(self, columns):
        self.columns = columns

    @samples.deleter
    def samples(self):
        self.columns = None

    @property
    def features(self):
        return self.index.tolist()

    @features.setter
    def features(self, index):
        self.index = index
        if self._featuredata is not None:
            self._featuredata.index = index

    @features.deleter
    def features(self):
        self.index = None
        if self._featuredata is not None:
            self._featuredata.index = None

    @property
    def featuredata(self):
        return self._featuredata

    @featuredata.setter
    def featuredata(self, featuredata):
        if featuredata is None:
            self._featuredata = None
            self._genomeindex = None
        else:
            self._featuredata = self._check_fdata(featuredata)
            self._genomeindex = self._form_gindex()

    @property
    def sampledata(self):
        return self._sampledata

    @sampledata.setter
    def sampledata(self, sampledata):
        if sampledata is None:
            self._sampledata = None
        else:
            self._sampledata = self._check_sdata(sampledata)

    def _check_fdata(self, featuredata):
        gindex_columns = [self._genomeindex_columns['chrom'],
                          self._genomeindex_columns['start'],
                          self._genomeindex_columns['end']]

        if not isinstance(featuredata, DataFrame):
            raise TypeError("featuredata should be an instance of a \
            pandas DataFrame")
        # check if the required location columns are present
        if not set(gindex_columns).issubset(featuredata.columns):
            raise ValueError("featuredata needs columns with these names" +
            gindex_columns + " and optinally the strand column " +
            self._genomeindex_columns['strand'])

        if featuredata.shape[0] != self.shape[0]:
            raise ValueError("featuredata does not have the same number \
            of rows as the GenomeFrame data (" +
            featuredata.shape[0] + " vs " + self.shape[0], ")")
        # Look for identity in the index values
        if (featuredata.index == self.index).sum() == self.shape[0]:
            return featuredata
        else:
            # Perhaps the feature data is out of order?
            # Try ordering the index as a last ditch effort
            if set(featuredata.index.tolist()).issubset(self.index.tolist()):
                ordered_fdata = featuredata.loc[self.index]
                warnings.warn("Recovered out of order feature data.")
                return ordered_fdata
            else:
                raise ValueError("featuredata needs to have the same index \
                values as the experimental data")

    def _check_sdata(self, sampledata):
        if not isinstance(sampledata, DataFrame):
            raise TypeError("sampledata should be an instance of a \
            pandas DataFrame")
        if sampledata.shape[0] != self.shape[1]:
            raise ValueError("The number of sampledata rows should equal\
            same number of columns as the experimental data (" +
            sampledata.shape[0] + " vs " + self.shape[1], ")")
        # Look for identity in the index values
        if (sampledata.index == self.columns).sum() == self.shape[1]:
            return sampledata
        else:
            # Perhaps the feature data is out of order?
            # Try ordering the index as a last ditch effort
            if set(sampledata.index.tolist()).issubset(self.columns.tolist()):
                ordered_fdata = sampledata.loc[self.columns]
                warnings.warn("Recovered out of order feature data.")
                return ordered_fdata
            else:
                raise ValueError("Labels of the sampledata index and \
                experimental data columns should be identical")

    def _form_gindex(self):
        return GenomeIndex(self._featuredata)

    def _concurrency(self):
        pass


class TestGenomicFrame(unittest.TestCase):

    #def __init__(self):
    def setUp(self):
        self.data = DataFrame({'subject1': [2, 12, 10, 5],
                          'subject2': [4, 11, 11, 7],
                          'subject3': [3, 7, 22, 2],
                          'subject4': [7, 6, 0, 2],
                          'subject5': [2, 5, 7, 2]
                          }, index=['A', 'B', 'C', 'D'])

        self.fd = DataFrame({'chrom': ['chr1', 'chr2', 'chr3', 'chr1'],
                        'start': [1, 5, 100, 200],
                        'end': [6, 20, 105, 201],
                        'strand': ['-', '+', '+', '-']},
                       index=['A', 'D', 'C', 'B'])

        self.pd = DataFrame({'Age': [92, 76, 51, 25, 56],
                        'Gender': ['M', 'F', 'F', 'F', 'M'],
                        'Disease': ['Cancer', 'Cancer', 'Normal', 'Normal',
                                    'Cancer'],
                        'Alive': [True, True, False, True, False]},
                        index=['subject1', 'subject2', 'subject3', 'subject4',
                               'subject5'])
        self.m = merge(self.data.T, self.pd, left_index=True,
                              right_index=True)

    #def setUp(self):
    #    pass

    def testGenomicFrame(self):
        gf = GenomeFrame(data=self.m)
        self.assertEqual(None, gf.pcols)
        gf.pcols = self.pd.columns.tolist()
        self.assertEqual(['Age', 'Alive', 'Disease', 'Gender'], gf.pcols)
        self.assertEqual(['subject1', 'subject2', 'subject3', 'subject4',
                          'subject5'], gf.samples)
        self.assertEqual(concat([gf.edata, gf.pdata], axis=1), gf)

    def testFeatureData(self):
        gf = GenomeFrame(data=self.m, pcol=self.pd.columns.tolist())
        self.assertEqual(None, gf.featuredata)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
