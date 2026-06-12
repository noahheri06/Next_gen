% PLUTO_TX_TRIGGER_STUDENT  -  FMCW transmit + oscilloscope trigger
%
% The Pluto transmits the chirp continuously and emits a short pulse on the L10P
% pin at the start of every sweep. Trigger the oscilloscope on that pulse.
%
% You only have to write the chirp 'sw' (see the CHIRP section). Everything else
% (packing it for the Pluto, transmitting) is already done.

clear; clc;

%% ===  PARAMETERS  =========================================================
PYTHON   = "";            % "" = current pyenv, else "3.11" or a python.exe path
PLUTO_IP = '192.168.2.1';
Fs       = 60.5e6;        % sample rate [Hz]
Fc       = 2.5e9;         % RF carrier frequency [Hz]
tx_gain  = -10;           % transmit power [dB]  (0 = maximum)
pulse_us = 10;            % scope-trigger pulse width [us]

%% ===  CHIRP  -  write this  ===============================================
% An FMCW radar transmits a tone whose frequency rises linearly in time. A target
% reflects it back delayed, so mixing the echo with the chirp gives a constant
% "beat" frequency proportional to the target distance. Build that chirp here.
%
% --- Your Chosen Parameters ---
fstart  = -10e6;                 % sweep start frequency [Hz] (e.g., -10 MHz)
fstop   =  10e6;                 % sweep stop frequency [Hz]  (e.g., +10 MHz)
T_chirp = 1e-3;                  % sweep duration [s] (e.g., 1 ms)

% --- Time Vector ---
% The sample instants, spaced by 1/Fs. 
% Fs is already defined in the parameters section above.
t = 0 : 1/Fs : T_chirp - 1/Fs;   

% --- Complex Chirp Generation ---
% The chirp rate (slope) K is the change in frequency over time
K = (fstop - fstart) / T_chirp;  

% The complex signal is generated using the instantaneous phase.
% Phase is the integral of the instantaneous frequency over time.
sw = exp(1j * 2 * pi * (fstart * t + (K / 2) * t.^2));



%% ===  PLUTO PACKING  (provided - do not change)  =========================
% Your chirp 'sw' is converted to the Pluto's I/Q sample format here.
% 4096 = 2^12, the Pluto's 12-bit DAC full scale: a chirp of amplitude 1 maps
% to +/-4096. The I and Q are interleaved [I0 Q0 I1 Q1 ...] as the Pluto wants.
sw       = sw(:);                                 % ensure a column
t        = (0:numel(sw)-1).'/Fs;                  % time vector
tx       = int16(reshape([int16(real(sw)*4096), int16(imag(sw)*4096)].', [], 1));
frame_ms = numel(sw)/Fs*1e3 + 0.1;                % sweep length + 0.1 ms gap [ms]

% look at the chirp you built: waveform in time + instantaneous frequency
figure('Name','Transmitted chirp','Color','w');
subplot(2,1,1);
  plot(t*1e3, real(sw), 'LineWidth', 1); grid on;
  xlabel('time [ms]'); ylabel('amplitude'); title('chirp waveform (I)');
subplot(2,1,2);
  plot(t(1:end-1)*1e3, diff(unwrap(angle(sw)))/(2*pi)*Fs/1e6, 'LineWidth', 1.2); grid on;
  xlabel('time [ms]'); ylabel('frequency [MHz]'); title('instantaneous frequency (slope)');

%% ===  TRANSMIT  ===========================================================
% start MATLAB's Python (it drives the Pluto) and locate the backend
if strlength(PYTHON) > 0
    terminate(pyenv); pyenv(ExecutionMode="OutOfProcess", Version=PYTHON);
end
py.sys.path().insert(int32(0), fileparts(mfilename('fullpath')));

% chirp out + L10P trigger pulse on every sweep
h = py.pluto_tdd.start_tdd_stream(PLUTO_IP, int64(Fs), int64(Fc), ...
        double(tx_gain), tx, frame_ms, double(pulse_us));
fprintf('Transmitting. Wire L10P -> scope trigger (CH2). Press any key to stop...\n');
pause;
py.pluto_tdd.stop_tdd_stream(h);
