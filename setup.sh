source env/bin/activate
export SUBEVENTHOME=${VIRTUAL_ENV}/../
export SUBEVENTDATA=${VIRTUAL_ENV}/../config
export SUBEVENTPATH=${VIRTUAL_ENV}/lib/python2.7/site-packages/pysubevent
export LD_LIBRARY_PATH=${SUBEVENTHOME}:${SUBEVENTPATH}/cfdiscriminator:${SUBEVENTPATH}/subevent:${LD_LIBRARY_PATH}
export DYLD_LIBRARY_PATH=${SUBEVENTPATH}/cfdiscriminator:${SUBEVENTPATH}/subevent:${DYLD_LIBRARY_PATH}
#export PYTHONPATH=${VIRTUAL_ENV}/lib/python2.7/site-packages:${PYTHONPATH}
#export LD_LIBRARY_PATH=${VIRTUAL_ENV}/../:${LD_LIBRARY_PATH}
