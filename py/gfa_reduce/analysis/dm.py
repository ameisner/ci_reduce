import numpy as np
from desimeter.time import mjd2lst
from desimeter.fieldmodel import FieldModel
import copy
from astropy.table import Table
import time

def fit_dm_fieldmodel(header, ccds, _catalog):
    t0 = time.time()
    
    fm = FieldModel()

    catalog = copy.deepcopy(_catalog)

    catalog = Table(catalog)
    
    catalog = catalog[catalog['ang_sep_deg'] < 2.0/3600.0]

    if len(np.unique(catalog['extname'])) < 2:
        print('not enough sources with Gaia counterparts for a FieldModel')
        return None
        
    good_ccds = ccds[ccds['contrast'] > 2]['extname']
    
    # restrict to guide cameras with (contrast > 2)
    # if < 2 such guide cameras, then give up

    # restrict catalog to include only sources from
    # (contrast > 2) guide cameras

    keep = [(_extname in good_ccds) for _extname in catalog['extname']]
    
    # give up if fewer than some minimum number of stars ??

    catalog = catalog[keep]

    if len(np.unique(catalog['extname'])) < 2:
        print('not enough sources with Gaia counterparts for a FieldModel')
        return None

    fm.ra  = header['TARGTRA'] # other option is SKYRA
    fm.dec = header['TARGTDEC'] # other option is SKYDEC
    fm.expid = header['EXPID']
    hexrot_string = (header['FOCUS'].split(','))[5]
    fm.hexrot_deg = float(hexrot_string)/3600.0

    fm.adc1 = header['ADC1PHI']
    fm.adc2 = header['ADC2PHI']

    fm.mjd = np.mean(catalog['mjd_obs'])
    fm.lst = mjd2lst(fm.mjd)

    # need to have catalog trimmed to matches w/ in 2 asec of
    # a Gaia counterpart at some point

    fm.fit_tancorr(catalog)

    # any other metadata that I want to record?
    fm.n_cameras = len(np.unique(catalog['extname']))

    dt = time.time()-t0
    print('total time taken to derive desimeter FieldModel : ', dt, ' seconds')
    return fm
