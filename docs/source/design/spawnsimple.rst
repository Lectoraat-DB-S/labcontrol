.. _design-version1:

Spawining the simple way
^^^^^^^^^^^^^^^^^^^^^^^^

As stated by the Python doc (:py:mod:`multiprocessing`), three ways exists to start a new process (:py:class:`multiprocessing.Process`):  'spawn', 'fork' en 'forkserver'. For Windows, 'spawn' is the default option. 'Spawning' means a fresh Python interpreter being created, where the new process only inherits necessary resources so it able to execute the process object's run() method. Therefore 'spawn' is probably the best choice, as it maximize isolation of data compared to the other two start options.
Normally, the run() method equals a worker function set by :py:class:`multiprocessing.Process` `target` parameter, as shown below:

.. code-block:: python

    def f(name):
        print('hello', name)

    p = Process(target=f, args=('bob',))
    p.start()
    p.join()

Here, `f` is the worker function to be executed by the process. Python has to be able to serialize `f` ('pickle'). Therefore, 'f' has to be:

1. A reference to an global scoped function (if it is not part of an object) or 
2. A reference to a member function of some type, which is known to Python. 


If not, execution will surely fail. Serializing is not the only sensible thing to do. See `this link`_ for more do's and don'ts.

.. _this link: https://docs.python.org/3/library/multiprocessing.html#multiprocessing-programming


Spawning into labcontrol
^^^^^^^^^^^^^^^^^^^^^^^^
After writing and testing dummy code, following has been incorporated into PhaseEstimator's and SineFitter's code:

1. A new member funtion 'makefit_mp_worker()' has been added to class SineFitter:

.. code-block:: python

    class SineFitter(object):

    def makefit_mp_worker(self, outQueue):
        outDict = {}
        self.makeParam()
        self._result = self.model.fit(data=self.ydat, params=self.params, x=self.xdat, 
                                       method=self.method)
        self.fitSummary = self._result.summary()
        outDict.update(self.bestValues)
        outQueue.put(outDict)

The last two lines of code puts the best fit values from ModelResult.summary()in the output Queue,


2. A new member function of PhaseEstimator, mp_fit(), does the actual spawning of the two worker SineFitter functions and waits until they finish:

.. code-block:: python

    class PhaseEstimator(ScopeFunction):
        
        def mp_fit(self):
            resultQueue1 = multiprocessing.Queue()
            resultQueue2 = multiprocessing.Queue()
            #chunksize = int(math.ceil(len(bufSize) / float(nprocs)))
            procs = []
            
            p1 = multiprocessing.Process(target=self._inputFitter.makefit_mp_worker, args=(resultQueue1, ))
            procs.append(p1)
            p1.start()
            p2 = multiprocessing.Process(target=self._outputFitter.makefit_mp_worker,args=(resultQueue2, ))
            procs.append(p2)
            p2.start()

            # Collect all results into a single result dict. We know how many dicts
            # with results to expect.
            
            #for i in range(nprocs):
            #    resultdict.update(out_q.get())

            # Wait for all worker processes to finish
            for p in procs:
                myp:multiprocessing.Process = p
                print(f"waiting for process with p: {myp.pid} to join")
                p.join()
            # all processes are finished. Now, set the best fit results back into the objects of this process.
            self.inputFitter.bestValues = resultQueue1.get()    
            self.outputFitter.bestValues = resultQueue2.get()
            # now return the estimate method to calculate phasedifference
            return

In the code above self._inputFitter and self._outputFitter are both references to two SineFitter instances.

For using the phase estimation in labcontrol, one has to do keep this api:

1. At creation of a new PhaseEstimator() object has to be initialized first once.
2. To perform a phase estimation:

    a. Set first guesses prior to the estimation, by calling PhaseEstimator().setAPriori(). 
    b. Start the estimation process by calling PhaseEstimator().estimate()
    
As an example, see code snippet of function doACSweep() from frequencyResponse.py below:

.. code-block:: python

    def doACSweep():
        
        estimator = PhaseEstimator(inputWF=scopeChan1.WF, outputWF=scopeChan2.WF, debugPrint=False)
        for freq in myFreqs:
            
            estimator.setAPriori(ampIn=val1, ampOut=val2, freq=freq)
            estimator.estimate()

Spawning results
^^^^^^^^^^^^^^^^

1. No Numpy broadcasting errors
2. Total time for fitting two 7k samples waveforms takes somewhere between 4 and 9 seconds. Always same trend: initial fitting takes long up to 9 seconds, where fitting at the end of the sweep takes far less time.
3. Some playing has been done with the code method mp_fit() of PhaseEstimator, some times join() has been omitted and or been placed before of after the queue.get() calls. No big differences, but the fastest fits seems to occur with the snippet code below.

.. code-block:: python

    #Now wait on the two process queues:
    self.inputFitter.bestValues = resultQueue1.get()    
    self.outputFitter.bestValues = resultQueue2.get()
    #And for savety: wait on both processes to finish
    for p in procs:
        myp:multiprocessing.Process = p
        print(f"waiting for process with p: {myp.pid} to join")
        p.join()
    return

Some thoughts
^^^^^^^^^^^^^

1. Spawning process is a time consuming matter (according to :py:class:`multiprocessing.Process` docs)
2. According to the programming tips found on :py:mod:`multiprocessing`, one should not move large amounts of data between process objects. Current implementation is very likely a ugly one in this regard. SineFitter is bulky kind of wrapper vor lmfit.model(). Meant to be an easy interface for using fitting, it contains references to memory consuming objects. Options to improve might be:

    a. Instead of just throwing the process away after one time usage and creation a new one each time you want te make a fit, it will likely be far better to start two fitter processes once and reuse them till the end of the running script. Implementing this would require some addition of input queue code and code a way to stop both processes.
    b. The current code could be improved by trying to use as little memory as possible. This will save the amount of pickle between calls, which will improve the speed of the fits.
