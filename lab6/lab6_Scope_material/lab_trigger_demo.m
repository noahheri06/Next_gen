% LAB_TRIGGER_DEMO  Generate a waveform + synchronized trigger via ADALM-Pluto
%
%  Two outputs on the Pluto:
%    RF TX   — chirp or sine wave, transmitted continuously
%    L10P    — hardware trigger pulse, synchronized to each waveform period
%              (< 10 ns jitter, same 100 MHz TDD counter)
%
%  Two launch modes — set USE_DOCKER below:
%
%    USE_DOCKER = true   (default)
%      Requires: Docker + image 'pluto-radarnext:latest'
%      Build once from project root:
%        docker build -t pluto-radarnext:latest -f docker/Dockerfile .
%
%    USE_DOCKER = false
%      Requires: Python with pyadi-iio installed, accessible via pyenv.
%      Set PYTHON_VERSION to match your installation, e.g. "3.12".

clear; clc;

% =========================================================================
%  LAUNCH MODE — comment/uncomment ONE block
% =========================================================================

% USE_DOCKER = true;
USE_DOCKER     = false;
PYTHON_VERSION = "3.12";   % Python version for pyenv (USE_DOCKER=false only)

% =========================================================================
%  PARAMETERS
% =========================================================================

PLUTO_IP = '192.168.2.1';
Fs       = 10e6;      % Sample rate (Hz)
Fc       = 2.4e9;     % Carrier frequency (Hz)
fstart   = 100e3;     % Chirp start frequency, baseband (Hz)
fstop    = 4e6;       % Chirp stop  frequency, baseband (Hz)
f_sine   = 1e6;       % Sine frequency (Hz) — used only if WAVEFORM='sine'
T_chirp  = 1e-3;      % Waveform period (s)
T_gap    = 0.1e-3;    % Silent gap after each period (s)
pulse_us = 50.0;      % L10P trigger pulse width (us), must be < T_gap * 1e6
amp      = 0.6;       % Amplitude, normalised 0-1
tx_gain  = -10;       % TX attenuation (dB), range 0 to -88

WAVEFORM = 'chirp';   % 'chirp'  or  'sine'

% Docker-specific
DOCKER_IMAGE  = 'pluto-radarnext:latest';
CONTAINER     = 'lab_trigger';
DATA_DIR_HOST = fullfile(tempdir, 'radarnext_lab');
DATA_DIR_CTR  = '/data';
MAT_FILE      = 'lab_trigger_params.mat';

% =========================================================================
%  WAVEFORM GENERATION
% =========================================================================

N = floor(T_chirp * Fs);
t = (0:N-1).' / Fs;

switch WAVEFORM
    case 'chirp'
        k  = (fstop - fstart) / T_chirp;
        iq = amp * exp(1j * 2*pi * (fstart*t + 0.5*k*t.^2));
    case 'sine'
        iq = amp * exp(1j * 2*pi * f_sine * t);
    otherwise
        error('WAVEFORM must be ''chirp'' or ''sine''');
end

