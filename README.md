uk_firstname_network

Hue (red - green - orange - blue - red) => average rank of character bigrams in name (weird word form <--> common word form)
Saturation => CONSTANT
Luminance => (higher/lower number of elements in partition = less/more luminous)

~/work/uk_firstname_network$ python3 src/build_firstname_network.py --inFileCSV data/ukbabynames_female.csv --outFileGraphML out/uk_girls.graphml --rankThreshold=200 --simThreshold=0.63 --degreeThreshold 2 --inFileMustHaveCSV data/must_have_female.txt --bonusMultiplier 1.2 --minFreq 15

