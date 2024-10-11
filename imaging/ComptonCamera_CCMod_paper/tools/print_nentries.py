import uproot

path = '../output/'

print([line.split('=')[1].strip() for line in open(path+'stats.txt') if 'NumberOfEvents' in line][0], 'events')
# print(uproot.open(path+'CC_Hits.root:Hits').num_entries, 'Hits')
print(uproot.open(path+'CC_Singles.root:Singles').num_entries, 'Singles')
print(uproot.open(path+'CC_Coincidences.root:Coincidences').num_entries, 'Coincidences')
print(uproot.open(path+'CC_sequenceCoincidence.root:sequenceCoincidence').num_entries, 'Sequence Coincidences')

# TIME 0.2
# MersenneTwister / Seed 6781

############################################
# NO ACTOR AT ALL
# 168413 events
# 1186863 Hits

############################################
# ACTOR DEFAULT
# 168413 events
# 1186863 Singles
# 1185168 Coincidences

# + ADDER
# 168413 events
# 2582 Singles
# 84 Coincidences

# + Clustering (3mm)
# 168413 events
# 2998 Singles
# 786 Coincidences

############################################
# + Clustering (3mm) + TCW (50 ns)

# NOTHING MORE
# 168413 events
# 2998 Singles
# 790 Coincidences

# + ADDER
# 168413 events
# 2582 Singles
# 88 Coincidences

# + CATEGORY2
# TODO: why is a digitizer module changing the number of events?
# TODO: => check SimulationStatisticActor
# TODO: => maybe some events are counted twice?
# 169285 events
# 3073 Singles
# 789 Coincidences

# + CATEGORY2 + GLOBAL THL
# 169285 events
# 2453 Singles
# 506 Coincidences

# + ADDER + CATEGORY2
# 169392 events
# 2652 Singles
# 90 Coincidences

# + ADDER + CATEGORY2 + GLOBAL THL 0 keV
# 169392 events
# 2648 Singles
# 88 Coincidences

# + ADDER + CATEGORY2 + LOCAL THL 85 keV
# 169392 events
# 415 Singles
# 0 Coincidences