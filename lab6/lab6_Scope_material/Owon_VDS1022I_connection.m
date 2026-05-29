%% Connect to OWON VDS1022 via TCP (OWON PC software must be running)
host = '127.0.0.1';
port = 5188;

scope = tcpclient(host, port, 'Timeout', 20);
%% Send IDN query
writeline(scope, '*IDN?');
pause(0.2);
response = readline(scope);
     disp(response);

%Example commands                       
writeline(scope, '*AUT');
