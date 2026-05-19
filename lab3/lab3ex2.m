clear; clc; close all;

global c f lambda k0 dy LOW_RES HIGH_RES

c = 3e8;
f = 15e9;
lambda = c/f;
k0 = 2*pi/lambda;

dy = lambda/2;

LOW_RES = 2000;
HIGH_RES = 10000;

%% MAIN
lab3_ex2a();
%lab3_ex2b();
lab3_ex2c();
lab3_ex2d();

%% =========================================================================
%  FUNCTIONS
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

    a=colorbar;
    a.Label.String = 'Normalized gain (dB)';

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

function lab3_ex2a()

    global dy LOW_RES HIGH_RES

    fprintf('A\n');

    theta = linspace(0, pi, LOW_RES);
    phi   = linspace(-pi, pi, LOW_RES);

    [THETA, PHI] = meshgrid(theta, phi);

    % 3D plot
    AF_norm = array_factor(dy, 0, PHI, THETA, 8);

    plot_pattern3D(AF_norm, THETA, PHI, 'Array factor (8x1)');

    % 2D cuts
    theta = linspace(-pi/2, pi/2, HIGH_RES);
    phi = [0 pi/2];

    [THETA, PHI] = meshgrid(theta, phi);

    AF_norm = array_factor(dy, 0, PHI, THETA, 8);

    AF_zerophi = AF_norm(1,:);
    AF_90phi   = AF_norm(2,:);

    AF_90phi_dB = 20*log10(AF_90phi);

    % Parameters
    max_sidelobe = calc_sidelobelevel(AF_90phi_dB);

    fprintf('The maximum sidelobe level is %.4f dB\n', max_sidelobe);

    beamwidth90   = get_beamwidth(AF_90phi, theta);
    beamwidthzero = get_beamwidth(AF_zerophi, theta);

    fprintf('The beamwidth in the phi=90 plane is %.4f deg\n', beamwidth90);
    fprintf('The beamwidth in the phi=0 plane is %.4f deg\n', beamwidthzero);

    D = 4*pi*(180/pi)^2 / (beamwidthzero*beamwidth90);

    fprintf('The directivity is %.3f, which is %.4f dB\n', ...
        D, 20*log10(D));

    [~, ax] = plot_2d_cuts(AF_zerophi, AF_90phi, theta);

    title(ax, 'Array Factor (8x1)');

end

%% =========================================================================

function lab3_ex2b()

    global LOW_RES HIGH_RES

    fprintf('----------\n');
    fprintf('B\n');

    L = 5e-3;
    W = 6.5e-3;

    theta = linspace(0, pi/2, LOW_RES);
    phi   = linspace(-pi, pi, LOW_RES);

    [THETA, PHI] = meshgrid(theta, phi);

    pattern_norm = patch_antenna(L, W, THETA, PHI);

    plot_pattern3D(pattern_norm, THETA, PHI, ...
        'Patch antenna radiation pattern');

    % 2D cuts
    phi = [0 pi/2];
    theta = linspace(-pi/2, pi/2, HIGH_RES);

    [THETA, PHI] = meshgrid(theta, phi);

    pattern = patch_antenna(L, W, THETA, PHI);

    pattern_zerophi = pattern(1,:);
    pattern_90phi   = pattern(2,:);

    [~, ax] = plot_2d_cuts(pattern_zerophi, pattern_90phi, theta);

    ylabel(ax, 'normalized gain (dB)');
    title(ax, 'Patch antenna radiation pattern');

    bwzero = get_beamwidth(pattern_zerophi, theta);
    bw90   = get_beamwidth(pattern_90phi, theta);

    D = 4*pi*(180/pi)^2 / (bwzero*bw90);

    fprintf('Patch antenna\n');
    fprintf('Beamwidth phi=90: %.4f deg\n', bw90);
    fprintf('Beamwidth phi=0 : %.4f deg\n', bwzero);
    fprintf('Directivity = %.3f (%.4f dB)\n', ...
        D, 20*log10(D));

end

%% =========================================================================

