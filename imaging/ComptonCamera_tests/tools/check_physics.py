import pandas
import uproot

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)

path = '/home/billoud/PycharmProjects/GateContrib/imaging/ComptonCamera_tests/ideal/sourcePoint_cameraSingle/output/'
nentries_printed = None # None to read all entries

tree = uproot.open(path + 'CC_Hits.root:Hits')
print(tree.num_entries, 'entries in tree Hits')
df = tree.arrays(library='pd', entry_stop=nentries_printed)
print(df)
df_compt = df[df['postStepProcess'] == 'compt']
print(df_compt.shape[0], 'Compton interactions')

# Compton equation at maximum angle: E_gamma_final = E_gamma_initial / (1 + 2 * E_gamma_initial / mc2)
df_compt_outlimit = df_compt[df_compt['energyFinal'] < (df_compt['energyIniT'] / (1 + 2 * df_compt['energyIniT'] / 0.511))]
print(round(df_compt_outlimit.shape[0] / df_compt.shape[0] * 100, 1), '% interactions not respecting compton equation')

# TODO: check if physics lists consider kinetic energy of bound electrons / doppler broaedning!
# https://geant4-userdoc.web.cern.ch/UsersGuides/PhysicsListGuide/html/electromagnetic/Opt4.html