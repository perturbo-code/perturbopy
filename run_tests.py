from perturbopy import tests_use
import sys

result = tests_use.do_tests(["-s", "--source_folder", './tests_supplementary', '--run_qe2pert'])
sys.exit(result)