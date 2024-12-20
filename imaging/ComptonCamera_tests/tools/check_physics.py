import pandas
import uproot

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)

path = '/imaging/ComptonCamera_tests/Gate9.2/output/'
nentries_printed = None # None to read all entries

tree = uproot.open(path + 'CC_Hits.root:Hits')
print(tree.num_entries, 'entries in tree Hits')
df = tree.arrays(library='pd', entry_stop=nentries_printed)

df = df.drop(columns=['runID','sourcePosX', 'sourcePosY', 'sourcePosZ', 'sourceEnergy', 'sourcePDG', 'volumeID'])
df = df.drop(columns=['localPosX', 'localPosY', 'localPosZ'])
df = df.drop(columns=['layerName'])
df = df.drop(columns=['trackLocalTime'])
# print(df[df['eventID'] == 0])
print(df)

df_compt = df[df['postStepProcess'] == 'compt']
print(df_compt.shape[0], 'Compton interactions')

# Compton equation at maximum angle: E_gamma_final = E_gamma_initial / (1 + 2 * E_gamma_initial / mc2)
df_compt_outlimit = df_compt[df_compt['energyFinal'] < (df_compt['energyIniT'] / (1 + 2 * df_compt['energyIniT'] / 0.511))]
print(round(df_compt_outlimit.shape[0] / df_compt.shape[0] * 100, 1), '% compton scatterings above max energy limit of compton'
                                                                      ' equation due to electron not being at rest '
                                                                      '(Doppler broadening)')

# TODO: check if physics lists consider kinetic energy of bound electrons / doppler broaedning!
# https://geant4-userdoc.web.cern.ch/UsersGuides/PhysicsListGuide/html/electromagnetic/Opt4.html