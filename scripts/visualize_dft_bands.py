import warnings as wn
wn.filterwarnings("ignore")

import pickle
import numpy as np
from fuller.mrfRec import MrfRec
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpes import fprocessing as fp, analysis as aly
from scipy import io as sio
from fuller.utils import loadHDF

def plot_bs(num_bands, n_epoch):
    """
    Plots the reconstructed BS constructed after n_epoch iterations
    """

    # Load preprocessed photoemission data
    bcsm = np.load('../data/processed/hslines/WSe2_vcut.npy')
    Evals = fp.readBinnedhdf5('../results/preprocessing/WSe2_preprocessed.h5')['E']
    ehi, elo = Evals[0], Evals[469]

    paths = np.load('../data/processed/hslines/WSe2_kpath.npz')

    reconbands = {}

    init_bands = np.empty((num_bands, 256, 256))
    recon_bands = np.empty((num_bands, 256, 256))

    for i in range(num_bands):
        # initialization bands
        with open(f'../results/band_data/init_band_n={i}_epoch={n_epoch}.pkl', 'rb') as f:
            init_band = pickle.load(f)
            init_bands[i] = init_band

        # reconstructed bands
        recon_band = loadHDF(f'../results/band_data/bs_recon_n={i}_epoch={n_epoch}.h5')
        kx, ky, Eb = recon_band['kx'], recon_band['ky'], recon_band['Eb']
        Eb.reshape(256, 256)
        recon_bands[i] = Eb
        
    bdi = aly.bandpath_map(np.moveaxis(init_bands, 0, 2), pathr=paths['rowInds'], pathc=paths['colInds'], eaxis=2)
    reconbands["init"] = bdi.T
    bdi = aly.bandpath_map(np.moveaxis(recon_bands, 0, 2), pathr=paths['rowInds'], pathc=paths['colInds'], eaxis=2)
    reconbands["recon"] = bdi.T


    pos = paths['pathInds']
    pos[-1] -= 1

    ff, axa = plt.subplots(1, 1, figsize=(10.5, 6))
    im = axa.imshow(bcsm, cmap='YlOrBr', extent=[0, 185, elo, ehi], aspect=12)

    for ib in range(num_bands): # normally set to 14
        axa.plot(reconbands['init'][:,ib], color='cyan', linestyle='dashed', zorder=1)
        axa.plot(reconbands['recon'][:,ib], color='lime', zorder=2)


    axa.tick_params(axis='y', length=8, width=2, labelsize=15)
    axa.tick_params(axis='x', length=0, labelsize=15, pad=8)
    axa.set_ylim([elo, ehi])
    axa.set_xticks(pos)
    axa.set_xticklabels(['$\overline{\Gamma}$', '$\overline{\mathrm{M}}$',
                        '$\overline{\mathrm{K}}$', '$\overline{\Gamma}$'])
    axa.set_ylabel('Energy (eV)', fontsize=20)
    for p in pos[:-1]:
            axa.axvline(x=p, c='k', ls='--', lw=2, dashes=[4, 2])
            
    axa.set_title('Reconstruction', fontsize=15, x=0.8, y=0.9)
    cax = inset_axes(axa, width="3%", height="30%", bbox_to_anchor=(460, 90, 440, 200))
    cb = plt.colorbar(im, cax=cax, ticks=[])
    cb.ax.set_ylabel('Intensity', fontsize=15, rotation=-90, labelpad=17)

    plt.savefig(f'../results/reconstruction/bs_recon_{n_epoch}.png')

if __name__=="__main__":
    plot_bs(8, 10)