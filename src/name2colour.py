from colour import Color

def getColor(charBigramRanks, nameCharBigramHistogram, name, freq, max_freq):

    print("name = %s" % name)
    print("nameCharBigramHistogram = ", nameCharBigramHistogram)
#    print("charBigramRanks = ", charBigramRanks)

    # nameCharBigramList is representation of first name
    # calculates average character bigram rank value
    # converts this value into a hue value (range: )
    nr_name_bigrams = sum(nameCharBigramHistogram.values())
    print ("nr_name_bigrams = %d" % nr_name_bigrams)
    sum_of_ranks = sum([count*charBigramRanks[cb] for cb,count in nameCharBigramHistogram.items()])
    print ("sum_of_ranks = %d" % sum_of_ranks)
    average_rank = float(sum_of_ranks) / float(nr_name_bigrams)
    print("average rank of '%s' is %2.2f" % (name, average_rank))

    hue = getHue(charBigramRanks,average_rank)
    print("hue of '%s' is %2.2f" % (name, hue))

    luminosity = getLuminosity(freq, max_freq)

    return Color(hsl=(hue,1,luminosity))

def getHue(charBigramRanks,average_rank):
    min_rank = 1
    max_rank = len(charBigramRanks.keys())
    assert(min_rank == min(charBigramRanks.values()))
    assert(max_rank == max(charBigramRanks.values()))
    min_hue = 0
    max_hue = 360

    # Inspired by http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
    std = (average_rank - min_rank) / (max_rank - min_rank)
    scaled_hue = std * (max_hue - min_hue) + min_hue

    return scaled_hue

    
def getLuminosity(freq, max_freq):
    # The more frequent, the smaller the luminosity

    print("freq = %d" % freq)
    print("max_freq = %d" % max_freq)
    percentage = float(freq)/float(max_freq)
    print("percentage = %2.1f" % percentage)
    luminosity = 0.8 + percentage*0.2
    
    print("luminosity = %2.1f" % luminosity)

    return luminosity
