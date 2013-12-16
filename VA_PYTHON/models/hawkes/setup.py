from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("getR",["getR.pyx"],libraries=["m"])]

setup(
    name = 'getR',
    cmdclass = {'build_ext':build_ext},
    ext_modules = ext_modules
)
