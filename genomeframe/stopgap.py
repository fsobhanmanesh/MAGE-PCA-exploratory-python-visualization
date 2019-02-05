#!/usr/bin/env python
'''
Created on 17/06/2013

@author: ros259
'''

version = 0.01

import multiprocessing as mp
import pysam
import nwalign as nw
import unittest
from scipy.stats import itemfreq
import itertools

#import copy_reg
#import types


'''
def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    if func_name.startswith('__') and not func_name.endswith('__'):
        cls_name = cls.__name__.lstrip('_')
        func_name = '_' + cls_name + func_name
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    for cls in cls.__mro__:
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)


copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
'''

def _map_unwrap(arg, **kwarg):
    '''    
    try:
        realigned = RealignReads._RealignReadTest(*arg, **kwarg)
    except:
        raise "Multiprocessor exception"
    return realigned
    '''
    return RealignReads._RealignReadTest(*arg, **kwarg)


class RealignReads(object):
    '''
    ref: dict
    read: SeqRecord
    '''
    def __init__(self, sam_in, ref, sam_out, matrix=None,
                 gap_open=-16,
                 gap_extend=-4,
                 reverse_sense=False,
                 only_gapped=False,
                 softclip_ends=True,
                 compute_scores=True,
                 binary_mode=True,
                 cpus=mp.cpu_count(),
                 verbose=True):
        if not isinstance(sam_in, pysam.Samfile):
            raise AttributeError('Need pysam samfile object')
        if not isinstance(ref, pysam.Fastafile):
            raise AttributeError('Need pysam samfile object')

        self.sam_in = sam_in
        self.ref = ref
        self.sam_out = sam_out
        if matrix is None:
            self.matrix = '/home/ros259/Dropbox/stopgap-measure/bismat.txt'
        else:
            self.matrix = matrix
        self.gap_open = gap_open
        self.gap_extend = gap_extend
        self.reverse_sense=reverse_sense
        self.only_gapped=only_gapped
        self.softclip_ends = softclip_ends
        self.compute_scores = compute_scores
        self.binary_mode = binary_mode
        self.cpus = cpus
        self.verbose = verbose
        self.refnames = sam_in.references
        self.matrix_scores = self._MakeMatrixLookup()
        
        print self.cpus
