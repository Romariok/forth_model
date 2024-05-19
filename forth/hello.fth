variable hello_string 13 allocate \ объявляем переменную, куда запишем строку

: set_hello_world \ заполняет переменную "Hello, World!" [72 101 108 108 111 44 32 87 111 114 108 100 33]
hello_string 1 +
dup 72 ! \ H
1 + dup 101 ! \ e
1 + dup 108 ! \ l
1 + dup 108 ! \ l
1 + dup 111 ! \ o
1 + dup 44 ! \ ,
1 + dup 32 ! \ 
1 + dup 87 ! \ W
1 + dup 111 ! \ o
1 + dup 114 ! \ r
1 + dup 108 ! \ l
1 + dup 100 ! \ d
1 + dup 33 ! \ !
;

: print_var \ <address> <size>
dup 0 = if \ Проверка на конец строки
swap 1 + dup \ <size> <address+1> <address+1>
@ 11 emit \ <size> <address+1>
swap 1 - \ <address+1> <size-1> 
print_var
then
;

set_hello_world
hello_string hello_string @
print_var