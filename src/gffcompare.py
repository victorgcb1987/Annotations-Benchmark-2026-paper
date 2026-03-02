from subprocess import run

# this function runs gffcompare using protein or transcript evidence, 
# manages the output files and returns the result for each evidence
def run_gffcompare(outbase, source_annotation, target_annotation, name):
    # define the command template and create a dedicated 'gffcompare_results' directory
    outpath = outbase / name
    renamed_annotation = outpath / f"{name}.gff"
    cmd_run = f"ln -s {target_annotation} {renamed_annotation}"
    if not outpath.exists():
            outpath.mkdir(parents=True, exist_ok=True)
    
    run(cmd_run, shell=True, capture_output=True) 

    
    # construct output file names and a list of expected suffixes
    cmd = "gffcompare -r {} -o {} {}"
    outfile = outpath/"{}".format(name)
    cmd_run = cmd.format(source_annotation, outfile, renamed_annotation)
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
            # on failure, capture and log the specific error details
        else:
            log_msg = "Gffcompare error: {}".format(cmd_results.stderr.decode())
            results = {"outfile": outfile, "log_msg": log_msg, 
                       "returncode": cmd_results.returncode, "cmd": cmd_run}
    return results