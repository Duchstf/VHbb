#!/usr/bin/python
import os, sys
import subprocess
import numpy as np

'''
Used to run the combine scan setup, like this:

python submit.py

NO NEED TO ENABLE SINGULARITY
'''

ParticleNet_WorkingPoints = {
       '2016APV_bb':    [0.0, 0.9088, 0.9737, 0.9883],
       '2016APV_cc':    [0.0, 0.9252, 0.9751, 0.9909],
       
       '2016_bb': [0.0, 0.9137, 0.9735, 0.9883],
       '2016_cc': [0.0, 0.9252, 0.9743, 0.9905],
       
       '2017_bb':    [0.0, 0.9105, 0.9714, 0.9870],
       '2017_cc':    [0.0, 0.9347, 0.9765, 0.9909],
       
       '2018_bb':    [0.0, 0.9172, 0.9734, 0.9880],
       '2018_cc':    [0.0, 0.9368, 0.9777, 0.9917]
}

#Scan thresholds for bb
bb_bins = [0.0, 0.97] + [round(x,4) for x in list(np.linspace(0.98,1.,50))] + ParticleNet_WorkingPoints['{}_bb'.format('2017')][1:]
bb_bins.sort()


#Scan thresholds for cc
cc_bins = [round(x,4) for x in list(np.linspace(0.,1.,50))]  + ParticleNet_WorkingPoints['{}_cc'.format('2017')][1:]
cc_bins.sort()
              
bb_thresholds = bb_bins[1:]
cc_thresholds = cc_bins[1:]

print(bb_thresholds)
print(cc_thresholds)

class Found(Exception): pass #for breaking nested loops

log_dir = "logs"
os.system('rm -rf {}/'.format(log_dir)) #Remove if it's there

#Create the logs directory
os.system("mkdir -p {}".format(log_dir))

#Make the tarball
os.system("rm tar_ball.tar.gz")
os.system("tar -czvf tar_ball.tar.gz tar_ball")
os.system("cp tar_ball.tar.gz {}/".format(log_dir))

# Copy the CMSSW Environment over
os.system("cp CMSSW_10_2_13.tar.gz {}/".format(log_dir))
current_path =  os.environ['PWD']

n_chunk = 10 #Process 10 points at a time
chunk_index = 0 #Chunk counter to keep index of the chunks
n_test = 2 #number of test loop

counter = 0
pair_string = ' '
#Loop over all the threshold combinations

try:
       for bb1 in bb_thresholds:
              for cc2 in cc_thresholds:

                     #Create the pairings
                     pair_string += '"{} {}" '.format(bb1, cc2)
                     counter += 1

                     if counter % n_chunk == 0:
                            
                            #Write the pre_scan
                            pre_scan_temp = open("{}/pre_scan_temp.sh".format(current_path)) #Template
                            pre_scan_local = "{}/{}/pre_scan_{}.sh".format(current_path, log_dir,chunk_index)

                            print("Creating pre scan files: ...")
                            pre_scan_file = open(pre_scan_local,"w")
                            for line in pre_scan_temp:
                                   line=line.replace('THRES_LIST', pair_string)
                                   pre_scan_file.write(line)
                            pre_scan_file.close()

                            #Write the main_scan
                            main_scan_temp = open("{}/main_scan_temp.sh".format(current_path)) #Template
                            main_scan_local = "{}/{}/main_scan_{}.sh".format(current_path, log_dir, chunk_index)

                            print("Creating main scan files: ...")
                            main_scan_file = open(main_scan_local, "w")
                            for line in main_scan_temp:
                                   line=line.replace('THRES_LIST', pair_string)
                                   main_scan_file.write(line)
                            main_scan_file.close()

                            #Produce excecutable:
                            print("Producing executable ...")
                            exec_temp =  open("{}/condor_temp.sh".format(current_path))
                            exec_local =  "{}/{}/condor_local_{}.sh".format(current_path, log_dir, chunk_index)

                            exec_local_file = open(exec_local, 'w')
                            for line in exec_temp:
                                   line=line.replace('PRE_SCAN_FILE', "pre_scan_{}.sh".format(chunk_index))
                                   line=line.replace('MAIN_SCAN_FILE', "main_scan_{}.sh".format(chunk_index))
                                   exec_local_file.write(line)
                            exec_local_file.close()


                            #Produce condor file
                            condor_temp = open("{}/condor_temp.sub".format(current_path))
                            condor_local = "{}/{}/condor_local_{}.sub".format(current_path, log_dir, chunk_index)

                            print("Creating condor files")
                            condor_local_file = open(condor_local, "w")
                            for line in condor_temp:
                                   line=line.replace('PREFIX', "condor_local_{}".format(chunk_index))
                                   line=line.replace('PRE_SCAN', "pre_scan_{}.sh".format(chunk_index))
                                   line=line.replace('MAIN_SCAN', "main_scan_{}.sh".format(chunk_index))
                                   line=line.replace('OUT_FILE', "out_file_{}.out".format(chunk_index))
                                   condor_local_file.write(line)
                            condor_local_file.close()

                            print("COUNTER: ", counter)
                            print("PAIRS: ", pair_string)
                            pair_string = ' '

                            chunk_index += 1

                            condor_temp.close()
                            exec_temp.close()
                            main_scan_temp.close()
                            pre_scan_temp.close()

                            os.system('condor_submit {}'.format(condor_local))

                     # if chunk_index == n_test:
                     #        raise Found

except Found:
       print("BREAKING")
       