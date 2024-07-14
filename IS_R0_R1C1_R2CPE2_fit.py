import numpy as np
import math as m
import matplotlib.pyplot as plt
from impedance.visualization import plot_nyquist
from impedance import preprocessing
from impedance.models.circuits import CustomCircuit
from impedance.models.circuits import fitting

# Step 1: Load your data
# The file should have frequency, Z_real, and Z_imag columns
frequencies, Z = preprocessing.readCSV('C:/Users/altor/Documents/PhD Thesis/B5NoNPIS.csv')
#frequencies, Z = preprocessing.readCSV('C:/Users/altor/Documents/PhD Thesis/B51_1NPIS.csv')

# keep only the impedance data in the first quandrant
frequencies, Z = preprocessing.ignoreBelowX(frequencies, Z)

bounds = ((Z[0].real*0.9, 0,    0,    0, 0, 0),  # Lower bounds for R0, R1, C1, R2, C2
          (Z[0].real*1.1, 1e11, 1, 1e11, 1, 1))  # Upper bounds for R0, R1, C1, R2, C2
circuit='R0-p(R1,C1)-p(R2,CPE2)'
# Step 2: Define the circuit model
# The string defines the circuit configuration
# R0-p(R1,CPE1)-p(R2,CPE2) represents an R-(RC)-(RC) circuit
fitting.set_default_bounds(circuit, constants={})
R0_guess = Z[0].real

R1_guess = 3E5
f1_guess = 10000
C1_guess = 21e-9#1/(2*m.pi*f1_guess*R1_guess)

R2_guess = 6e10#10000
f2_guess = 0.2
CPE2_guess = 7e-7#1/(2*m.pi*f2_guess*R2_guess)
CPE2a_guess = 0.5

circuit = CustomCircuit(initial_guess=[R0_guess, R1_guess, C1_guess, R2_guess, CPE2_guess,CPE2a_guess], circuit=circuit)
fit_frequencies = np.logspace(m.log(min(frequencies)),m.log(max(frequencies)),1000)
# Step 3: Fit the model to the data
circuit.fit(frequencies, Z, bounds = bounds)
Z_fit = circuit.predict(fit_frequencies)
# Step 4: Print the fitted parameters
print(circuit)

# Step 5: Plotting
fig, ax = plt.subplots()
plot_nyquist(Z, fmt='o', scale=10, ax=ax)
plot_nyquist(Z_fit, fmt='-', scale=10, ax=ax)

plt.legend(['Data', 'Fit'])
plt.show()
