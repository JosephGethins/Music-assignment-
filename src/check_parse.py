from input_readers import read_midi

for e in read_midi("input/cs322_simple_melody.mid"):
    print(e)