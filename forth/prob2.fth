variable result 
variable current 
variable next
variable temp

: next_fib
drop
temp @ 4000000 > \ Проверка на число 
if 
temp current @ next @ + ! \ Следующее число
current next @ !

temp @ 2 mod 0 > \ Если число четное, то складываем
if 
result dup @ temp @ + !
then

next temp @ !
1
else
0 \ Кладём 0, чтобы выйти из цикла
then
;

result 0 !
current 0 !
next 1 !
1
begin \ цикл, который генерирует числа
next_fib
until

result @ 11 emit  \ вывод результата