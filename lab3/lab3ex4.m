clear; clc; close all;

global c f lambda k0 dy LOW_RES HIGH_RES

c = 3e8;
f = 15e9;

lambda = c/f;
k0 = 2*pi/lambda;

dy = lambda/2;

LOW_RES = 1000;
HIGH_RES = 10000;

%% =========================================================================
% Functions
% =========================================================================


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
    caxis([-c_sens 0]);

    xlabel('x');
    ylabel('y');
    zlabel('z');

    xlim([-1.01 1.01]);
    ylim([-1.01 1.01]);
    zlim([0 2.02]);

    title(titleStr);
    grid on;
    axis equal;
    view(45,30);

end

%% =========================================================================

function AF_norm = array_factor(dy, dx, PHI, THETA, N, M)

    global k0

    if nargin < 6
        M = 1;
    end

    AF = zeros(size(THETA));

    for m = 0:M-1
        for n = 0:N-1

            kx = k0 .* sin(THETA) .* cos(PHI);
            ky = k0 .* sin(THETA) .* sin(PHI);
            kz = k0 .* cos(THETA);

            rx = dx * m;
            ry = dy * n;
            rz = 0;

            kdotr = kx*rx + ky*ry + kz*rz;

            AF = AF + exp(1j*kdotr);

        end
    end

    AF_mag = abs(AF);
    AF_norm = AF_mag ./ max(AF_mag(:));

end

%% =========================================================================

function AF_norm = array_factor_single_phi(phi, dy, dx, PHI, THETA, N, M)

    global k0

    if nargin < 7
        M = 1;
    end

    AF = zeros(size(THETA));

    for m = 0:M-1
        for n = 0:N-1

            kx = k0 .* sin(THETA) .* cos(PHI);
            ky = k0 .* sin(THETA) .* sin(PHI);
            kz = k0 .* cos(THETA);

            rx = dx * m;
            ry = dy * n;
            rz = 0;

            kdotr = kx*rx + ky*ry + kz*rz;

            AF = AF + exp(1j*kdotr);

        end
    end

    AF_mag = abs(AF);
    AF_norm = AF_mag ./ max(AF_mag(:));

    AF_norm = AF_norm(1,:);

end

%% =========================================================================
% Returns normalized patch antenna radiation pattern
% =========================================================================

function pattern_norm = patch_antenna(L, W, THETA, PHI)

    global lambda

    vx = (L/lambda) .* sin(THETA) .* cos(PHI);
    vy = (W/lambda) .* sin(THETA) .* sin(PHI);

    f = cos(vx*pi) .* sinc(vy);

    pattern = (cos(THETA).^2 .* sin(PHI).^2 + cos(PHI).^2) ...
                .* abs(f).^2;

    pattern_norm = pattern ./ max(pattern(:));

end

%% =========================================================================

function bw = get_beamwidth(pattern, theta)

    power = pattern.^2;

    ind_above_halfpower = find(power > 0.5);

    if isempty(ind_above_halfpower)
        fprintf('NO GROUPS FOUND, BEAMWIDTH IMPOSSIBLE\n');
        bw = 360;
        return;
    end

    splits = find(diff(ind_above_halfpower) ~= 1) + 1;
    groups = mat2cell(ind_above_halfpower, ...
                      1, ...
                      diff([0 splits length(ind_above_halfpower)]));

    middlebeam = groups{floor(length(groups)/2) + 1};

    if length(middlebeam) <= 1
        fprintf('NO MIDDLEBEAM FOUND, BEAMWIDTH IMPOSSIBLE\n');
        bw = 360;
        return;
    end

    bw = theta(middlebeam(end)) - theta(middlebeam(1));
    bw = rad2deg(bw);

end

%% =========================================================================

function max_sidelobe = calc_sidelobelevel(pattern)

    [pks, ~] = findpeaks(pattern);

    [~, idx] = max(pks);

    pks(idx) = [];

    max_sidelobe = max(pks);

end

%% =========================================================================

function [figHandle, axHandle] = plot_2d_cuts(pat_zerophi, pat_90phi, theta)

    pat_zerophi_dB = 20*log10(pat_zerophi);
    pat_90phi_dB  = 20*log10(pat_90phi);

    figHandle = figure;
    axHandle = axes;

    plot(rad2deg(theta), pat_zerophi_dB, ...
        'DisplayName', '\phi = 0^\circ');
    hold on;

    plot(rad2deg(theta), pat_90phi_dB, ...
        'DisplayName', '\phi = 90^\circ');

    ylim([-70 5]);

    xlabel('\theta (deg)');
    ylabel('normalized AF (dB)');

    legend;
    grid on;

end




%% =========================================================================
% A
% =========================================================================

N = 8;
att = 45;

% Dolph-Chebyshev taper coefficients
taper_coef = chebwin(N, att);

