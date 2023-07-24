import subprocess
import json

def get_children(parent):
    # print(f"DEBUG : Call to get_children({parent})")
    command = f"eos root://cmseos.fnal.gov ls -F {parent}"
    # print(command)
    result = subprocess.getoutput(command)  # , stdout=subprocess.PIPE)
    # print(result)
    return result.split("\n")


def get_subfolders(parent):
    subfolders = []
    for x in get_children(parent):
        if len(x) == 0:
            continue
        if x[-1] == "/":
            subfolders.append(x)
    return subfolders


folders_to_index = [
    
    #ZH, WH, VBF, ttH, ggZH
    #Include both ZH and ggZH for completeness.
    #HToBB has everything except for gluon fusion so need to add GluGluHTOBB.
    "/store/user/lpcpfnano/cmantill/v2_3/2016/HToBB/",
    "/store/user/lpcpfnano/cmantill/v2_3/2016APV/HToBB/",
    "/store/user/lpcpfnano/cmantill/v2_3/2017/HToBB/",
    "/store/user/lpcpfnano/cmantill/v2_3/2018/HToBB/",
    
    "/store/user/lpcpfnano/rkansal/v2_3/2016/GluGluHToBB/",
    "/store/user/lpcpfnano/rkansal/v2_3/2016APV/GluGluHToBB/",
    "/store/user/lpcpfnano/rkansal/v2_3/2017/GluGluHToBB/",
    "/store/user/lpcpfnano/rkansal/v2_3/2018/GluGluHToBB/",
    
    #Inclusive QCD
    "/store/user/lpcpfnano/cmantill/v2_3/2016/QCD",
    "/store/user/lpcpfnano/cmantill/v2_3/2016APV/QCD",
    "/store/user/lpcpfnano/cmantill/v2_3/2017/QCD",
    "/store/user/lpcpfnano/cmantill/v2_3/2018/QCD",
    
    #bEnriched QCD
    "/store/user/lpcpfnano/duhoang/v2_3/2016/QCD_bEnriched/",
    "/store/user/lpcpfnano/duhoang/v2_3/2016APV/QCD_bEnriched/",
    "/store/user/lpcpfnano/duhoang/v2_3/2017/QCD_bEnriched/",
    "/store/user/lpcpfnano/duhoang/v2_3/2018/QCD_bEnriched/",
    
    #BGenFilter QCD
    "/store/user/lpcpfnano/duhoang/v2_3/2016/QCD_BGenFilter/",
    "/store/user/lpcpfnano/duhoang/v2_3/2016APV/QCD_BGenFilter/",
    "/store/user/lpcpfnano/duhoang/v2_3/2017/QCD_BGenFilter/",
    "/store/user/lpcpfnano/duhoang/v2_3/2018/QCD_BGenFilter/",
    
    #ttbar
    "/store/user/lpcpfnano/cmantill/v2_3/2016/TTbar",
    "/store/user/lpcpfnano/cmantill/v2_3/2016APV/TTbar",
    "/store/user/lpcpfnano/rkansal/v2_3/2017/TTbar",
    "/store/user/lpcpfnano/cmantill/v2_3/2018/TTbar",
    #
    "/store/group/lpcpfnano/jdickins/v2_3/2016/TTbarBoosted/",
    "/store/group/lpcpfnano/jdickins/v2_3/2016APV/TTbarBoosted/",
    "/store/group/lpcpfnano/jdickins/v2_3/2017/TTbarBoosted/",
    "/store/group/lpcpfnano/jdickins/v2_3/2018/TTbarBoosted/",
    
    #VV
    "/store/user/lpcpfnano/rkansal/v2_3/2016/Diboson/",
    "/store/user/lpcpfnano/rkansal/v2_3/2016APV/Diboson/",
    "/store/user/lpcpfnano/rkansal/v2_3/2017/Diboson/",
    "/store/user/lpcpfnano/rkansal/v2_3/2018/Diboson/",
    
    #Wjets
    "/store/user/lpcpfnano/cmantill/v2_3/2016/WJetsToQQ",
    "/store/user/lpcpfnano/cmantill/v2_3/2016APV/WJetsToQQ",
    "/store/user/lpcpfnano/cmantill/v2_3/2017/WJetsToQQ",
    "/store/user/lpcpfnano/rkansal/v2_3/2017/WJetsToQQ",  # missing HT200-400
    "/store/user/lpcpfnano/cmantill/v2_3/2018/WJetsToQQ",
    
    "/store/group/lpcpfnano/jdickins/v2_3/2017/WJetsToQQ", #Include HT200-400
    
    #Zjets
    "/store/user/lpcpfnano/cmantill/v2_3/2016/ZJetsToQQ",
    "/store/user/lpcpfnano/cmantill/v2_3/2016APV/ZJetsToQQ",
    "/store/user/lpcpfnano/cmantill/v2_3/2017/ZJetsToQQ",
    "/store/user/lpcpfnano/rkansal/v2_3/2017/ZJetsToQQ",  # missing HT200-400
    "/store/user/lpcpfnano/cmantill/v2_3/2018/ZJetsToQQ",
    
    "/eos/uscms/store/group/lpcpfnano/jdickins/v2_3/2017/ZJetsToQQ", #Include HT200-400
    
    #TODO: DYJets
    
    # For muon control region. 
    # "/store/user/lpcpfnano/rkansal/v2_3/2016/SingleMu2016",
    # "/store/user/lpcpfnano/rkansal/v2_3/2017/SingleMu2017",
    "/store/user/lpcpfnano/rkansal/v2_3/2018/SingleMu2018",
    
    #Data
    "/store/user/lpcpfnano/cmantill/v2_3/2016/JetHT2016", #Split into 2016 and 2016APV in filesets.ipynb,
    "/store/user/lpcpfnano/cmantill/v2_3/2017/JetHT2017",
    "/store/user/lpcpfnano/cmantill/v2_3/2018/JetHT2018",
    
    #Singlet
    "/store/user/lpcpfnano/cmantill/v2_3/2016/SingleTop",
    "/store/user/lpcpfnano/cmantill/v2_3/2016APV/SingleTop",
    "/store/user/lpcpfnano/rkansal/v2_3/2017/SingleTop",
    "/store/user/lpcpfnano/cmantill/v2_3/2017/SingleTop",
    "/store/user/lpcpfnano/cmantill/v2_3/2018/SingleTop",
    
    #TODO: Why do we need this? 
    "/store/user/lpcpfnano/drankin/v2_2/2016/WJetsToLNu",
    "/store/user/lpcpfnano/drankin/v2_2/2016APV/WJetsToLNu",
    "/store/user/lpcpfnano/drankin/v2_2/2017/WJetsToLNu",
    "/store/user/lpcpfnano/drankin/v2_2/2018/WJetsToLNu",
]

