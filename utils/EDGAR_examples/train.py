#!/usr/bin/python

import os
import sys
import getopt
import caffe
import matplotlib.pyplot as plt
import numpy as np
import time

models  = {"places205_alexnet":   "models/places205_alexnet/places205CNN_iter_300000_upgraded.caffemodel",
	   "places205_hybrid":	  "models/places205_hybrid/hybridCNN_iter_700000_upgraded.caffemodel",
	   "places205_googlenet": "models/places205_googlenet/googlenet_places205_train_iter_2400000.caffemodel",
	   "caffenet": 		  "../caffe/models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel"}

solvers = {"edgar21_caffenet": 	  "models/edgar21_caffenet/solver.prototxt",
	   "edgar21_alexnet":     "models/edgar21_alexnet/solver.prototxt",
	   "edgar21_googlenet":   "models/edgar21_googlenet/solver.prototxt",
	   "edgar21_hybrid":      "models/edgar21_hybrid/solver.prototxt"}

os.chdir("..")

def parseModel(arg):
  if arg in models:
    return models[arg]
  else:
    return arg
  
def parseSolver(arg):
  if arg in solvers:
    return solvers[arg]
  else:
    return arg

def main(argv):
  ftmodel 	= [None]
  model 	= [None]
  niter		= 100
  
  logstep	= 20
  
  # Parseamos los argumentos.
  try:
    opts, args = getopt.getopt(argv,"f:m:i:l:b:")
  except getopt.GetoptError:
    print 'bad usage'
    sys.exit(2)
      
  for opt, arg in opts:
    if opt == "-f":
      ftModel = [parseModel(arg)]
    if opt == "-m":
      model = [parseSolver(arg)]
    if opt == "-i":
      niter = int(arg)
    if opt == "-l":
      logstep = int(arg)
    if opt == '-b':
      f = open(arg, "r")
      lines = f.readlines()
      ftmodel = []
      model = []
      for line in lines:
	sol, mod = line.rstrip().split(',')
	model += [parseSolver(sol)]
	ftmodel += [parseModel(mod)]
  
  # GPU por defecto
  caffe.set_device(0)
  caffe.set_mode_gpu()

  t = time.time()
  
  plt.ion()
  
  fig = plt.figure()
  plotLoss = fig.add_subplot(211)
  
  loss = []
  solvers = []
  # Solver that finetunes from original caffenet
  for x in range(len(model)):
    print model[x]
    solvers += [caffe.SGDSolver(model[x])]
    if ftmodel[x] != None:
      solvers[x].net.copy_from(ftmodel[x])
    
    # Inicializamos las estructuras que guardaran los datos.
    loss += [np.zeros(niter)]
  handles =[]
  for it in range(niter):
    
    if it % logstep == 0:
      plotLoss.cla()
      plotLoss.axis((0, it, 0, 10))
      handles = []
    for x in range(len(solvers)):
      solvers[x].step(1)
      loss[x][it] = solvers[x].net.blobs['loss'].data
      
      if it % logstep == 0:
	print "[Solver%d] iter %d, loss=%f, time/%diter=%f" % (x, it, loss[x][it], logstep, time.time()-t)
	t = time.time()
	handle, = plotLoss.plot(range(0, it), loss[x][:it], label="Solver"+str(x))
	handles += [handle]
	plotLoss.grid(True)
	
    if it % logstep == 0:
      plotLoss.legend(handles)
      plt.pause(0.0001)
      plt.show()
      
      
  print 'done'
  plt.ioff()
  plt.show()

if __name__ == "__main__":
  main(sys.argv[1:])
