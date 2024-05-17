'''
Mainscript to run the ftests.

Usage: python submit.py -y year -p <pt order> -r <rho order> -n <number of jobs>

How does the F-tests work? 

1. 
'''
#!/usr/bin/python
import os, sys
import subprocess
import argparse

# Main method                                                                          
def main():

    parser = argparse.ArgumentParser(description='F-test batch submit')
    parser.add_argument('-y', '--year', type=str, help='Year as a string')
    parser.add_argument('-p', '--pt', type=int, help='pt of baseline as an integer')
    parser.add_argument('-r','--rho', type=int, help='rho of baseline')
    parser.add_argument('-n','--njobs', type=int, help='number of 100 toy jobs to submit', default=10)
    args = parser.parse_args()

    pt = args.pt
    rho = args.rho
    njobs = args.njobs
    year = args.year

    print(f"Year: {year}, pT: {pt}, rho: {rho}, njobs: {njobs}.")

    #Make logs directory
    tag=f"pt{pt}rho{rho}"

    #Condor working directory
    workdir = f'/eos/uscms/store/user/dhoang/vh_ftests/MCTF/{year}/'
    os.system(f'mkdir -p {workdir}')
    print("CONDOR work dir: ", workdir)

    outdir = workdir + tag 

    for i in range(0, njobs):
        prefix = f"{tag}_{i}"
        print('Submitting:', prefix)

        #Fill in the condor template
        condor_templ_file = open("templates/submit.templ.condor")

        files_transfer = f"compare.py, pt{pt}rho{rho}, pt{pt+1}rho{rho}, pt{pt}rho{rho+1}" #Files to transfer
        submit_args = f"{pt} {rho} {outdir} {i}"
    
        local_condor = f"{year}/{prefix}.condor"
        condor_file = open(local_condor,"w")
        for line in condor_templ_file:
            line=line.replace('TRANSFERFILES',files_transfer)
            line=line.replace('PREFIX',prefix)
            line=line.replace('SUBMITARGS',submit_args)
            condor_file.write(line)
        condor_file.close()
    
        if (os.path.exists('%s.log'  % local_condor)): os.system('rm %s.log' % local_condor) #Clean log

        #Go to the directory and submit the jobs
        og_dir = os.getcwd()
        os.chdir(year)
        os.system('condor_submit %s' % f"{prefix}.condor") #submit jobs
        os.chdir(og_dir)

        condor_templ_file.close()
    
    return 

if __name__ == "__main__":
    main()