function lab3_ex2c()

    global dy LOW_RES HIGH_RES

    fprintf('----------\n');
    fprintf('C\n');

    L = 5e-3;
    W = 6.5e-3;
    N = 8;

    theta = linspace(-pi/2, pi/2, LOW_RES);
    phi   = linspace(-pi, pi, LOW_RES);

    [THETA, PHI] = meshgrid(theta, phi);

    element_pattern_norm = patch_antenna(L, W, THETA, PHI);

    AF_norm = array_factor(dy, 0, PHI, THETA, N);

    total_norm = element_pattern_norm .* AF_norm;

    plot_pattern3D(total_norm, THETA, PHI, ...
        'Total Radiation Pattern');

    % 2D cuts
    theta = linspace(-pi/2, pi/2, HIGH_RES);
    phi = [0 pi/2];

    [THETA, PHI] = meshgrid(theta, phi);

    ef = patch_antenna(L, W, THETA, PHI);

    ef_zerophi = ef(1,:);
    ef_90phi   = ef(2,:);

    [~, ax] = plot_2d_cuts(ef_zerophi, ef_90phi, theta);

    ylabel(ax, 'normalized gain (dB)');

    af = array_factor(dy, 0, PHI, THETA, N);

    af_zerophi = af(1,:);
    af_90phi   = af(2,:);

    [~, ax] = plot_2d_cuts(af_zerophi, af_90phi, theta);

    ylabel(ax, 'normalized AF (dB)');

    total_zerophi = ef_zerophi .* af_zerophi;
    total_90phi   = ef_90phi .* af_90phi;

    bwzero = get_beamwidth(total_zerophi, theta);
    bw90   = get_beamwidth(total_90phi, theta);

    D = 4*pi*(180/pi)^2 / (bwzero*bw90);

    fprintf('Total pattern\n');
    fprintf('Beamwidth phi=90: %.4f deg\n', bw90);
    fprintf('Beamwidth phi=0 : %.4f deg\n', bwzero);
    fprintf('Directivity = %.3f (%.4f dB)\n', ...
        D, 20*log10(D));

end

%% =========================================================================

function lab3_ex2d()

    global dy LOW_RES HIGH_RES

    fprintf('----------\n');
    fprintf('D\n');

    N = 8;
    M = 8;

    L = 5e-3;
    W = 6.5e-3;

    dx = dy;

    phi   = linspace(-pi, pi, LOW_RES);
    theta = linspace(-pi/2, pi/2, LOW_RES);

    [THETA, PHI] = meshgrid(theta, phi);

    element_pattern_norm = patch_antenna(L, W, THETA, PHI);

    AF_norm = array_factor(dy, dx, PHI, THETA, N, M);

    total_pattern = AF_norm .* element_pattern_norm;

    plot_pattern3D(AF_norm, THETA, PHI, 'Array factor (8x8)');

    plot_pattern3D(total_pattern, THETA, PHI, ...
        'Antenna factor (8x8)');

    % Directivity calculations
    phi = [0 pi/2];
    theta = linspace(-pi/2, pi/2, HIGH_RES);

    [THETA, PHI] = meshgrid(theta, phi);

    AF_norm = array_factor(dy, dx, PHI, THETA, N, M);

    AF_zerophi = AF_norm(1,:);
    AF_90phi   = AF_norm(2,:);

    element_pattern_norm = patch_antenna(L, W, THETA, PHI);

    pattern_zerophi = element_pattern_norm(1,:);
    pattern_90phi   = element_pattern_norm(2,:);

    total_zerophi = AF_zerophi .* pattern_zerophi;
    total_90phi   = AF_90phi .* pattern_90phi;

    beamwidth90   = get_beamwidth(total_90phi, theta);
    beamwidthzero = get_beamwidth(total_zerophi, theta);

    fprintf('----------\n');
    fprintf('8x8 matrix\n');

    fprintf('Beamwidth phi=90: %.4f deg\n', beamwidth90);
    fprintf('Beamwidth phi=0 : %.4f deg\n', beamwidthzero);

    D = 4*pi*(180/pi)^2 / (beamwidthzero*beamwidth90);

    fprintf('Directivity = %.3f (%.4f dB)\n', ...
        D, 20*log10(D));

end