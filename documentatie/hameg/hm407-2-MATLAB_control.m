function hm407
% funcion para obtener los datos de un osciloscopio digital
% function to get the data displayed by a digital oscilloscope
%
% HAMEG ANALOG DIGITAL SCOPE HM407
%
% ver si se ha ejecutado ya la funcion
hameg = findobj('Tag','HM407');
if (isempty(hameg)),
    % crear la nueva figura
    hameg = figure;
    set(hameg,'numbertitle','off');
    set(hameg,'name','HAMEG HM407');
    set(hameg,'MenuBar','none');
    set(hameg,'doublebuffer','on');
    set(hameg,'Tag','HM407');
    % #########################################################################
    %		M	E	N	U
    % #########################################################################
    Hm_se  = uimenu('Label','&Read');
    Hm_ch1  = uimenu(Hm_se,'Label','&Read CH1','Callback',@ch1);
    Hm_ch2  = uimenu(Hm_se,'Label','&Read CH2','Callback',@ch2);
    Hm_save = uimenu(Hm_se,'Label','&Save data as...','enable','off','Callback',@savedata,'separator','on','tag','save');
    Hm_load = uimenu(Hm_se,'Label','&Load data...','Callback',@loaddata,'separator','on');
    Hm_cf  = uimenu('Label','&Configuration');
    Hm_cfs  = uimenu(Hm_cf,'Label','&serial PORT');
    Hm_com1 = uimenu(Hm_cfs,'Label','&COM1','Callback',@changeserial,'tag','COM1','userdata','serial');
    Hm_com2 = uimenu(Hm_cfs,'Label','&COM2','Checked','on','Callback',@changeserial,'tag','COM2','userdata','serial');
    
    Hm_an  = uimenu('Label','&Analyze','enable','off','tag','an');
    Hm_rp  = uimenu(Hm_an,'Label','&Plot data','Callback',@replot);
    Hm_fil = uimenu(Hm_an,'Label','&Filter data','Callback',@datfilt);
    Hm_mm  = uimenu(Hm_an,'Label','&Max / Min','Callback',@maxmin);
    
    hm407.port = 'COM2';
    
    set(hameg,'userdata',hm407);
else,
    figure(hameg);
