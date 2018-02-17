# Log analyzer

Для проверки работоспособности кода, 
корректности результатов выполнения кода, необходимо выполнить следующие команды в терминале: 
    
 - скрипт с основным функционалом задания можно запустить с указанием конфиг файла, 
   тогда указанные в конфиг файле параметры обновят параметры конфига заданнаого по умолчанию,
   а так же запустить без указания конфиг файла, тогда скрипт будет использовать параметры 
   конфига заданные поулчанию:
    - ``python2.7 log_analyzer.py --config <путь к конфиг файлу>`` 
    - ``python2.7 log_analyzer.py``
 
 - запуск скрипта с тестами основного функционала задания:
   - ``python2.7 log_analyzer_tests.py -v``