% Scale to int16 interleaved [I0,Q0,I1,Q1,...] — Pluto 12-bit DAC range
SCALE = 4096;
I_int = int16(real(iq) * SCALE);
Q_int = int16(imag(iq) * SCALE);
tx_waveform = int16(reshape([I_int, Q_int].', [], 1));

frame_ms = (T_chirp + T_gap) * 1e3;   % T_PRI in ms

fprintf('Waveform : %s  |  %d samples  |  T = %.1f ms  |  T_PRI = %.2f ms\n', ...
    WAVEFORM, N, T_chirp*1e3, frame_ms);
fprintf('L10P     : pulse %.0f us, rising edge at period start\n\n', pulse_us);

% =========================================================================
%  PLOTS
% =========================================================================

figure(1); clf;

subplot(3,1,1);
plot(t*1e3, real(iq), 'b');
xlabel('Time (ms)'); ylabel('I');
title(['I component — ' upper(WAVEFORM)]);

subplot(3,1,2);
plot(t*1e3, abs(iq), 'k');
xlabel('Time (ms)'); ylabel('|s(t)|');
title('Envelope');
ylim([0 1.1]);

subplot(3,1,3);
f_inst = diff(unwrap(angle(iq))) / (2*pi) * Fs;
plot(t(1:end-1)*1e3, f_inst/1e6, 'r');
xlabel('Time (ms)'); ylabel('f_{inst} (MHz)');
title('Instantaneous frequency');

sgtitle(sprintf('%s  |  Fs = %.0f MHz  Fc = %.2f GHz  T = %.1f ms', ...
    upper(WAVEFORM), Fs/1e6, Fc/1e9, T_chirp*1e3));

% =========================================================================
%  START
% =========================================================================

if USE_DOCKER

    % ── Docker path ────────────────────────────────────────────────────────
    % Write parameter file — Docker reads it to configure Pluto + TDD engine
    if ~isfolder(DATA_DIR_HOST), mkdir(DATA_DIR_HOST); end
    mat_path = fullfile(DATA_DIR_HOST, MAT_FILE);

    params.pluto_ip    = PLUTO_IP;
    params.sample_rate = Fs;
    params.center_freq = Fc;
    params.tx_gain     = double(tx_gain);
    params.frame_ms    = frame_ms;
    params.pulse_us    = double(pulse_us);
    params.tx_waveform = tx_waveform;
    save(mat_path, '-struct', 'params');

    fprintf('Starting Docker container (%s)...\n', CONTAINER);

    % Stop any other pluto-radarnext container that may hold the Pluto
    [~, busy] = system('docker ps -q --filter ancestor=pluto-radarnext:latest');
    if ~isempty(strtrim(busy))
        fprintf('Stopping other pluto-radarnext containers...\n');
        system('docker stop $(docker ps -q --filter ancestor=pluto-radarnext:latest) 2>/dev/null; true');
        pause(1);
    end
    system(sprintf('docker rm -f %s 2>/dev/null; true', CONTAINER));

    %   --network host : container reaches Pluto at 192.168.2.1
    %   -v             : mounts the .mat parameter file into the container
    cmd = sprintf('docker run -d --rm --name %s --network host -v %s:%s %s ', ...
        CONTAINER, DATA_DIR_HOST, DATA_DIR_CTR, DOCKER_IMAGE);
    cmd = [cmd sprintf('python /app/run_tdd_trigger.py --in_mat %s/%s', ...
        DATA_DIR_CTR, MAT_FILE)];

    [status, out] = system(cmd);
    if status ~= 0
        error('Docker failed to start.\nBuild: docker build -t %s -f docker/Dockerfile .\n%s', ...
            DOCKER_IMAGE, out);
    end

    pause(3);
    [~, running] = system(sprintf('docker ps -q -f name=%s', CONTAINER));
    if isempty(strtrim(running))
        system(sprintf('docker logs %s 2>&1', CONTAINER));
        error('Docker container stopped unexpectedly. See logs above.');
    end
    fprintf('Container running  (%s)\n', CONTAINER);

else

    % ── Native Python via pyenv ────────────────────────────────────────────
    % Same pattern as setupPlutoSDR_TDD: terminate any existing session,
    % then call the Python functions directly — no subprocess, no .mat file.
    if ~exist('PYTHON_VERSION', 'var')
        error('Set PYTHON_VERSION (e.g. "3.12") before running with USE_DOCKER=false.');
    end

    terminate(pyenv);
    pyenv(ExecutionMode="OutOfProcess", Version=PYTHON_VERSION);

    % Add the folder containing this .m file to Python's module search path.
    % Put tdd_trigger_stream.py in the same folder as lab_trigger_demo.m.
    py.sys.path().insert(int32(0), fileparts(mfilename('fullpath')));

    fprintf('Connecting to Pluto and starting TDD engine...\n');
    tdd_handles = py.tdd_trigger_stream.start_tdd_stream( ...
        PLUTO_IP, ...
        int32(Fs), ...
        int32(Fc), ...
        double(tx_gain), ...
        tx_waveform, ...
        frame_ms, ...
        double(pulse_us));

end

fprintf('\nBoth channels active:\n');
fprintf('  RF TX  — %s  (Fc=%.2f GHz, T=%.1f ms)\n', WAVEFORM, Fc/1e9, T_chirp*1e3);
fprintf('  L10P   — trigger pulse %.0f us, rising edge at period start\n\n', pulse_us);
fprintf('Press any key to stop...\n');
pause;

% =========================================================================
%  STOP
% =========================================================================

if USE_DOCKER
    system(sprintf('docker stop %s 2>/dev/null; true', CONTAINER));
else
    py.tdd_trigger_stream.stop_tdd_stream(tdd_handles);
    terminate(pyenv);
end

fprintf('Done.\n');