end,
% ###################################################################################
% ###################################################################################
function ch1(hco,eventStruct)
% funcion para leer el canal 1
hameg = findobj('Tag','HM407');
hm407 = get(hameg,'userdata');
set(hameg,'Pointer','watch');
s2 = serial(hm407.port);
set(s2,'Terminator','');
set(s2,'StopBits', 2);
set(s2,'FlowControl','hardware');
set(s2,'Timeout',1);
set(s2,'InputBufferSize', 2100);
fopen(s2);
% iniciar comunicacion con el osciloscopio
missatge = [' ' char(13)];
fwrite(s2, missatge);
warning off;
idn = fread(s2,3,'uchar');
% obtener la version del osciloscopio
fprintf(s2, 'VERS?');
idn = fread(s2,20,'uchar');
% verificar que VERS este en la respuesta
if (isempty(findstr(char(idn)','VERS'))),
    % no hay comunicacion
    fclose(s2);
    
    set(hameg,'Pointer','arrow');
    
    errordlg(['HM407 is not on' hm407.port],'Error...','modal');
    warning on;
end,
% averiguar la configuracion del osciloscopio
missatge = ['DDF?' char(13) char(10)];
fwrite(s2, missatge);
info = fread(s2);
info_ch1 = info(5);
info_ch2 = info(6);
vermode  = info(7);
info_tba = info(8);
info_tbb = info(9);
hormode  = info(10);
info_trig = info(11);
strmode = info(12);
voltdiv = bitand(info_ch1,15);
switch (voltdiv),
    case 0,
        escala = 0.001; % 1mV/DIV
    case 1,
        escala = 0.002; % 2mV/DIV
    case 2,
        escala = 0.005; % 5mV/DIV
    case 3,
        escala = 0.010; % 10mV/DIV
    case 4,
        escala = 0.020; % 20mV/DIV
    case 5,
        escala = 0.050; % 50mV/DIV
    case 6,
        escala = 0.100; % 100mV/DIV
    case 7,
        escala = 0.200; % 200mV/DIV
    case 8,
        escala = 0.500; % 500mV/DIV
    case 9,
        escala = 1.000; % 1V/DIV
    case 10,
        escala = 2.000; % 2V/DIV
    case 11,
        escala = 5.000; % 5V/DIV
    case 12,
        escala = 10.000; % 10V/DIV
    case 13,
        escala = 20.00; % 20V/DIV
end,
timediv = bitand(info_tba,31);
switch (timediv),
    case 0,
        tiempo = 50e-9; % 50ns/DIV
    case 1,
        tiempo = 100e-9; % 100ns/DIV
    case 2,
        tiempo = 200e-9; % 200ns/DIV
    case 3,
        tiempo = 500e-9; % 500ns/DIV
    case 4,
        tiempo = 1e-6; % 1us/DIV
    case 5,
        tiempo = 2e-6; % 2us/DIV
    case 6,
        tiempo = 5e-6; % 5us/DIV
    case 7,
        tiempo = 10e-6; % 10us/DIV
    case 8,
        tiempo = 20e-6; % 20us/DIV
    case 9,
        tiempo = 50e-6; % 50us/DIV
    case 10,
        tiempo = 100e-6; % 100us/DIV
    case 11,
        tiempo = 200e-6; % 200us/DIV
    case 12,
        tiempo = 500e-6; % 500us/DIV
    case 13,
        tiempo = 1e-3; % 1ms/DIV
    case 14,
        tiempo = 2e-3; % 2ms/DIV
    case 15,
        tiempo = 5e-3; % 5ms/DIV
    case 16,
        tiempo = 10e-3; % 10ms/DIV
    case 17,
        tiempo = 20e-3; % 20ms/DIV
    case 18,
        tiempo = 50e-3; % 50ms/DIV
    case 19,
        tiempo = 100e-3; % 100ms/DIV
    case 20,
        tiempo = 200e-3; % 200ms/DIV
    case 21,
        tiempo = 500e-3; % 500ms/DIV
    case 22,
        tiempo = 1; % 1s/DIV
    case 23,
        tiempo = 2; % 2s/DIV
    case 24,
        tiempo = 5; % 5s/DIV
    case 25,
        tiempo = 10; % 10s/DIV
    case 26,
        tiempo = 20; % 20s/DIV
    case 27,
        tiempo = 50; % 50s/DIV
    case 28,
        tiempo = 100; % 100s/DIV
end,
% averiguar el waveform preamble
missatge = ['WFMPRE?' char(13) char(10)];
fwrite(s2, missatge);
info = fread(s2,7,'uchar');
info = fread(s2,5,'int16');
x_res = info(2);        % resolucion en la direccion X por division
y_res = info(3);        % resolucion en la direccion Y por division
y1_pos = info(4);       % Y1 pos standarized
% pedir datos del canal 1
missatge = ['RDWFM1:' char(0) char(0) char(0) char(8) char(13) char(10)];
fwrite(s2, missatge);
set(s2,'Timeout',5);
data = fread(s2,2059,'uchar');
dades = data(12:end);
set(s2,'Timeout',1);
missatge = ['RM0' char(13) char(10)];
fwrite(s2, missatge);
final = fread(s2);
warning on;
fclose(s2);
% escalado de los datos
hm407.tiempo = tiempo*[0:1:2047]/x_res;
hm407.datos = escala*(dades-128-y1_pos)/y_res;
% guardar los nuevos datos
set(hameg,'userdata',hm407);
% dibujar nuevos datos
plot(hm407.tiempo,hm407.datos);
c=axis;
axis([hm407.tiempo(1) hm407.tiempo(end) c(3) c(4)]);
ylabel('amplitude (V)');
xlabel('time (s)');
title([num2str(escala) ' V/DIV : ' num2str(tiempo) ' S/DIV']);
set(hameg,'Pointer','arrow');
set(findobj('tag','save'),'enable','on');
set(findobj('tag','an'),'enable','on');
% ###################################################################################
% ###################################################################################
function ch2(hco,eventStruct)
% funcion para leer el canal 2
hameg = findobj('Tag','HM407');
hm407 = get(hameg,'userdata');
set(hameg,'Pointer','watch');
s2 = serial(hm407.port);
set(s2,'Terminator','');
set(s2,'StopBits', 2);
set(s2,'FlowControl','hardware');
set(s2,'Timeout',1);
set(s2,'InputBufferSize', 2100);
fopen(s2);
% iniciar comunicacion con el osciloscopio
missatge = [' ' char(13)];
fwrite(s2, missatge);
warning off;
idn = fread(s2,3,'uchar');
% obtener la version del osciloscopio
fprintf(s2, 'VERS?');
warning off;
idn = fread(s2,20,'uchar');
% verificar que VERS este en la respuesta
if (isempty(findstr(char(idn)','VERS'))),
    % no hay comunicacion
    fclose(s2);
    
    set(hameg,'Pointer','arrow');
    
    errordlg(['HM407 is not on' hm407.port],'Error...','modal');
    warning on;
end,
% averiguar la configuracion del osciloscopio
missatge = ['DDF?' char(13) char(10)];
fwrite(s2, missatge);
info = fread(s2);
info_ch1 = info(5);
info_ch2 = info(6);
vermode  = info(7);
info_tba = info(8);
info_tbb = info(9);
hormode  = info(10);
info_trig = info(11);
strmode = info(12);
voltdiv = bitand(info_ch2,15);
switch (voltdiv),
    case 0,
        escala = 0.001; % 1mV/DIV
    case 1,
        escala = 0.002; % 2mV/DIV
    case 2,
        escala = 0.005; % 5mV/DIV
    case 3,
        escala = 0.010; % 10mV/DIV
    case 4,
        escala = 0.020; % 20mV/DIV
    case 5,
        escala = 0.050; % 50mV/DIV
    case 6,
        escala = 0.100; % 100mV/DIV
    case 7,
        escala = 0.200; % 200mV/DIV
    case 8,
        escala = 0.500; % 500mV/DIV
    case 9,
        escala = 1.000; % 1V/DIV
    case 10,
        escala = 2.000; % 2V/DIV
    case 11,
        escala = 5.000; % 5V/DIV
    case 12,
        escala = 10.000; % 10V/DIV
    case 13,
        escala = 20.00; % 20V/DIV
end,
timediv = bitand(info_tba,31);
switch (timediv),
    case 0,
        tiempo = 50e-9; % 50ns/DIV
    case 1,
        tiempo = 100e-9; % 100ns/DIV
    case 2,
        tiempo = 200e-9; % 200ns/DIV
    case 3,
        tiempo = 500e-9; % 500ns/DIV
    case 4,
        tiempo = 1e-6; % 1us/DIV
    case 5,
        tiempo = 2e-6; % 2us/DIV
    case 6,
        tiempo = 5e-6; % 5us/DIV
    case 7,
        tiempo = 10e-6; % 10us/DIV
    case 8,
        tiempo = 20e-6; % 20us/DIV
    case 9,
        tiempo = 50e-6; % 50us/DIV
    case 10,
        tiempo = 100e-6; % 100us/DIV
    case 11,
        tiempo = 200e-6; % 200us/DIV
    case 12,
        tiempo = 500e-6; % 500us/DIV
    case 13,
        tiempo = 1e-3; % 1ms/DIV
    case 14,
        tiempo = 2e-3; % 2ms/DIV
    case 15,
        tiempo = 5e-3; % 5ms/DIV
    case 16,
        tiempo = 10e-3; % 10ms/DIV
    case 17,
        tiempo = 20e-3; % 20ms/DIV
    case 18,
        tiempo = 50e-3; % 50ms/DIV
    case 19,
        tiempo = 100e-3; % 100ms/DIV
    case 20,
        tiempo = 200e-3; % 200ms/DIV
    case 21,
        tiempo = 500e-3; % 500ms/DIV
    case 22,
        tiempo = 1; % 1s/DIV
    case 23,
        tiempo = 2; % 2s/DIV
    case 24,
        tiempo = 5; % 5s/DIV
    case 25,
        tiempo = 10; % 10s/DIV
    case 26,
        tiempo = 20; % 20s/DIV
    case 27,
        tiempo = 50; % 50s/DIV
    case 28,
        tiempo = 100; % 100s/DIV
end,
% averiguar el waveform preamble
missatge = ['WFMPRE?' char(13) char(10)];
fwrite(s2, missatge);
info = fread(s2,7,'uchar');
info = fread(s2,5,'int16');
x_res = info(2);
y_res = info(3);
y2_pos = info(5);
% pedir datos del canal 2
missatge = ['RDWFM2:' char(0) char(0) char(0) char(8) char(13) char(10)];
fwrite(s2, missatge);
set(s2,'Timeout',5);
data = fread(s2,2059,'uchar');
dades = data(12:end);
set(s2,'Timeout',1);
missatge = ['RM0' char(13) char(10)];
fwrite(s2, missatge);
final = fread(s2);
warning on;
fclose(s2);
% escalado de los datos
hm407.tiempo = tiempo*[0:1:2047]/x_res;
hm407.datos = escala*(dades-128-y2_pos)/y_res;
% guardar los nuevos datos
set(hameg,'userdata',hm407);
% dibujar nuevos datos
plot(hm407.tiempo,hm407.datos);
c=axis;
axis([hm407.tiempo(1) hm407.tiempo(end) c(3) c(4)]);
ylabel('amplitude (V)');
xlabel('time (s)');
title([num2str(escala) ' V/DIV : ' num2str(tiempo) ' S/DIV']);
set(hameg,'Pointer','arrow');
set(findobj('tag','save'),'enable','on');
set(findobj('tag','an'),'enable','on');
% ###################################################################################
% ###################################################################################
function changeserial(hco,eventStruct)
% funcion para modificar el puerto de comunicaciones
hameg = findobj('Tag','HM407');
hm407 = get(hameg,'userdata');
set(findobj('userdata','serial'),'checked','off');
set(hco,'checked','on');
hm407.port = get(hco,'tag');
% guardar los nuevos datos
set(hameg,'userdata',hm407);
% ###################################################################################
% ###################################################################################
function savedata(hco,eventStruct)
% funcion para guardar los datos
[filename, pathname] = uiputfile('*.mat', 'Save data as...');
if (ischar(filename)),
    hameg = findobj('Tag','HM407');
    hm407 = get(hameg,'userdata');
    
    if (isempty(findstr(lower(filename),'.mat'))),
        save([lower(pathname) lower(filename) '.mat'],'hm407');
    else,
        save([lower(pathname) lower(filename)],'hm407');
    end,
    
    set(hameg,'name',['HAMEG HM407: ' lower(filename)]);
end,
% ###################################################################################
% ###################################################################################
function loaddata(hco,eventStruct)
% funcion para recuperar los datos
[filename, pathname] = uigetfile('*.mat', 'Load data...');
if (ischar(filename)),
    hameg = findobj('Tag','HM407');
    hm407 = get(hameg,'userdata');
    
    port = hm407.port;
    % recuperar variable
    a = load([lower(pathname) lower(filename)],'-mat');
    hm407 = a.hm407;
    
    hm407.port = port;
    % dibujar nuevos datos
    plot(hm407.tiempo,hm407.datos,'r-');
    c=axis;
    axis([hm407.tiempo(1) hm407.tiempo(end) c(3) c(4)]);
    ylabel('amplitude (V)');
    xlabel('time (s)');
    title(['']);
    % guardar los nuevos datos
    set(hameg,'userdata',hm407);
    set(hameg,'name',['HAMEG HM407: ' lower(filename)]);
    
    set(findobj('tag','an'),'enable','on');
    
end,
% ###################################################################################
% ###################################################################################
function replot(hco,eventStruct)
% funcion para redibujar los datos
hameg = findobj('Tag','HM407');
hm407 = get(hameg,'userdata');
    
% dibujar los datos
plot(hm407.tiempo,hm407.datos,'r-');
c=axis;
axis([hm407.tiempo(1) hm407.tiempo(end) c(3) c(4)]);
ylabel('amplitude (V)');
xlabel('time (s)');
title(['']);
% ###################################################################################
% ###################################################################################
function datfilt(hco,eventStruct)
% funcion para filtrar los datos
hameg = findobj('Tag','HM407');
hm407 = get(hameg,'userdata');
    
% dibujar los datos originales
plot(hm407.tiempo,hm407.datos,'r-');
% filtrar
hm407.datos = filtfilt([1 1 1 1 1 1 1 1 1 1]/10,1,hm407.datos);
% guardar los nuevos datos
set(hameg,'userdata',hm407);
hold on;
plot(hm407.tiempo,hm407.datos,'k-');
hold off;
c=axis;
axis([hm407.tiempo(1) hm407.tiempo(end) c(3) c(4)]);
ylabel('amplitude (V)');
xlabel('time (s)');
title(['']);
% ###################################################################################
% ###################################################################################
function maxmin(hco,eventStruct)
% funcion para analizar los datos
hameg = findobj('Tag','HM407');
hm407 = get(hameg,'userdata');
a_max = max(hm407.datos);
a_min = min(hm407.datos);
i_max = find(hm407.datos == a_max);
i_min = find(hm407.datos == a_min);
% dibujar nuevos datos
plot(hm407.tiempo,hm407.datos,'r-');
hold on;
plot(hm407.tiempo(i_max(1)), a_max,'go');
plot(hm407.tiempo(i_min(1)), a_min,'go');
plot([hm407.tiempo(1) hm407.tiempo(end)], [a_max a_max],'b:');
plot([hm407.tiempo(1) hm407.tiempo(end)], [a_min a_min],'b:');
hold off;
c=axis;
axis([hm407.tiempo(1) hm407.tiempo(end) c(3) c(4)]);
ylabel('amplitude (V)');
xlabel('time (s)');
title(['max = ' num2str(a_max) ', min = ' num2str(a_min)]);
% ###################################################################################