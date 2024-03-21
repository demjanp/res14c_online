## Res14C - Online
Radiocarbon Dating Resolution Calculator - Online

Crated on 20.3.2024

<details>
<summary>Table of Contents</summary>

1. [About Res14C - Online](#about)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Developer Notes](#developer)
5. [Contact](#contact)
6. [Acknowledgements](#acknowledgements)
7. [License](#license)

</details>

## About Res14C - Online <a name="about"></a>

An online implementation of the method of calculating the expected temporal resolution of radiocarbon dating based on the expected actual age of the samples. For an overview of the method see:

Svetlik, I., A. J. T. Jull, M. Molnár, P. P. Povinec, T. Kolář, P. Demján, K. Pachnerova Brabcova, et al. “The Best Possible Time Resolution: How Precise Could a Radiocarbon Dating Method Be?” Radiocarbon 61, no. 6 (December 2019): 1729–40. (https://doi.org/10.1017/RDC.2019.134).

The data for different time periods is pre-calculated using the Python script [process.py](src/res14c_online/process.py).
The results can be published and queried online as a [Chart.js](https://www.chartjs.org/) script implemented in [res14c.htm](src/res14c_online/web/res14c.htm).

## Installation <a name="installation"></a>
Upload the files [res14c.htm](src/res14c_online/web/res14c.htm) and [c14_resolution_data.csv](src/res14c_online/web/c14_resolution_data.csv) to a web server.
The contents of c14_resolution_data.csv can be re-generated using different settings via [process.py](src/res14c_online/process.py) (see [Usage](#usage))

## Usage <a name="usage"></a>
Open [res14c.htm](src/res14c_online/web/res14c.htm) uploaded on a web server via a web browser and enter the lower and upper bounds of the expected dating of the sample. A graph showing the expected resolution of C-14 dating of this sample will be displayed, with the posibility to download the data in a CSV format.

To re-generate the underlaying data with different settings like dating uncertainty or calibration curve, use the Python script [process.py](src/res14c_online/process.py) in the format:

```
process.py [-h] [-from FROM] [-to TO] [-uncert UNCERT] [-curve CURVE] 
				[-result RESULT] [-max_cpus MAX_CPUS] [-max_queue MAX_QUEUE]
options:
  -h, --help            show this help message and exit
  -from FROM            Lower bound in years AD. Use negative values for BC 
						(default: -20000)
  -to TO                Upper bound in years AD. Use negative values for BC 
						(default: 1950)
  -uncert UNCERT        Basic measurement uncertainty for 0 BP (1950 AD) (default: 15)
  -curve CURVE          File path to load the radiocarbon age calibration curve 
						(default: intcal20.14c)
  -result RESULT        File path to store the result in CSV format 
						(default: c14_resolution_data.csv)
  -max_cpus MAX_CPUS    Maximum number of CPUs to use (-1 = all available) (default: -1)
  -max_queue MAX_QUEUE  Maximum number of jobs in the queue. 
						Use higher values on machines with sufficient RAM (>8 GB)
                        (default: 100)
```

See [Developer Notes](#developer) on instructions how to set up a python environment to run the script.

After executing process.py, copy the created dataset, specified by the -result argument, to the directory ```src/res14c_online/web```.
If necessary, modify the script in [res14c.htm](src/res14c_online/web/res14c.htm) so the code ```const response = await fetch("c14_resolution_data.csv");``` points to the current dataset file. Upload the updated dataset and script to the web server.

## Developer Notes <a name="developer"></a>
### Preparing the Virtual Environment <a name="venv"></a>
Running the process.py script requires Python 3.

To prepare a Python virtual environment open a terminal or command prompt window and type the following commands:
```
git clone https://github.com/demjanp/res14c_online.git

python -m venv venv

venv\Scripts\activate.bat

python.exe -m pip install --upgrade pip

cd res14c_online

pip install -e .

```
To run the script, go to the folder ```src/res14c_online/```. See [Usage](#usage) on instructions how to run the script.


## Contact: <a name="contact"></a>
Peter Demján (peter.demjan@gmail.com)

Institute of Archaeology of the Czech Academy of Sciences, Prague, v.v.i.

## Acknowledgements <a name="acknowledgements"></a>

Development of this software was supported by project OP JAC "Ready for the future: understanding long-term resilience of the human culture (RES-HUM)", Reg. No. CZ.02.01.01/00/22_008/0004593 of the Ministry of Education, Youth, and Sports of the Czech Republic and EU.

Uses atmospheric data [intcal20.14c](intcal20.14c) from:

Reimer PJ, Bard E, Bayliss A, Beck JW, Blackwell PG, Bronk Ramsey C, Buck CE, Cheng H, Edwards RL, Friedrich M, Grootes PM, Guilderson TP, Haflidason H, Hajdas I, Hatté C, Heaton TJ, Hogg AG, Hughen KA, Kaiser KF, Kromer B, Manning SW, Niu M, Reimer RW, Richards DA, Scott EM, Southon JR, Turney CSM, van der Plicht J. IntCal13 and MARINE13 radiocarbon age calibration curves 0-50000 years calBP. Radiocarbon 55(4). DOI: 10.2458/azu_js_rc.55.16947

This software uses the following open source packages:
* [NumPy](https://www.numpy.org/)
* [SciPy](https://scipy.org/)
* [Chart.js](https://www.chartjs.org/)


## License <a name="license"></a>

This code is licensed under the [GNU GENERAL PUBLIC LICENSE](https://www.gnu.org/licenses/gpl-3.0.en.html) - see the [LICENSE](LICENSE) file for details