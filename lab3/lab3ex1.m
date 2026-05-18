clear; clc; close all;

C = 2.99e8;
resonant_freq = 15e9;
substrate_thickness = 0.5e-3;
epsilon_r = 3.66;

test_frequencies = [14e9, 15e9, 16e9];

% Patch dimensions are designed for 15 GHz
[l, w] = find_L_W(resonant_freq, epsilon_r, substrate_thickness);

phi = linspace(0, 2*pi, 300);
theta = linspace(0, 0.5*pi, 300);

figure;
tiledlayout(1, 3);

for k = 1:length(test_frequencies)

    freq = test_frequencies(k);

    g_theta_phi = gain_func(l, w, freq, phi, theta);

    nexttile;
    plot_gain_subplot(phi, theta, g_theta_phi);

    title(sprintf('Gain at %.0f GHz', freq/1e9));

end


function [l, w] = find_L_W(fr, er, h)

    C = 2.99e8;

    w = C / (2 * fr * sqrt((er + 1) / 2));

    epsilon_eff = (er + 1) / 2 + ...
        (er - 1) / (2 * sqrt(1 + 12 * h / w));

    L_eff = C / (2 * fr * sqrt(epsilon_eff));

    disp(epsilon_eff);
    disp(L_eff);

    delta_L = (0.412 * h * (epsilon_eff + 0.3) * (w/h + 0.264)) / ...
              ((epsilon_eff - 0.258) * (w/h + 0.8));

    l = L_eff - 2 * delta_L;

    fprintf("Found W and L are: W = %.6f mm, L = %.6f mm\n", ...
        w * 1000, l * 1000);

end


function g = gain_func(l, w, freq, phi, theta)

    C = 2.99e8;
    lambda0 = C / freq;

    g = zeros(length(theta), length(phi));

    for i = 1:length(theta)
        for j = 1:length(phi)

            v_y = (w / lambda0) * sin(theta(i)) * sin(phi(j));

            if v_y == 0
                v_y = 1e-10;
            end

            v_x = (l / lambda0) * sin(theta(i)) * cos(phi(j));

            F_theta_phi = cos(pi * v_x) * sin(pi * v_y) / (pi * v_y);

            g_theta_phi = ((cos(theta(i)) * sin(phi(j)))^2 + ...
                           cos(phi(j))^2) * F_theta_phi^2;

            g(i,j) = g_theta_phi;

        end
    end

end


function plot_gain_subplot(phi, theta, gain_values)

    c_sens = 15;

    len_t = length(theta);
    len_p = length(phi);

    X = zeros(len_t, len_p);
    Y = zeros(len_t, len_p);
    Z = zeros(len_t, len_p);

    for i = 1:len_t
        for j = 1:len_p
            X(i,j) = gain_values(i,j) * sin(theta(i)) * cos(phi(j));
            Y(i,j) = gain_values(i,j) * sin(theta(i)) * sin(phi(j));
            Z(i,j) = gain_values(i,j) * cos(theta(i));
        end
    end

    gain_dB = 10 * log10(gain_values);
    gain_dB = max(min(gain_dB, 0), -c_sens);

    surf(X, Y, Z, gain_dB, 'EdgeColor', 'none');

    colormap jet;
    a = colorbar;
    a.Label.String='Normalized gain (dB)';
    caxis([-c_sens 0]);

    xlabel('X');
    ylabel('Y');
    zlabel('Z');

    axis equal;
    grid on;
    view(3);

end