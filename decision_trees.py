import numpy as np
import matplotlib.pyplot as plt
import pandas




def graphRawFX():
    games = pandas.read_csv("daily/TWSE/20170605/3443.csv")


    fig = plt.figure(figsize=(10, 7))
    ax1 = plt.subplot2grid((40, 40), (0, 0), rowspan=40, colspan=40)

    ax1.plot(games['price'], games['store'])
    ax1.plot(games['price'], games['buy'])
    #ax1.xazis.set_major_formatter()
    plt.grid(True)
    plt.show()
