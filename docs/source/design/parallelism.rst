.. role:: small

Improve performance of fitting capability within Labcontrol
===========================================================

This text explains the lessons learned and steps taken to improve the performane of the curve fitting software which has been written
within/for Labcontrol. Originaly, curve fitting capabilities were thought to be a nifty addition for labcontrol in order to:

- Fit parameters of first and secondorder transferfunctions on response data acquired during typical control stuff.
- Fit parameters of a theoratical sine functions on sinusoidal (time) data with the aim to find phaseshift between to signals

Although both functionalities have been coded into labccontrol. The latter one has been tested the most, which showed a problem with
the sinefitting code. When used with a Tektronix TDS2002C oscilloscope, producing 2500 samples per channel, the code functions without problems, 
albeit rather slow. When used with a Siglent SDS1202X-E scope, which returns 7000 samples per channel, the code crashed. The code stops 
excuting, because of a Numpy kind of error, stating broadcasting of the matrices used, is not possible. And indeed, one of the fitted arrays
suddenly appears not to be 7k of size, but only contains 350 points.

Design of sine fitting code 
---------------------------

The Tektronix TDS2002C comes with a number of interesting measurements functions, such as: 

* determination of the Pk-Pk,  
* measuring the frequency of a channel and 
* taking the phase difference between channels.

Especially the last feauture was quite interesting for usage in a script for creating Bodeplots based on two channel measurements. 
Unfortunately, these nice features turned out only to work nicely on TDS2002C's display. When called with VISA, the delay in responses from 
queries increases massive, from 1 second to over 5 seconds each query, making usage of the TDS 2000 series too slow for labcontrol. Next to 
speed performance, only some TDS scopes in our lab had this phase measuring capabilities. Therefore an alternative was needed, which was 
swiftly found in the fitting capabilities of scipy.

During the writing of the fitting code, an interesting piece of software appeared on the horizon: lmfit, an extension of the scipy package.
Its advantages: a more consistent and intuitive interface compared to scipy and also coming with a lot of very good examples and extensive
doccumentation.

The approach of the original sine fitting code was:

1. A PhaseEstimator class for controlling the fitting the sine function parameters of the inputsignal as well as the outputsignal.
2. PhaseEstimator holds and instantiates two private datamembers: inputFitter and outputFitter. Both variables are of type SineFitter.
3. SineFitter is a convenient class centered around lmfit.Model (opzoeken hoe ik hiervan een automatische referentie kan maken naar de documentatie van lmfit). It task is to fit the parameters of a standard sine function on sampled data acquired by an oscilloscope.
4. Usage of PhaseEStimator is according a two step API: 

    a. Call PhaseEstimator().setAPriori(ampIn=val1, ampOut=val2, freq=freq), with val1, val2 and freq the currenty measured values.
    b. Subsequently call PhaseEstimator().estimate(). This method will perform the parameter fitting of input and output and will return the phase difference between input an output.

5. Both, PhaseEstimator and SineFitter are coded with the rule "See no Evil, if you hear no Evil". No assumptions have been made about the
way used packages have been designed and build. For example, the fitting code is quite naive about the question if lmfit code is reentrant 
or not. Therefore PhaseEstimator().estimate() implemented logic for getting the phase difference is simple:

    a. First estimate the parameters of the input signal.
    b. Then, estimate the parameters of the outupt signal.
    c. Finally substract the 'best values' of lmfit's phase estimations.

Between the three lines of code, no synchronization or locking has been performed.

Problem description
-------------------

As written, the phase estimation works normally and in debug mode with 2.5k samples per waveform. Estimation is not very fast: 
two fits takes between 3 and 6 seconds. When using 7k samples or more per waveform, execution will fail during normal run and 
occassionally succeeds when debugging. The error ('can not broadcast') during normal running is the result of a strange
difference of the size between input and output arrays with a factor of 20: 7k versus 350 elements. The origin of this behaviour is 
unknown. Now, the naive way of coding fails to apply. For now, a timing issues is assumed to be the problem. Fitting a 7k data array
takes considerable more time compared to a 2.5k array. Somewhere in the code stack, a timeout probably occurs, which interrupts 
the fittin, ultimately leading to the strange mismatch in array size. Big question: why? As time of writing, no clue, but keeping
the main thread hanging for a long time twice, without locking critical data, is asking for trouble.

The fixing concept 
------------------

Based on gut feeling just described, one can try to lock the critical variables during fitting and combine this in using
threading. Another option would be to push the parameter fitting work onto a separate process. During some research on Internet, 
dispatching the fitting itself on a separate process was given preference over threading. The reasons for preference are:

1. Doing a parameter fit does not depend on I/O, assuming the data to fit on has been acquired already.
2. Dispatching execution to another process will very likely improve speed. Threads can't, because threads all share a same processor. Spawining work on process makes true parallellism.
3. Rescoures needed to do the work, will inherited (copied?) and pushed onto the new processor, making usage mutexes of semaphores superfluous.
4. According to Pythons core documentation, the support for multiprocessing is quite good and stable on the major OS options: Windows 11, Mac and Linux. Remark: given the user selects for 'spawning', which is the default choice at Windows and Mac, but not at Linux (which is 'fork'). (Verwijzing nog maken!)

Parallellism and Python
-----------------------

Python's multiprocessing module offers both concepts 'thread' and 'process'. This section describes the first steps taken
to get acquainted to Python's way of doing this in really parallell-land and how these steps were translated in a first version of  parallel fitting code.

.. include:: spawnsimple.rst
.. include:: spawnonce.rst
