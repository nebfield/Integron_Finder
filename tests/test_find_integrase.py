import os
import tempfile
import shutil
import argparse
import re
import distutils.spawn


try:
    from tests import IntegronTest
except ImportError as err:
    msg = "Cannot import integron_finder: {0!s}".format(err)
    raise ImportError(msg)

from integron_finder.utils import read_single_dna_fasta
from integron_finder.config import Config
from integron_finder import integrase

_call_ori = integrase.call


def call_wrapper():
    """
    hmmsearch or prodigal write lot of things on stderr or stdout 
    which noise the unit test output
    So I replace the `call` function in module integron_finder
    by a wrapper which call the original function but add redirect stderr and stdout
    in dev_null
    :return: wrapper around integron_finder.call
    :rtype: function
    """
    def wrapper(*args, **kwargs):
        with open(os.devnull, 'w') as f:
            kwargs['stderr'] = f
            kwargs['stdout'] = f
            res = _call_ori(*args, **kwargs)
        return res
    return wrapper


class TestFindIntegrase(IntegronTest):

    def setUp(self):
        if 'INTEGRON_HOME' in os.environ:
            self.integron_home = os.environ['INTEGRON_HOME']
            self.local_install = True
        else:
            self.local_install = False
            self.integron_home = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

        self.tmp_dir = os.path.join(tempfile.gettempdir(), 'tmp_test_integron_finder')
        os.makedirs(self.tmp_dir)

        self.args = argparse.Namespace()
        self.args.attc_model = 'attc_4.cm'
        self.args.cpu = 1
        self.args.hmmsearch = distutils.spawn.find_executable('hmmsearch')
        self.args.prodigal = distutils.spawn.find_executable("prodigal")
        integrase.call = call_wrapper()

    def tearDown(self):
        integrase.call = _call_ori
        try:
            shutil.rmtree(self.tmp_dir)
            pass
        except:
            pass


    def test_find_integrase_gembase(self):
        cfg = Config(self.args)
        self.args.gembase = True
        cfg._prefix_data = os.path.join(os.path.dirname(__file__), 'data')

        replicon_name = 'acba.007.p01.13'
        replicon_path = self.find_data(os.path.join('Replicons', replicon_name + '.fst'))
        replicon = read_single_dna_fasta(replicon_path)
        prot_file = os.path.join(self.tmp_dir, replicon_name + ".prt")

        shutil.copyfile(self.find_data(os.path.join('Proteins', replicon_name + ".prt")), prot_file)

        integrase.find_integrase(replicon_path, replicon, prot_file, self.tmp_dir, cfg)

        for suffix in ('_intI.res', '_intI_table.res', '_phage_int.res', '_phage_int_table.res'):
            res = os.path.join(self.tmp_dir, replicon_name + suffix)
            self.assertTrue(os.path.exists(res))


    def test_find_integrase_no_gembase_with_protfile(self):
        cfg = Config(self.args)
        self.args.gembase = False
        cfg._prefix_data = os.path.join(os.path.dirname(__file__), 'data')

        replicon_name = 'acba.007.p01.13'
        replicon_path = self.find_data(os.path.join('Replicons', replicon_name + '.fst'))
        replicon = read_single_dna_fasta(replicon_path)

        len_ori = replicon.__class__.__len__
        replicon.__class__.__len__ = lambda x: 200

        prot_file = os.path.join(self.tmp_dir, replicon_name + ".prt")
        shutil.copyfile(self.find_data(os.path.join('Proteins', replicon_name + ".prt")), prot_file)

        integrase.find_integrase(replicon_path, replicon, prot_file, self.tmp_dir, cfg)
        for suffix in ('_intI.res', '_intI_table.res', '_phage_int.res', '_phage_int_table.res'):
            res = os.path.join(self.tmp_dir, replicon_name + suffix)
            self.assertTrue(os.path.exists(res))
        replicon.__class__.__len__ = len_ori


    def test_find_integrase_no_gembase_no_protfile_short_seq(self):
        cfg = Config(self.args)
        self.args.gembase = False
        cfg._prefix_data = os.path.join(os.path.dirname(__file__), 'data')

        replicon_name = 'acba.007.p01.13'
        replicon_path = self.find_data(os.path.join('Replicons', replicon_name + '.fst'))
        replicon = read_single_dna_fasta(replicon_path)

        len_ori = replicon.__class__.__len__
        replicon.__class__.__len__ = lambda x: 200

        prot_file = os.path.join(self.tmp_dir, replicon_name + ".prt")

        integrase.find_integrase(replicon_path, replicon, prot_file, self.tmp_dir, cfg)
        for suffix in ('_intI.res', '_intI_table.res', '_phage_int.res', '_phage_int_table.res'):
            res = os.path.join(self.tmp_dir, replicon_name + suffix)
            self.assertTrue(os.path.exists(res))
        replicon.__class__.__len__ = len_ori


    def test_find_integrase_no_gembase_no_protfile_long_seq(self):
        cfg = Config(self.args)
        self.args.gembase = False
        cfg._prefix_data = os.path.join(os.path.dirname(__file__), 'data')

        replicon_name = 'acba.007.p01.13'
        replicon_path = self.find_data(os.path.join('Replicons', replicon_name + '.fst'))
        replicon = read_single_dna_fasta(replicon_path)

        len_ori = replicon.__class__.__len__
        replicon.__class__.__len__ = lambda x: 500000

        prot_file = os.path.join(self.tmp_dir, replicon_name + ".prt")

        shutil.copyfile(self.find_data(os.path.join('Proteins', replicon_name + ".prt")), prot_file)

        integrase.find_integrase(replicon_path, replicon, prot_file, self.tmp_dir, cfg)
        for suffix in ('_intI.res', '_intI_table.res', '_phage_int.res', '_phage_int_table.res'):
            res = os.path.join(self.tmp_dir, replicon_name + suffix)
            self.assertTrue(os.path.exists(res))
        replicon.__class__.__len__ = len_ori


    def test_find_integrase_no_gembase_no_protfile_no_prodigal(self):
        self.args.hmmsearch = 'foo'
        self.args.gembase = False
        cfg = Config(self.args)
        cfg._prefix_data = os.path.join(os.path.dirname(__file__), 'data')

        replicon_name = 'acba.007.p01.13'
        replicon_path = self.find_data(os.path.join('Replicons', replicon_name + '.fst'))
        replicon = read_single_dna_fasta(replicon_path)

        len_ori = replicon.__class__.__len__
        replicon.__class__.__len__ = lambda x: 500000

        prot_file = os.path.join(self.tmp_dir, replicon_name + ".prt")

        shutil.copyfile(self.find_data(os.path.join('Proteins', replicon_name + ".prt")), prot_file)

        with self.assertRaises(RuntimeError) as ctx:
            integrase.find_integrase(replicon_path, replicon, prot_file, self.tmp_dir, cfg)
        self.assertTrue(str(ctx.exception).endswith('failed : [Errno 2] No such file or directory'))

        replicon.__class__.__len__ = len_ori


    def test_find_integrase_no_gembase_no_protfile(self):
        cfg = Config(self.args)
        self.args.gembase = False
        cfg._prefix_data = os.path.join(os.path.dirname(__file__), 'data')

        replicon_name = 'acba.007.p01.13'
        replicon_path = self.find_data(os.path.join('Replicons', replicon_name + '.fst'))
        replicon = read_single_dna_fasta(replicon_path)

        len_ori = replicon.__class__.__len__
        replicon.__class__.__len__ = lambda x: 500000
        prot_file = os.path.join(self.tmp_dir, replicon_name + ".prt")

        with self.assertRaises(RuntimeError) as ctx:
            integrase.find_integrase('foo', replicon,  prot_file, self.tmp_dir, cfg)
        self.assertTrue(str(ctx.exception).endswith('failed returncode = 5'.format(cfg.prodigal)))

        replicon.__class__.__len__ = len_ori


    def test_find_integrase_gembase_no_hmmer_no_replicon(self):
        self.args.gembase = True
        self.args.hmmsearch = 'foo'
        cfg = Config(self.args)
        cfg._prefix_data = os.path.join(os.path.dirname(__file__), 'data')

        replicon_name = 'acba.007.p01.13'
        replicon_path = os.path.join(self._data_dir, 'Replicons', replicon_name + '.fst')
        replicon = read_single_dna_fasta(replicon_path)

        prot_file = os.path.join(self.tmp_dir, replicon_name + ".prt")

        with self.assertRaises(RuntimeError) as ctx:
            integrase.find_integrase(replicon_path, replicon, prot_file, self.tmp_dir, cfg)
        self.assertTrue(re.match('^foo .* failed : \[Errno 2\] No such file or directory$',
                                 str(ctx.exception)))


    def test_find_integrase_gembase_hmmer_error(self):
        self.args.gembase = True
        self.args.cpu = 'foo'
        cfg = Config(self.args)
        cfg._prefix_data = os.path.join(os.path.dirname(__file__), 'data')

        replicon_name = 'acba.007.p01.13'
        replicon_path = os.path.join(self._data_dir, 'Replicons', replicon_name + '.fst')
        replicon = read_single_dna_fasta(replicon_path)

        prot_file = os.path.join(self.tmp_dir, replicon_name + ".prt")
        shutil.copyfile(os.path.join(self._data_dir, 'Proteins', replicon_name + ".prt"),
                        prot_file)
        with self.assertRaises(RuntimeError) as ctx:
            integrase.find_integrase(replicon_path, replicon, prot_file, self.tmp_dir, cfg)
        self.assertTrue(str(ctx.exception).endswith('failed return code = 1'))