#    def __call__(self, read):
#        return self._RealignRead(read)
    '''
    def __getstate__(self):
        pass
        return()
    
    def __setstate__(self, state):
        pass
    '''
    
    def _RealignReadList(self, readlist):
        return [self._RealignReadTest(read) for read in readlist]

    def _RealignReadTest(self, read):
        print "Hello"
        return

    
    def _RealignRead(self, read):
        has_score = False

        if read.is_unmapped is True:
            #self._out.write(read)
            return read
    
        tags = read.tags
        '''If any of the read tags are AS, then remember the read has an
        existing score.'''
        for i in range(0, len(tags)):
            if tags[i][0] == 'AS':
                has_score = True
                continue

        if self.only_gapped is True:
            has_indel = False
            for c in read.cigar:
                if c[0] == 1 or c[0] == 2:
                    # read has an indel
                    has_indel = True
                    break
            if has_indel == False:
                # Read must not have an indel
                '''
                If the read is a perfect match then don't realign
                '''
                print(read.qname + ', ' + str(read.cigar) + " does not have an indel")
                #self._out.write(read)
                return read

        fivep_soft_clip = 0
        threep_soft_clip = 0
        cigar_last = len(read.cigar) - 1
        if read.cigar[0][0] == 4:
            fivep_soft_clip = read.cigar[0][1]
        if read.cigar[cigar_last][0] == 4:
            threep_soft_clip = read.cigar[cigar_last][1]

        ref = self.ref.fetch(reference=self.refnames[read.tid],
                                      start=read.aend - read.alen - fivep_soft_clip,
                                      end=read.aend + threep_soft_clip)


        # Realign sense strand reads
        query = ''
        subject = ''
        if self.reverse_sense is True and read.is_reverse is False:
            query = self.ReverseSeq(read.seq)
            subject = self.ReverseSeq(ref.upper())
            #query = Seq(read.seq).complement().tostring()
            #subject = Seq(ref.upper()).complement().tostring()
        else:
            query = read.seq
            subject = ref.upper()

        print query, subject
        aln = nw.global_align(query, subject,
                              gap_open=self.gap_open,
                              gap_extend=self.gap_extend,
                              matrix=self.matrix)

        if self.compute_scores is True:
            score = nw.score_alignment(aln[0], aln[1],
                                       gap_open=self.gap_open,
                                       gap_extend=self.gap_extend,
                                       matrix=self.matrix)

            if has_score is True:
                as_index = None
                tags = read.tags
                for i in range(0, len(tags)):
                    if tags[i][0] == 'AS':
                        as_index = i
                if as_index is None:
                    raise ValueError("Read " + read.qname +
                    " is missing an alignment score.")
                tags[as_index] = ('AS', score)
                read.tags = tags
            else:
                read.tags = [('AS', score)] + read.tags 
        
        bam_cigar = self._MakeBamCigar(aln, read)
        if self.reverse_sense is True and read.is_reverse is False:
            bam_cigar.reverse()
        
        if self.verbose is True:
            self.PrettyPrint(read, aln, bam_cigar)

        # New read
        read.cigar = bam_cigar
        read.tags = read.tags + [('OC', self._MakeSamCigar(read.cigar)),
                                 ('OP', read.pos)]
        #self._out.write(read)
        return read


    def RemapReads(self, count=None):

        counter = 0
        write_mode = 'wb'
        if self.binary_mode is False:
            write_mode = 'wh'
        self._out = pysam.Samfile(self.sam_out,
                                  mode=write_mode,
                                  referencenames=self.sam_in.references,
                                  referencelengths=self.sam_in.lengths,
                                  header=self._MakeHeader(self.sam_in.header)
                                  )
        
        read_iter = itertools.islice(self.sam_in.fetch(), count)        
        p = mp.Pool(self.cpus)

        chunk_size = 10
        while True:        
            aligned_reads = list(itertools.islice(read_iter, chunk_size))
            #aligned_reads = itertools.islice(read_iter, chunk_size)
            # Check if there are any reads left
            print len(aligned_reads)
            if len(aligned_reads) == 0:
                break

            remapped_reads = p.map(_map_unwrap, zip([self]*len(aligned_reads), aligned_reads))
            for read in remapped_reads:
                self._out.write(read)
            
        self._out.close
        return


    def RemapReadsSingle(self, count=None):
        #scores = {}
        counter = 0
        has_score = False
        write_mode = 'wb'
        if self.binary_mode is False:
            write_mode = 'wh'
        self._out = pysam.Samfile(self.sam_out,
                                  mode=write_mode,
                                  referencenames=self.sam_in.references,
                                  referencelengths=self.sam_in.lengths,
                                  header=self._MakeHeader(self.sam_in.header)
                                  )

        for read in self.sam_in.fetch():
            'Optional setting of count, to only realign count reads'
            if count is not None and counter > count:
                break
            if read.is_unmapped is True:
                self._out.write(read)
                continue
            if counter == 0:
                # Check if an alignment score is already present
                # If it is then record this in the has_score flag
                tags = read.tags
                for i in range(0, len(tags)):
                    if tags[i][0] == 'AS':
                        has_score = True
                        continue
            if self.only_gapped is True:
                has_indel = False
                for c in read.cigar:
                    if c[0] == 1 or c[0] == 2:
                        # read has an indel
                        has_indel = True
                        break
                if has_indel == False:
                    # Read must not have an indel
                    print(read.qname + ', ' + str(read.cigar) + " does not have an indel")
                    self._out.write(read)
                    continue
                    '''
                    if the read is a perfect match then don't realign
                    '''

            fivep_soft_clip = 0
            threep_soft_clip = 0
            cigar_last = len(read.cigar) - 1
            if read.cigar[0][0] == 4:
                fivep_soft_clip = read.cigar[0][1]
            if read.cigar[cigar_last][0] == 4:
                threep_soft_clip = read.cigar[cigar_last][1]

            ref = self.ref.fetch(reference=self.refnames[read.tid],
                                          start=read.aend - read.alen - fivep_soft_clip,
                                          end=read.aend + threep_soft_clip)

            # Realign sense strand reads
            query = ''
            subject = ''
            if self.reverse_sense is True and read.is_reverse is False:
                query = self.ReverseSeq(read.seq)
                subject = self.ReverseSeq(ref.upper())
                #query = Seq(read.seq).complement().tostring()
                #subject = Seq(ref.upper()).complement().tostring()
            else:
                query = read.seq
                subject = ref.upper()

            aln = nw.global_align(query, subject,
                                  gap_open=self.gap_open,
                                  gap_extend=self.gap_extend,
                                  matrix=self.matrix)

            if self.compute_scores is True:
                score = nw.score_alignment(aln[0], aln[1],
                                           gap_open=self.gap_open,
                                           gap_extend=self.gap_extend,
                                           matrix=self.matrix)

                if has_score is True:
                    as_index = None
                    tags = read.tags
                    for i in range(0, len(tags)):
                        if tags[i][0] == 'AS':
                            as_index = i
                    if as_index is None:
                        raise ValueError("Read " + read.qname +
                        " is missing an alignment score.")
                    tags[as_index] = ('AS', score)
                    read.tags = tags
                else:
                    read.tags = [('AS', score)] + read.tags 

            bam_cigar = self._MakeBamCigar(aln, read)
            if self.reverse_sense is True and read.is_reverse is False:
                bam_cigar.reverse()

            if self.verbose is True:
                self.PrettyPrint(read, aln, bam_cigar)

            # New read
            read.cigar = bam_cigar
            read.tags = read.tags + [('OC', self._MakeSamCigar(read.cigar)),
                                     ('OP', read.pos)]
            self._out.write(read)
            counter += 1
        self._out.close

    def PrettyPrint(self, read, aln, bam_cigar):
                #if read.cigar != aln.bam_cigar():
        sam_cigar = self._MakeSamCigar(bam_cigar)
        print(read.qname)
        print('      ' + read.seq)
        #fancy = read.fancy_str()
        #print fancy
        #print("First:")
        print('Ref : ' + aln[1])
        print('Read: ' + aln[0])
        print(read.cigar)
        print(bam_cigar)
        print(sam_cigar)
        print('#########################################')

    def ReverseSeq(self, seq):
        seq_list = list(seq)
        seq_list.reverse()
        rev_seq = ''.join(seq_list)
        return rev_seq

    def _MakeMatrixLookup(self):
        matrix_handle = open(self.matrix)
        matrix_scores = {}
        col_index = None
        row_count = 0
        col_count = 0
        for l in matrix_handle:
            if l.startswith('#'):
                continue
            if l.startswith('\n'):
                continue
            row = l.strip().split()

            if col_index is None:
                col_index = row
                col_count = len(col_index)
                continue

            row_index = row.pop(0)
            if len(row) != col_count:
                raise TypeError("Matrix row elements different to alphabet \
                length in cols(" + str(col_count) + ")")

            for i in range(0, col_count):
                #print(col_index[i] + row_index + " = " + str(row[i]))
                matrix_scores[(col_index[i], row_index)] = row[i]
            row_count += 1
        if row_count != col_count:
            raise TypeError("Number of matrix rows (" + 
            str(row_count) + ") not equal to columns (" +
            str(col_count) + ").")
        return matrix_scores

    def _MakeBamCigar(self, aln, read):
        '''
        Operation to BAM mapping
        Op # Desc
        M  0 Match or mismatch
        I  1 Insertion to the ref
        D  2 Deletion from the ref
        N  3 Skipped from the ref
        S  4 Soft clipping (clipped sequences present in SEQ)
        H  5 Hard clipping (clipped sequences not present in SEQ)
        P  6 Padding (silent deletion from padded reference)
        =  7 sequence match
        X  8 sequence mismatch

        H needs to be the first or last operation
        Sum of lengths of M/I/S/=/X shall equal the length of SEQ
        '''

        q_seq = aln[0]
        s_seq = aln[1]
        gap_char = '-'

        cigar_list = None
        op_state = None
        mismatch = 0
        op_length = 0
        q_len = len(q_seq)
        del_length = 0

        for i in range(q_len):
            # set op as 0 (match) by default
            op = 0
            s = s_seq[i]
            q = q_seq[i]

            if s == gap_char:
                # Insertion
                op = 1
                mismatch += 1
                del_length = 0
            elif q == gap_char:
                # Deletion
                op = 2
                mismatch += 1
                # Increment deletion length
                # This is used to trim dels at the start of the read later
                del_length += 1
            else:
                score = 0
                del_length = 0
                try:
                    score = self.matrix_scores[(s, q)]
                except KeyError:
                    raise KeyError("Can't find " + s + "/" + q +
                        " in matrix for read " + read.qname)
                    print(read.fancy_str())
                if score <= 0:
                    '''
                    If the substitution matrix has a zero or negative score
                    then call it a mismatch
                    '''
                    mismatch += 1
                else:
                    mismatch = 0

            if cigar_list is None:
                if del_length > 0:
                    # Don't count extra reference at the start
                    continue

                if mismatch > 0 or op == 1:
                    '''
                    If there is a mismatch (0 or less match score)
                    or an insertion at the start of the read then softclip it.
                    '''
                    op = 4

                op_state = op
                op_length = 1
                cigar_list = []
                continue
            if op_state == 4 and mismatch > 0:
                op = 4

            # Add to cigar now...
            if op_state == op:
                op_length += 1
            else:
                cigar_list.append((op_state, op_length))
                op_state = op
                op_length = 1

        # Add last element to cigar
        if mismatch == 0:
            cigar_list.append((op_state, op_length))
        else:
            '''Convert an insertion at the end of the ref into a read softclip'''
            # A deletion from the ref at the end means the ref is too long
            # Ignore adding this to the cigar string
            cigar_list.append((op_state, op_length - mismatch))
            cigar_list.append((4, mismatch - del_length))

        return cigar_list


    def _MakeSamCigar(self, bam_cigar):

        sam_cigar = ''
        for op, op_length in bam_cigar:
            sam_cigar += str(op_length) + 'MIDNSHP=X'[op]
        return sam_cigar


    def MakeBam(self, ref_name, aln):
        qual_list = self.sam_quality()        
        qual = ''.join(qual_list[aln.begin:aln.end])
        bam = pysam.AlignedRead()
        bam.qname = self.read.name
        bam.seq=self.read.seq.tostring()
        bam.flag = 0
        #bam.rname = ref_name
        bam.pos = aln.begin + 1
        bam.mapq = 255
        bam.cigar = aln.bam_cigar()
        bam.qual = qual
        bam.tags = ( ("NM", 1),
                   ("RG", "L1") )
        return bam

    def _MakeHeader(self, header):
        
        if not isinstance(header, dict):
            print("Header is not a dict")
            print(header)
            header = {}
        new_pg = {'CL': 'command line',
                  'ID': 'stopgap',
                  'PN': 'stopgap',
                  'VN': version}

        if header.has_key('PG'):
            pg_list = header['PG']
            # existing_pg is a list with a dict inside
            new_pg['PP'] = pg_list[len(pg_list) - 1]['ID']
        else:
            pg_list = []

        pg_list.append(new_pg)
        header['PG'] = pg_list
        return header

class TestSuite(unittest.TestCase):

    def test_matches(self):

        test1 = ('ACGTACGT', 'ACGTACGT')
        self.assertEqual(RealignReads._MakeBamCigar(test1), [(0, 8)])
        test2 = ('AGCTACGT', 'ACGTACGT')
        self.assertEqual(RealignReads._MakeBamCigar(test2), [(0, 8)])
        
        
    
    def test_softclips(self):
        # aln1 is ref
        # aln0 is read
        test1 = ('ATTTACGTACGT', '----ACGTACGT')
        self.assertEqual(self._MakeBamCigar(test1), [(4, 4), (0, 8)])
        test2 = ('----ACGTACGT', 'ATTTACGTACGT')
        self.assertEqual(self._MakeBamCigar(test2), [(0, 8)])
        test3 = ('A----CGTACGT', 'ATTTACGTACGT')
        self.assertEqual(self._MakeBamCigar(test3), [(0, 1), (2, 4), (0, 7)])
        
        
        
        
        
        pass


if __name__ == '__main__':
    unittest.main()