index_APV = {}

# Data path:
# .......................f1........................|...f2.....|..........f3.......|.....f4......|.f5.|....
# /store/user/lpcpfnano/dryu/v2_2/2017/SingleMu2017/SingleMuon/SingleMuon_Run2017C/211102_162942/0000/*root
#
# MC path:
# .......................f1.........................|.......................f2..............................|..........f3.........|.....f4......|.f5.|....
# /store/user/lpcpfnano/cmantill/v2_3/2017/WJetsToQQ/WJetsToQQ_HT-800toInf_TuneCP5_13TeV-madgraphMLM-pythia8/WJetsToQQ_HT-800toInf/211108_171840/0000/*root

ignore_files = [
    "/store/user/lpcpfnano/cmantill/v2_3/2018/SingleTop/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/ST_t-channel_top_4f_InclusiveDecays/220808_150919/0000/nano_mc2018_17.root"
]

ignore_subsamples = ["SingleMuon_Run2016B_ver1_HIPM"]

for pyear in ["2016", "2016APV", "2017", "2018"]:
    if pyear != "2018":
        continue
    print(pyear)
    index = {}
    for f1 in folders_to_index:
        f1 = f1.rstrip("/")
        year = f1.split("/")[-2]
        sample_short = f1.split("/")[-1]
        if year == "2017v1":
            year = "2017"
        if year != pyear:
            continue

        print(f1)

        sample_short = f1.split("/")[-1]
        print(f" {sample_short}")

        if not year in index:
            index[year] = {}
        if not sample_short in index[year]:
            index[year][sample_short] = {}

        f1_subfolders = get_subfolders(f"{f1}")
        for f2 in f1_subfolders:
            print(f"\t/{f2}")
            subsample_long = f2.replace("/", "")  # This should be the actual dataset name
            f2_subfolders = get_subfolders(f"{f1}/{f2}")
            if len(f2_subfolders) == 0:
                root_files = [
                    f"{f1}/{f2}/{x}".replace("//", "/")
                    for x in get_children((f"{f1}/{f2}"))
                    if x[-5:] == ".root"
                ]
                if not subsample_long in index[year][sample_short]:
                    index[year][sample_short][subsample_long] = []
                index[year][sample_short][subsample_long].extend(root_files)

            for f3 in f2_subfolders:
                print(f"\t\t/{f3}")
                subsample_short = f3.replace("/", "")
                if "ext1" in subsample_short:
                    print("   Ext1")

                if subsample_short in ignore_subsamples:
                    print(f"Ignoring {subsample_short}")
                    continue

                # if year == "2016" and subsample_short.endswith("HIPM"):
                #     continue

                # skip non-PSWeights files, and rename PSWeights ones
                if year == "2018" and subsample_short.startswith("QCD"):
                    if not subsample_short.endswith("_PSWeights_madgraph"):
                        continue
                    else:
                        subsample_short = subsample_short.replace("_PSWeights_madgraph", "")

                subsample_short = subsample_short.replace("_ext1", "")
                print(f"  {subsample_short}")

                if not subsample_short in index[year][sample_short]:
                    index[year][sample_short][subsample_short] = []
                f3_subfolders = get_subfolders(f"{f1}/{f2}/{f3}")

                if len(f3_subfolders) >= 2:
                    print(f"WARNING : Found multiple timestamps for {f1}/{f2}/{f3}")
                    print(f3_subfolders)

                for f4 in f3_subfolders:  # Timestamp
                    if len(f3_subfolders) >= 2:
                        if f4 == "220801_140806/":  # ignoring repeat of 2016H
                            print(f"Ignoring {f4}")
                            continue

                    f4_subfolders = get_subfolders(f"{f1}/{f2}/{f3}/{f4}")

                    for f5 in f4_subfolders:  # 0000, 0001, ...
                        f5_children = get_children((f"{f1}/{f2}/{f3}/{f4}/{f5}"))
                        root_files = [
                            f"{f1}/{f2}/{f3}/{f4}/{f5}/{x}".replace("//", "/")
                            for x in f5_children
                            if x[-5:] == ".root"
                            and f"{f1}/{f2}/{f3}/{f4}/{f5}/{x}".replace("//", "/")
                            not in ignore_files
                        ]

                        if len(root_files) == 0:
                            for f6 in f5_children:
                                f6_children = get_children((f"{f1}/{f2}/{f3}/{f4}/{f5}/{f6}"))
                                root_files.extend(
                                    [
                                        f"{f1}/{f2}/{f3}/{f4}/{f5}/{f6}/{x}".replace("//", "/")
                                        for x in f6_children
                                        if x[-5:] == ".root"
                                    ]
                                )

                        if year == "2016" and "preUL" in subsample_short:
                            # duplicate preUL 2016 samples into the 2016APV lists
                            if not sample_short in index_APV:
                                index_APV[sample_short] = {}
                            if not subsample_short in index_APV[sample_short]:
                                index_APV[sample_short][subsample_short] = []
                                index_APV[sample_short][subsample_short].extend(root_files)

                        if year == "2016" and "HIPM" in subsample_short:
                            if not sample_short in index_APV:
                                index_APV[sample_short] = {}
                            if not subsample_short in index_APV[sample_short]:
                                index_APV[sample_short][subsample_short] = []
                                index_APV[sample_short][subsample_short].extend(root_files)
                        else:
                            if not subsample_short in index[year][sample_short]:
                                index[year][sample_short][subsample_short] = []
                            index[year][sample_short][subsample_short].extend(root_files)

    if pyear == "2016APV":
        for sample_short in index_APV.keys():
            for subsample_short in index_APV[sample_short].keys():
                if not sample_short in index[pyear]:
                    index[pyear][sample_short] = {}
                if not subsample_short in index[pyear][sample_short]:
                    index[pyear][sample_short][subsample_short] = []
                index[pyear][sample_short][subsample_short] = index_APV[sample_short][
                    subsample_short
                ]

    with open(f"pfnanoindex_{pyear}.json", "w") as f:
        json.dump(index, f, sort_keys=True, indent=2)
