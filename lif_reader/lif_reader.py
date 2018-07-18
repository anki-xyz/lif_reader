import numpy as np
from pyprind import prog_percent
import deepdish as dd
import javabridge
import bioformats
from xml.etree import ElementTree as ETree


def readLifAndSaveAsH5 (fn):
    '''Read LIF (Leica) file using bioformats and save it compressed as HDF5 file
    :param fn: filename
    :return: filename of HDF5 file'''
    print('Working on ', fn)
    javabridge.start_vm(class_path=bioformats.JARS)

    fn_hdf5 = fn.replace('.lif','.h5')
    md = bioformats.get_omexml_metadata(fn) # Load meta data
    mdroot = ETree.fromstring(md) # Parse XML
    meta = mdroot[1][3].attrib # Get relevant meta data
    
    # Pre-allocate RAM
    prealloc_stack = np.empty((int(meta['SizeZ']), 
                           int(meta['SizeT']), 
                           int(meta['SizeX']), 
                           int(meta['SizeY'])), dtype=np.uint16)
    
    # Create ImageReader instance
    ir = bioformats.ImageReader(fn)
    
    # Load the whole stack...
    for plane in prog_percent(range(prealloc_stack.shape[0])):
        for t in range(prealloc_stack.shape[1]):
            prealloc_stack[plane, t] = ir.read(z=plane, t=t, rescale=False)[...,0]
           
    javabridge.kill_vm()

    # Save stack as HDF5 file with BLOSC compression.
    dd.io.save(fn_hdf5, {'stack': prealloc_stack, 'meta': meta}, compression='blosc')
    
    print('Data saved.\n')

    return fn_hdf5

# Execute this 
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QFileDialog
    app = QApplication([])
    fn = QFileDialog.getOpenFileName(caption='Select a LIF file to be converted to HDF5',filter='*.lif')[0]

    if fn:
        fn_hdf5 = readLifAndSaveAsH5(fn)
    
        print('fn_hdf5: ', fn_hdf5)