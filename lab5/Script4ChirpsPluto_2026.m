clc; clear; %close all;

%%
%%%%%%%%%%%%%%%%%%%% Python Environment configuration %%%%%%%%%%%%%%%%%%%%%
terminate(pyenv); % Terminate any active Python sessions
pe = pyenv; % Initialize Python environment
if pe.Status == "NotLoaded"
    disp("----- Python Environment Configuration -----");
    pyenv(ExecutionMode="OutOfProcess", Version="3.12");
end

%%
%%%%%%%%%%%%%%%%%%%% Pluto's parameters configuration %%%%%%%%%%%%%%%%%%%%%
% Program sample_rate, tx_lo, rx_lo, tx_gain and rx_gain as follows:


Pluto_IP = '192.168.2.1';
PlutoSamprate = 40e6; % Sampling frequency (Hz): Pluto can sample up to
% 61 MHz but due to the USB 2.0 interface you have
% to choose values lower or equal to 5MHz if you
% want to receive 100% of samples over time.
Tx_CenterFrequency = 2.5e9; % Pluto TX operating frequency (Hz) must be
% between 70MHz and 6GHz
Rx_CenterFrequency = 2.5e9; % Pluto TX operating frequency (Hz) must be
% between 70MHz and 6GHz
tx_gain = -10; % Pluto TX channel Gain must be between 0 and -88 with a
% resolution of 0.25 dB
rx_gain = 0; % Pluto RX channel Gain must be between -3 and 70 with a
% resolution of 0.25 dB


%% Radar Waveform Parameters

B = 5e6;       % Chirp bandwidth (Hz)
T = 100e-6;       % Chirp duration (s)
f0 = 2.5e9;      % Carrier frequency of the RF signal (Hz)
fs = PlutoSamprate;     % Sampling rate of all the signals in this simulation (Hz) 
c = 3e8;        % Speed of light (m/s)

%% Time Vectors definition

t = 0:1/fs:(T-1/fs);  % Time vector for one chirp
N = length(t); % Number of time samples in one chirp
rx_time_ms = 1000*length(t)/PlutoSamprate; 
sdr_object = py.setupPlutoSDR_TDD.initialize_Pluto_TDD(Pluto_IP, PlutoSamprate, f0, rx_gain, tx_gain, rx_time_ms);

% NOTE: SDR and TDD objects; these object must be passed to the Python module 
% that will be used to transmit and receive data.
my_sdr = sdr_object{1};
tddn = sdr_object{2};

%% Signal Generator - Chirp generation (Base Band)

k = B / T;     % Chirp slope defined as ratio of bandwidth over duration
sig_A = exp(1j*2*pi*(0.5*k*t.^2));

t_start = tic;
save_path = fileparts(mfilename("fullpath"));
rx_SamplePerFrame = fs;


tx_waveform = ((2^14)).*sig_A;
frame_length_samples = floor(rx_time_ms*PlutoSamprate/1000);
% Setup SDR
my_sdr = py.setupPlutoSDR.initialize_Pluto(Pluto_IP, int32(length(tx_waveform)), int32(PlutoSamprate), Tx_CenterFrequency, Rx_CenterFrequency, int32(rx_gain), int32(tx_gain),int32(rx_SamplePerFrame));

capture_range = 100;

% Send and receive data with Pluto
results = py.TDD_Transreceiver.pluto_transmit_receive(my_sdr, tddn, tx_waveform, int32(capture_range), int32(frame_length_samples),save_path);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Beginning of the data processing to load data onto MATLAB workspace
% Load the received data into the current Matlab workspace
received_data=load([save_path,'\received_data.mat']);
received_data=received_data.received_data;
t_stop = toc(t_start);
disp(['Data received - Elapsed Time: ', num2str(t_stop),'s']);





