function R2 = computeR2(b, diameters, yData, wavelength,L_left,L_right)
    yFit = zeros(length(diameters),1);
    for iy = 1:length(yFit)
    yFit(iy) = plasmonRegion(diameters(iy), wavelength,L_left,L_right,b);
    end
    yFit = yFit/max(yFit);
    SSres = sum((yData - yFit).^2);
    SStot = sum((yData - mean(yData)).^2);
    R2 = 1 - SSres/SStot
end