diameters = [1.8,2.2,3,4,5,10,20,50,1.8,2.2,3,4,5,10,20,50];
wavelength = 450;
b_max = 10;
b_min = 4;

% Initial guesses for b
a = 6; % lower bound
b = 6; % upper bound
tol = 1e-8; % tolerance for convergence
L_left = 79*10^-6; %m
L_right = 79*10^-6; %m
% Call the bisection method
optimalB = bisectionOptimize(a, b, tol,diameters, rawY, wavelength,L_left,L_right)