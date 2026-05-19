clear; clc; close all;

function plot_pattern3D(pattern, THETA, PHI, titleStr)

R = pattern;

X = R .* sin(THETA) .* cos(PHI);
Y = R .* sin(THETA) .* sin(PHI);
Z = R .* cos(THETA);

c_sens = 15;
pat_dB = 10*log10(pattern);

figure;
surf(X, Y, Z, pat_dB, ...
    'EdgeColor', 'none', ...
    'FaceColor', 'interp');

colormap(jet);
clim([-c_sens 0]);

xlabel('x');
ylabel('y');
zlabel('z');

a=colorbar;
a.Label.String = 'Normalized gain (dB)';

title(titleStr);
grid on;
axis equal;
view(45,30);

end


f = 15e9;
c = 3e8;
lambda = c/f;
k0 = 2*pi/lambda;

L = lambda/2;
W = lambda;

theta0 = pi/6;   % 30 deg steering
phi0   = pi/18;   % phi plane
dx = lambda/2;
dy = lambda/2;

% Angular grid
theta_vec = linspace(-pi/2, pi/2, 500);
phi_vec   = linspace(0, 2*pi, 500);
[THETA, PHI] = meshgrid(theta_vec, phi_vec);

% Array factor (8x8)
A_factor2 = zeros(size(THETA));
for m = 0:7
    for n = 0:7
        A_factor2 = A_factor2 + ...
            exp(1j*k0*n*dy*(sin(THETA).*sin(PHI) - sin(theta0)*sin(phi0))) .* ...
            exp(1j*k0*m*dx*(sin(THETA).*cos(PHI) - sin(theta0)*cos(phi0)));
    end
end

% Element factor (patch)
kx = k0*sin(THETA).*cos(PHI);
ky = k0*sin(THETA).*sin(PHI);
vx = (kx*L)/(2*pi);
vy = (ky*W)/(2*pi);
F  = cos(pi*vx).*sinc(vy);   % sinc in MATLAB is already normalized sinc

% Combined pattern
g    = (cos(THETA).^2 .* sin(PHI).^2 + cos(PHI).^2) .* F.^2;
gain = g .* abs(A_factor2).^2;
nor_gain = gain / max(gain(:));

% Plot

plot_pattern3D(nor_gain, THETA, PHI, 'Total radiation pattern (directed 8x8)');
%plot_pattern3D(g, THETA, PHI, 'Total radiation pattern (directed 8x8)');

