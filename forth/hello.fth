variable hello_string 13 allocate \ объявляем переменную, куда запишем строку

: set_hello \ заполняет переменную "Hello, World!" [72 101 108 108 111 44 32 87 111 114 108 100 33]
hello_string
72 over ! \ H
101 over 1 + ! \ e
108 over 1 + ! \ l
108 over 1 + ! \ l
111 over 1 + ! \ o
44 over 1 + ! \ ,
32 over 1 + ! \ 
87 over 1 + ! \ W
111 over 1 + ! \ o
114 over 1 + ! \ r
108 over 1 + ! \ l
100 over 1 + ! \ d
33 over 1 + ! \ !
;

: print_var \ <address> <size>
dup 0 = if
swap 1 +
dup @ 11 emit
swap 1 -
print_var
then
;

set_hello
13 
print_var

