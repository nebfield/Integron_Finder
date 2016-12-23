#!/usr/bin/env python
# coding: utf-8


"""
Unit tests read_infernal function of integron_finder
"""

import integron_finder
import pandas as pd
import os
import unittest
import pandas.util.testing as pdt


class TestFunctions(unittest.TestCase):

    def setUp(self):
        """
        Define variables common to all tests
        """
        self.rep_name = "acba.007.p01.13"
        integron_finder.replicon_name = self.rep_name  # name of replicon in given fasta file
        integron_finder.length_cm = 47  # length in 'CLEN' (value for model attc_4.cm)


    def test_nofile(self):
        """
        Test that the function returns an empty dataframe if the given infernal file does not
        exist.

        """
        filename = "infernal.txt"
        df = integron_finder.read_infernal(filename)
        expect = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut",
                                       "cm_fin", "pos_beg", "pos_end", "sens", "evalue"])
        pdt.assert_frame_equal(df, expect)

    def test_nohit(self):
        """
        Test that if the infernal file exists but there is no hit
        inside, it returns an empty dataframe.
        """
        filename = os.path.join("tests", "data", "Results_Integron_Finder_" + self.rep_name,
                                 "other", self.rep_name + "_attc_table-empty.res")
        df = integron_finder.read_infernal(filename)
        expect = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut",
                                       "cm_fin", "pos_beg", "pos_end", "sens", "evalue"])
        pdt.assert_frame_equal(df, expect)

    def test_evalue_thres(self):
        """
        Test that if the infernal file exists and there are hits, but
        the given evalue threshold is smaller than the hits thresholds:
        no hit kept, should return an empty dataframe.
        """
        filename = os.path.join("tests", "data", "Results_Integron_Finder_" + self.rep_name,
                                 "other", self.rep_name + "_attc_table.res")
        df = integron_finder.read_infernal(filename, evalue=1e-10)
        expect = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut",
                                       "cm_fin", "pos_beg", "pos_end", "sens", "evalue"])
        pdt.assert_frame_equal(df, expect)

    def test_generate_df(self):
        """
        Test that if the infernal file exists and there are hits, it returns the
        dataframe corresponding to it.
        """
        filename = os.path.join("tests", "data", "Results_Integron_Finder_" + self.rep_name,
                                 "other", self.rep_name + "_attc_table.res")
        df = integron_finder.read_infernal(filename)
        expect = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut",
                                       "cm_fin", "pos_beg", "pos_end", "sens", "evalue"])
        expect = expect.append({"Accession_number": self.rep_name, "cm_attC": "attC_4",
                                    "cm_debut": 1, "cm_fin": 47, "pos_beg": 17825,
                                    "pos_end": 17884, "sens": "-", "evalue": 1e-9},
                                    ignore_index=True)
        expect = expect.append({"Accession_number": self.rep_name, "cm_attC": "attC_4",
                                    "cm_debut": 1, "cm_fin": 47, "pos_beg": 19080,
                                    "pos_end": 19149, "sens": "-", "evalue": 1e-4},
                                    ignore_index=True)
        expect = expect.append({"Accession_number": self.rep_name, "cm_attC": "attC_4",
                                    "cm_debut": 1, "cm_fin": 47, "pos_beg": 19618,
                                    "pos_end": 19726, "sens": "-", "evalue": 1.1e-7},
                                    ignore_index=True)
        # convert positions to int
        intcols = ["cm_debut", "cm_fin", "pos_beg", "pos_end"]
        expect[intcols] = expect[intcols].astype(int)
        pdt.assert_frame_equal(df, expect)
