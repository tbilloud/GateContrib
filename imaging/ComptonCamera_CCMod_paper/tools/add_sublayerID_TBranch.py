import uproot

# This script adds a dummy sublayerID column to the sequenceCoincidence tree
# This is necessary for the GateDigit_seqCoinc2Cones executable to work
# It gives the following errors, but they can be ignored if the sublayerID and volumeID are not needed:
# Error in <TTree::SetBranchAddress>: The pointer type given "Int_t" (3) does not correspond to the type needed "Long64_t" (16) by the branch: sublayerID
# Error in <TTree::SetBranchAddress>: The pointer type given "Int_t" (3) does not correspond to the type needed "Long64_t" (16) by the branch: volumeID

path = '/media/billoud/Volume/CT/GATE/3So100se/'
file_name = 'CC_sequenceCoincidence.root'
new_file_name = 'CC_sequenceCoincidence_new.root'

tree = uproot.open(path+file_name+':sequenceCoincidence')
with uproot.recreate(path+new_file_name) as file:
    df = tree.arrays(library='pd')
    df['sublayerID'] = -1
    file["sequenceCoincidence"] = df
tree_new = uproot.open(path+'CC_sequenceCoincidence_new.root:sequenceCoincidence')
print(tree_new.keys())