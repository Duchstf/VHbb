import numpy as np
import sys

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
bb_bins = [0.0, 0.97, 0.9918] + [round(x,4) for x in list(np.linspace(0.98,1.,20))] + ParticleNet_WorkingPoints['{}_bb'.format(sys.argv[1])][1:]
bb_bins.sort()
print('bb bins: ', bb_bins)
print(any(bb_bins.count(x) > 1 for x in bb_bins))

#Scan thresholds for cc
cc_bins = [round(x,4) for x in list(np.linspace(0.,1.,50))]  + ParticleNet_WorkingPoints['{}_cc'.format(sys.argv[1])][1:]
cc_bins.sort()
print('cc bins: ', cc_bins)
print(any(cc_bins.count(x) > 1 for x in cc_bins))
