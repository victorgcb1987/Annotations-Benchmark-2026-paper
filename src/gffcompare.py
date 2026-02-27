import os
import shutil

from src.docs import SOURCE_ANNOTS_FOR_GEMOMA
from subprocess import run

# this function runs gffcompare using protein or transcript evidence, 
# manages the output files and returns the result for each evidence
def run_gffcompare(outbase, source_annotations, benchmarks):
    for species, benchmark in benchmarks.items():

    # define the command template and create a dedicated 'gffcompare_results' directory
    cmd = "gffcompare -r {} -o {} {}"
    outpath = outbase / "gffcompare_results"
    if not outpath.exists():
            outpath.mkdir(parents=True, exist_ok=True)
    # processing evidence
    
        # construct output file names and a list of expected suffixes
    outfile = outpath/"{}".format(target_annotation.name)
    out_prefix = "{}.{}"
    suffixes = ["tmap", "refmap"]
    cmd_run = cmd.format(source_annotation, outfile, target_annotation)
    # if output already exists, skip execution
    if outfile.is_file():
        log_msg = "Gffcompare already done, skipping it"
        results = {"outfile": outfile, "log_msg": log_msg,
                   "returncode": 0, "cmd": cmd_run}
        # otherwise, run the command via a systeam shell
    else:
        cmd_results = run(cmd_run, shell=True, capture_output=True)
        # on success
        if cmd_results.returncode == 0:
            # log the completion
            log_msg = "Gffcompare successfully done"
            results = {"outfile": outfile, "log_msg": log_msg,
                      "returncode": cmd_results.returncode, "cmd": cmd_run}
                # file relocation
            for suffix in suffixes:
                ref_fpath = source_annotation.parent / out_prefix.format(target_annotation.name, suffix)
                new_fpath = outpath/ out_prefix.format(target_annotation.name, suffix)
                shutil.move(ref_fpath, new_fpath)
            # on failure, capture and log the specific error details
        else:
            log_msg = "Gffcompare error: {}".format(cmd_results.stderr.decode())
            results = {"outfile": outfile, "log_msg": log_msg, 
                       "returncode": cmd_results.returncode, "cmd": cmd_run}
    return results