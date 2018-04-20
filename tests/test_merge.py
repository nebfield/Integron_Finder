# -*- coding: utf-8 -*-

####################################################################################
# Integron_Finder - Integron Finder aims at detecting integrons in DNA sequences   #
# by finding particular features of the integron:                                  #
#   - the attC sites                                                               #
#   - the integrase                                                                #
#   - and when possible attI site and promoters.                                   #
#                                                                                  #
# Authors: Jean Cury, Bertrand Neron, Eduardo PC Rocha                             #
# Copyright © 2015 - 2018  Institut Pasteur, Paris.                                #
# See the COPYRIGHT file for details                                               #
#                                                                                  #
# integron_finder is free software: you can redistribute it and/or modify          #
# it under the terms of the GNU General Public License as published by             #
# the Free Software Foundation, either version 3 of the License, or                #
# (at your option) any later version.                                              #
#                                                                                  #
# integron_finder is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                   #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with this program (COPYING file).                                          #
# If not, see <http://www.gnu.org/licenses/>.                                      #
####################################################################################

import tempfile
import os
import shutil
import sys
import glob

from Bio import BiopythonExperimentalWarning
import warnings
warnings.simplefilter('ignore', FutureWarning)
warnings.simplefilter('ignore', BiopythonExperimentalWarning)
from Bio import SeqIO, Seq

try:
    from tests import IntegronTest
except ImportError as err:
    msg = "Cannot import integron_finder: {0!s}".format(err)
    raise ImportError(msg)

import integron_finder.scripts.split as split


class TestMerge(IntegronTest):

    def setUp(self):
        tmp_dir = tempfile.gettempdir()
        self.out_dir = os.path.join(tmp_dir, 'test_integron_merge')
        if os.path.exists(self.out_dir) and os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir)
        os.makedirs(self.out_dir)
        self.replicons = ('acba.007.p01.13', 'lian.001.c02.10', 'pssu.001.c01.13')
        self.res_dirs = []
        for rep in self.replicons:
            res_dir = os.path.join(self.out_dir, 'Result_{}'.format(rep))
            os.makedirs(res_dir)
            in_dir = self.find_data('Results_Integron_finder_()'.format(rep))
            shutil.copyfile(os.path.join(in_dir, '{}.integrons'.format(rep)), res_dir)
            for gbk in glob.glob(os.path.join(in_dir, '*.gbk')):
                shutil.copyfile(gbk, res_dir)
            for pdf in glob.glob(os.path.join(in_dir, '*.pdf')):
                shutil.copyfile(pdf, res_dir)
            self.res_dirs.append(res_dir)


    def tearDown(self):
        if os.path.exists(self.out_dir) and os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir)

    def test_merge(self):

        result_to_merge = [self.find_data('Results_Integron_Finder_{}'.format(r) for r in replicons)
        chunk_names = split.split(replicon_path, outdir=self.out_dir)




class TestParseArgs(IntegronTest):

    def test_parse_one_result(self):
        parsed_args = split.parse_args(['outdir', 'outfile' 'result_1'])
        self.assertEqual(parsed_args.outdir, None)
        self.assertEqual(parsed_args.outfile, 'foo')
        self.assertTupleEqual(parsed_args.outfile.results, ('result_1',))
        self.assertEqual(parsed_args.quiet, 0)
        self.assertEqual(parsed_args.verbose, 0)
        self.assertEqual(parsed_args.replicon, 'replicon')

    def test_parse_2_results(self):
        parsed_args = split.parse_args(['outdir', 'outfile' 'result_1', 'result_2'])
        self.assertEqual(parsed_args.outdir, None)
        self.assertEqual(parsed_args.outfile, 'foo')
        self.assertTupleEqual(parsed_args.outfile.results, ('result_1', 'result_2'))
        self.assertEqual(parsed_args.quiet, 0)
        self.assertEqual(parsed_args.verbose, 0)
        self.assertEqual(parsed_args.replicon, 'replicon')


    def test_verbose(self):
        parsed_args = split.parse_args(['outdir', 'outfile' 'result_1', 'result'])
        self.assertEqual(parsed_args.verbose, 0)
        parsed_args = split.parse_args(['--verbose', 'outdir', 'outfile' 'result'])
        self.assertEqual(parsed_args.verbose, 1)
        parsed_args = split.parse_args(['-vv', 'outdir', 'outfile' 'result'])
        self.assertEqual(parsed_args.verbose, 2)

    def test_quiet(self):
        parsed_args = split.parse_args(['outdir', 'outfile' 'result'])
        self.assertEqual(parsed_args.quiet, 0)
        parsed_args = split.parse_args(['--quiet', 'outdir', 'outfile' 'result'])
        self.assertEqual(parsed_args.quiet, 1)
        parsed_args = split.parse_args(['-qq', 'outdir', 'outfile' 'result'])
        self.assertEqual(parsed_args.quiet, 2)


class TestMain(IntegronTest):

    def setUp(self):
        tmp_dir = tempfile.gettempdir()
        self.out_dir = os.path.join(tmp_dir, 'test_integron_split')
        if os.path.exists(self.out_dir) and os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir)
        os.makedirs(self.out_dir)

    def tearDown(self):
        if os.path.exists(self.out_dir) and os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir)


    def test_wo_chunk(self):
        replicon_path = self.find_data(os.path.join('Replicons', 'multi_fasta.fst'))
        command = 'integron_split --outdir {} {}'.format(self.out_dir, replicon_path)
        with self.catch_io(out=True, err=True):
            split.main(command.split()[1:])
            out = sys.stdout.getvalue()
        chunk_names = out.split()
        seq_index = SeqIO.index(replicon_path, "fasta", alphabet=Seq.IUPAC.unambiguous_dna)
        files_expected = [os.path.join(self.out_dir, r + '.fst') for r in seq_index]
        self.assertListEqual(files_expected, chunk_names)
        for f in chunk_names:
            seq_it = SeqIO.parse(f, 'fasta')
            for s in seq_it:
                ref_seq = seq_index[s.id]
                self.assertEqual(s.id, ref_seq.id)
                self.assertEqual(s.description, ref_seq.description)
                self.assertEqual(s.seq, ref_seq.seq)


    def test_w_chunk(self):
        replicon_path = self.find_data(os.path.join('Replicons', 'multi_fasta.fst'))
        chunk = 2
        command = 'integron_split --outdir {} --chunk {} {}'.format(self.out_dir, chunk, replicon_path)
        with self.catch_io(out=True, err=True):
            split.main(command.split()[1:])
            out = sys.stdout.getvalue()
        chunk_names = out.split()
        seq_index = SeqIO.index(replicon_path, "fasta", alphabet=Seq.IUPAC.unambiguous_dna)
        files_expected = [os.path.join(self.out_dir, "multi_fasta_chunk_{}.fst".format(i)) for i in range(1, chunk + 1)]
        self.assertListEqual(files_expected, chunk_names)
        for f in chunk_names:
            seq_it = SeqIO.parse(f, 'fasta')
            for s in seq_it:
                ref_seq = seq_index[s.id]
                self.assertEqual(s.id, ref_seq.id)
                self.assertEqual(s.description, ref_seq.description)
                self.assertEqual(s.seq, ref_seq.seq)