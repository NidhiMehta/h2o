import unittest
import random, sys, time, os
sys.path.extend(['.','..','py'])

import h2o, h2o_cmd, h2o_hosts, h2o_browse as h2b, h2o_import as h2i, h2o_kmeans

class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        global SEED, localhost
        SEED = h2o.setup_random_seed()
        localhost = h2o.decide_if_localhost()
        if (localhost):
            h2o.build_cloud(3,java_heap_GB=4)
        else:
            h2o_hosts.build_cloud_with_hosts() # uses import Hdfs for s3n instead of import folder

    @classmethod
    def tearDownClass(cls):
        # wait while I inspect things
        # time.sleep(1500)
        h2o.tear_down_cloud()

    def test_parse_bounds_libsvm(self):
        # just do the import folder once
        importFolderPath = "/home/0xdiag/datasets/libsvm"

        # make the timeout variable per dataset. it can be 10 secs for covtype 20x (col key creation)
        # so probably 10x that for covtype200
        csvFilenameList = [
            ("mnist_train.svm", "cM", 30, 1),
            # FIX! fails KMeansScore
            # not integer output
            # ("colon-cancer.svm",   "cA", 30, 1),
            ("connect4.svm",       "cB", 30, 1),
            ("syn_6_1000_10.svm",  "cK", 30, 1),
            ("syn_0_100_1000.svm", "cL", 30, 1),
            ("mushrooms.svm",      "cG", 30, 1),
            ("duke.svm",           "cD", 30, 1),
            # too many features? 150K inspect timeout?
            # ("E2006.train.svm",    "cE", 30, 1),
            ("gisette_scale.svm",  "cF", 30, 1),
            ("news20.svm",         "cH", 30, 1),

            ("tmc2007_train.svm",  "cJ", 30, 1),
            ("covtype.binary.svm", "cC", 30, 1),
            # normal csv
        ]

        ### csvFilenameList = random.sample(csvFilenameAll,1)
        # h2b.browseTheCloud()
        lenNodes = len(h2o.nodes)

        firstDone = False
        for (csvFilename, key2, timeoutSecs, resultMult) in csvFilenameList:
            # have to import each time, because h2o deletes source after parse
            h2i.setupImportFolder(None, importFolderPath)
            csvPathname = importFolderPath + "/" + csvFilename

            # PARSE******************************************
            # creates csvFilename.hex from file in importFolder dir 
            parseKey = h2i.parseImportFolderFile(None, csvFilename, importFolderPath, 
                key2=key2, timeoutSecs=2000)
            print csvPathname, 'parse time:', parseKey['response']['time']
            print "Parse result['destination_key']:", parseKey['destination_key']

            # INSPECT******************************************
            start = time.time()
            inspect = h2o_cmd.runInspect(None, parseKey['destination_key'], timeoutSecs=360)
            print "Inspect:", parseKey['destination_key'], "took", time.time() - start, "seconds"
            h2o_cmd.infoFromInspect(inspect, csvFilename)

            # RF******************************************
            kwargs = {
                'ntree': 6,
                'response_variable': 0,
            }

            timeoutSecs = 600
            start = time.time()
            rf = h2o_cmd.runRFOnly(parseKey=parseKey, timeoutSecs=timeoutSecs, **kwargs)
            elapsed = time.time() - start
            print "rf end on ", csvPathname, 'took', elapsed, 'seconds.', \
                "%d pct. of timeout" % ((elapsed/timeoutSecs) * 100)



if __name__ == '__main__':
    h2o.unit_main()
