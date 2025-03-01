# Import packages
import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

from mpes import analysis as aly, fprocessing as fp
from fuller.mrfRec import MrfRec
from fuller.utils import loadHDF


# Load preprocessed data
print("loading preprocessed data...")
data = loadHDF('../data/pes/3_smooth.h5')
E = data['E']
kx = data['kx']
ky = data['ky']
I = data['V']

# Create MRF model
print("creating mrf model...")
mrf = MrfRec(E=E, kx=kx, ky=ky, I=I, eta=.12)
mrf.I_normalized = True

# Initialize mrf model with band structure approximation from DFT
print("initializing E_0 to DFT calculations...")
path_dft = '../data/theory/WSe2_HSE06_bands.mat'


def reconstruct(band_index):
    """
    Wrapper function for reconstructing band structure given some parameters
    """

    band_index = 1  # there is a total of 80 different bands
    offset = 0.4    # default was -0.1
    k_scale = 1.0

    kx_dft, ky_dft, E_dft = mrf.loadBandsMat(path_dft)
    print("band structure shape:", E_dft.shape)

    # possible modify source to train multiple bands at once
    mrf.initializeBand(kx=kx_dft, ky=ky_dft, Eb=E_dft[band_index,...], offset=offset, kScale=k_scale, flipKAxes=True)

    # Plot slices with initialiation to check offset and scale
    print("plotting initialized mrf...")

    mrf.plotI(ky=0, plotBandInit=True, cmapName='YlGn', bandColor='tab:orange', initColor='m')
    plt.savefig("../results/reconstruction/init_ky_0")

    mrf.plotI(kx=0, plotBandInit=True, cmapName='YlGn', bandColor='tab:orange', initColor='m')
    plt.savefig("../results/reconstruction/init_kx_0")

    # Run optimization to perform reconstruction
    print("training model...")
    eta = 0.1 # default 0.1
    n_epochs = 150 # default 150

    mrf.eta = eta
    mrf.iter_para(n_epochs)

    # Plot results
    print("plotting reconstructed bands...")
    mrf.plotBands(surfPlot=True)
    plt.savefig("../results/reconstruction/bs_surface")

    mrf.plotI(ky=0, plotBand=True, plotBandInit=True, cmapName='YlGn', bandColor='tab:orange', initColor='m')
    plt.savefig("../results/reconstruction/band_ky_0")

    mrf.plotI(kx=0, plotBand=True, plotBandInit=True, cmapName='YlGn', bandColor='tab:orange', initColor='m')
    plt.savefig("../results/reconstruction/band_kx_0")

    # Save results
    path_save = '../results/band_data/'
    mrf.saveBand(f"{path_save}mrf_rec_{band_index}.h5", index=band_index)

    # think about maybe serializing the mrf for later use


# call the wrapper function
for band_index in range(14):
    print(f"reconstructing the {band_index}th band...")
    reconstruct(band_index)