fprintf('Amplitude weights:\n');
disp(taper_coef);

phi   = linspace(-pi, pi, LOW_RES);
theta = linspace(0, pi, LOW_RES);

[THETA, PHI] = meshgrid(theta, phi);

AF_norm = array_factor_taper(dy, 0, PHI, THETA, taper_coef, N);

plot_pattern3D(AF_norm, THETA, PHI, '8x1 array');

%% 2D PLOTS

theta = linspace(-pi/2, pi/2, HIGH_RES);
phi = [0 pi/2];

[THETA, PHI] = meshgrid(theta, phi);

AF = array_factor_taper(dy, 0, PHI, THETA, taper_coef, N);

AF_zerophi = AF(1,:);
AF_90phi   = AF(2,:);

[fig, ax] = plot_2d_cuts(AF_zerophi, AF_90phi, theta);

AF_zerophi_dB = 20*log10(AF_zerophi);
AF_90phi_dB   = 20*log10(AF_90phi);

max_sidelobe = calc_sidelobelevel(AF_90phi_dB);

fprintf('The maximum sidelobe level is %.4f dB\n', max_sidelobe);

title(ax, 'Array Factor (8x1 tapered)');

beamwidth90   = get_beamwidth(AF_90phi, theta);
beamwidthzero = get_beamwidth(AF_zerophi, theta);

fprintf('8 in a line\n');
fprintf('The beamwidth in the phi=90 plane is %.4f deg\n', beamwidth90);
fprintf('The beamwidth in the phi=0 plane is %.4f deg\n', beamwidthzero);

D = 4*pi*(180/pi)^2 / (beamwidthzero*beamwidth90);

fprintf('The directivity is %.3f, which is %.4f dB\n', ...
    D, 20*log10(D));

%% =========================================================================
% B
% =========================================================================

dx = dy;

N = 8;
M = 8;
att = 45;

% Dolph-Chebyshev taper coefficients
taper_coef_N = chebwin(N, att);
taper_coef_M = chebwin(M, att);

[a, b] = meshgrid(taper_coef_N, taper_coef_M);

taper_coef = a .* b;

fprintf('Amplitude weights:\n');
disp(taper_coef);

phi   = linspace(0, pi, LOW_RES);
theta = linspace(-pi, pi, LOW_RES);

[THETA, PHI] = meshgrid(theta, phi);

AF_norm = array_factor_taper(dy, dx, PHI, THETA, taper_coef, N, M);

plot_pattern3D(AF_norm, THETA, PHI, '8x8 array');

%% 2D PLOTS

theta = linspace(-pi/2, pi/2, HIGH_RES);
phi = [0 pi/2];

[THETA, PHI] = meshgrid(theta, phi);

AF = array_factor_taper(dy, dx, PHI, THETA, taper_coef, N, M);

AF_zerophi = AF(1,:);
AF_90phi   = AF(2,:);

[fig, ax] = plot_2d_cuts(AF_zerophi, AF_90phi, theta);

AF_zerophi_dB = 20*log10(AF_zerophi);
AF_90phi_dB   = 20*log10(AF_90phi);

max_sidelobe = calc_sidelobelevel(AF_90phi_dB);

fprintf('The maximum sidelobe level is %.4f dB\n', max_sidelobe);

title(ax, 'Array Factor (8x8 tapered)');

beamwidth90   = get_beamwidth(AF_90phi, theta);
beamwidthzero = get_beamwidth(AF_zerophi, theta);

fprintf('8x8 array\n');
fprintf('The beamwidth in the phi=90 plane is %.4f deg\n', beamwidth90);
fprintf('The beamwidth in the phi=0 plane is %.4f deg\n', beamwidthzero);

D = 4*pi*(180/pi)^2 / (beamwidthzero*beamwidth90);

fprintf('The directivity is %.3f, which is %.4f dB\n', ...
    D, 20*log10(D));

%% =========================================================================
% FUNCTIONS
% =========================================================================

function AF_norm = array_factor_taper(dy, dx, PHI, THETA, taper, N, M)

    global k0

    if nargin < 7
        M = 1;
    end

    AF = zeros(size(THETA));

    for m = 0:M-1
        for n = 0:N-1

            kx = k0 .* sin(THETA) .* cos(PHI);
            ky = k0 .* sin(THETA) .* sin(PHI);
            kz = k0 .* cos(THETA);

            rx = dx * m;
            ry = dy * n;
            rz = 0;

            kdotr = kx*rx + ky*ry + kz*rz;

            % Weighting
            if M == 1
                weight = taper(n+1);
            else
                weight = taper(n+1, m+1);
            end

            AF = AF + weight .* exp(1j*kdotr);

        end
    end

    AF_mag = abs(AF);

    AF_norm = AF_mag ./ max(AF_mag(:));

end

%% =========================================================================

