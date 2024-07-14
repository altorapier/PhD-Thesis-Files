function b_opt = bisectionOptimize(a, b, tol, diameter, yData, wavelength,L_left,L_right)
    c = (a + b)/2;
    while (b - a)/2 > tol
        if computeR2(c, diameter, yData, wavelength,L_left,L_right) < computeR2(c + tol, diameter, yData, wavelength,L_left,L_right)
            a = c;
        else
            b = c;
        end
        c = (a + b)/2;
    end
    b_opt = c;
end