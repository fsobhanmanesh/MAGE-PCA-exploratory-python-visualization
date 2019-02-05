# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 09:50:29 2013

@author: ros259
"""

#base_path = "/home/jason/Dropbox/stopgap-measure/"
base_path = "/home/ros259/Dropbox/stopgap-measure/"
#cd "/home/ros259/Dropbox/stopgap-measure/"
#cd "/home/jason/Dropbox/stopgap-measure/"

import stopgap
import sys
import os
import pysam
import cProfile, pstats, io

#bam_file='/media/Scratchy/Projects/454_Amplicons/out/bam/RLMID2cancer_sorted.bam'
#bam_file='/home/ros259/Dropbox/stopgap-measure/RLMID10cancer_sorted.bam'
#samfile = pysam.Samfile(bam_file, "rb")
if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()

    #bam_file='/home/ros259/Dropbox/stopgap-measure/tests/stop_gap-test1_bwa_sorted.bam'
    #bam_file='/home/ros259/Dropbox/stopgap-measure/RLMID10cancer_sorted.bam'
    bam_file = os.path.join(base_path, 'RLMID10cancer_sorted.bam')    
    ref_fasta_file = os.path.join(base_path, '454BisAmpliconsShrimp.fa')
    #bam_file='/home/ros259/Dropbox/stopgap-measure/tests/DLX5_Test_bwa_sorted.bam'
    samfile = pysam.Samfile(bam_file, "rb")
    #read = samfile.next()
    #ref_fasta_file = '/media/Scratchy/Projects/454_Amplicons/reference/454BisAmpliconsShrimp.fa'
    #ref_fasta_file = '/home/ros259/Dropbox/stopgap-measure/tests/stop_gap-test1.fa'
    #ref_fasta_file = '/home/ros259/Dropbox/stopgap-measure/tests/DLX5_Test.fa'
    reference = pysam.Fastafile(ref_fasta_file)
    '''
    r = RealignReads(sam_in=samfile,
                     ref_file=reference,
                     sub_matrix=default_matrix,
                     verbose=True)
    r.remapReads(30)
    
    s = RealignReads(sam_in=samfile,
                     ref_file=reference,
                     sub_matrix=shrimp_matrix,
                     gap_open=-33,
                     gap_extend=-7,
                     gap_justify='left',
                     verbose=True)
    s.remapReads(30)
    '''
    t = stopgap.RealignReads(sam_in=samfile,
                     ref=reference,
                     sam_out=os.path.join(base_path, 'test_out.sam'),
                    matrix=os.path.join(base_path, 'bismat.txt'),
                     gap_open=-10,
                     gap_extend=-6,
                     reverse_sense=True,
                     only_gapped=False,
                     softclip_ends=True,
                     compute_scores=True,
                     binary_mode=False,
                     cpus=2,
                     verbose=True)
    
    #old_sys_stdout = sys.stdout
    #sys.stdout = open('test.txt', 'w')
    t.RemapReads(1000)
    #sys.stdout.close()
    #sys.stdout = old_sys_stdout
    pr.disable()
    
    #s = io.StringIO()
    ps = pstats.Stats(pr, stream=sys.stdout)
    #ps = pstats.Stats(pr, stream=s)
    ps.sort_stats('time')
    ps.print_stats()
    #print( os.getcwd())
    #os.system("samtools view -Sb test_out.sam > test_out.bam")
    #os.system("samtools sort test_out.bam test_out_sorted")
    
    #ps.dump_stats('/home/ros259/Dropbox/stopgap-measure/profiler_results.txt')

